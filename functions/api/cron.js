// 日次バッチ（CRON_SECRET で保護）。GitHub Actions から1日1回叩く想定。
//  1) 定期請求の期日到来分を全ユーザー分生成（auto_send はオンラインリンクを宛先へメール）
//  2) 未入金リマインド: オプトイン(users.auto_remind)ユーザーの未払い請求書に、
//     期日3日前／期日当日／3日・7日・14日超過のタイミングでリンク付きメール（1日1回・最大5回）
import { json } from '../_lib.js';
import { ensureCols } from '../_schema.js';
import { sendMail, invoiceEmailHtml, invoiceEmailText } from '../_mail.js';
import { generateDueAllUsers } from './_recgen.js';

const REMIND_BEFORE = [3];            // 期日の何日前に送るか
const REMIND_OVERDUE = [0, 3, 7, 14]; // 期日超過の何日後に送るか
const REMIND_CAP = 5;                 // 1請求書あたりの最大送信回数
const SWEEP_LIMIT = 300;              // 1回のリマインド走査上限

function todayISO() { return new Date().toISOString().slice(0, 10); }
function daysBetween(fromISO, toISO) {
  const a = Date.parse(fromISO + 'T00:00:00Z'), b = Date.parse(toISO + 'T00:00:00Z');
  if (isNaN(a) || isNaN(b)) return null;
  return Math.round((b - a) / 86400000);
}
function authed(env, url, request) {
  const secret = env.CRON_SECRET;
  if (!secret) return false;
  const key = url.searchParams.get('key') || request.headers.get('x-cron-key') || '';
  if (key.length !== secret.length) return false;
  let diff = 0; for (let i = 0; i < key.length; i++) diff |= key.charCodeAt(i) ^ secret.charCodeAt(i);
  return diff === 0;
}

async function runReminders(env) {
  const today = todayISO();
  let rows = [];
  try {
    rows = (await env.DB.prepare(
      `SELECT d.id, d.doc_no, d.payable, d.paid_total, d.due_date, d.share_token, d.recipient_email, d.remind_count,
              c.name AS client_name, u.company_name AS sender_name, u.email AS sender_email
       FROM documents d
       JOIN users u ON u.id = d.user_id
       LEFT JOIN clients c ON c.id = d.client_id
       WHERE d.type='invoice' AND d.status IN ('pending','partial')
         AND u.auto_remind=1 AND d.recipient_email IS NOT NULL AND d.recipient_email<>''
         AND d.share_token IS NOT NULL AND d.due_date IS NOT NULL
         AND (d.last_reminder IS NULL OR d.last_reminder < ?)
         AND COALESCE(d.remind_count,0) < ?
       LIMIT ?`
    ).bind(today, REMIND_CAP, SWEEP_LIMIT).all()).results || [];
  } catch (e) { return { checked: 0, sent: 0 }; }

  let sent = 0;
  for (const d of rows) {
    try {
      const diff = daysBetween(today, d.due_date); // >0: 期日まであと diff 日 / <=0: 超過
      let due = false, overdue = false;
      if (diff > 0) { if (REMIND_BEFORE.indexOf(diff) >= 0) due = true; }
      else { overdue = true; if (REMIND_OVERDUE.indexOf(-diff) < 0) overdue = 'skip'; }
      if (!due && overdue !== true) continue;

      const remaining = Math.max(0, (d.payable || 0) - (d.paid_total || 0));
      const link = 'https://free-bizdocs.com/i/' + d.share_token;
      const opts = {
        lang: 'ja', kind: 'reminder', overdue: (overdue === true),
        senderName: d.sender_name || '', docNo: d.doc_no, amount: remaining, dueDate: d.due_date, link: link,
      };
      const r = await sendMail(env, {
        to: d.recipient_email, fromName: d.sender_name || 'Free BizDoc', replyTo: d.sender_email || '',
        subject: (overdue === true ? '【お支払い期限超過のお知らせ】' : '【お支払い期限のご確認】') + (d.doc_no ? ('請求書 ' + d.doc_no) : ''),
        html: invoiceEmailHtml(opts), text: invoiceEmailText(opts),
      });
      if (r && r.ok) {
        sent++;
        await env.DB.prepare('UPDATE documents SET last_reminder=?, remind_count=COALESCE(remind_count,0)+1 WHERE id=?').bind(today, d.id).run();
      }
    } catch (e) { /* 1件の失敗で止めない */ }
  }
  return { checked: rows.length, sent: sent };
}

async function handle(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  if (!authed(env, url, request)) return json({ ok: false, error: 'forbidden' }, 403);
  await ensureCols(env);
  let recurring = { users: 0, made: 0 }, reminders = { checked: 0, sent: 0 };
  try { recurring = await generateDueAllUsers(env); } catch (e) {}
  try { reminders = await runReminders(env); } catch (e) {}
  return json({ ok: true, date: todayISO(), recurring: recurring, reminders: reminders });
}

export async function onRequestGet(context) { return handle(context); }
export async function onRequestPost(context) { return handle(context); }

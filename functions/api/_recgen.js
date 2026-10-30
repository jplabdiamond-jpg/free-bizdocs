// 定期請求の共有ロジック: テーブル定義・日付計算・テンプレから請求書生成・期日到来分の自動生成。
import { calcTotals, randToken } from '../_lib.js';
import { ensureCols } from '../_schema.js';
import { sendMail, invoiceEmailHtml, invoiceEmailText } from '../_mail.js';

export const RECURRING_DDL =
  'CREATE TABLE IF NOT EXISTS recurring (' +
  'id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, client_id INTEGER, ' +
  "title TEXT DEFAULT '', items_json TEXT NOT NULL, bank TEXT DEFAULT '', notes TEXT DEFAULT '', " +
  "cycle TEXT NOT NULL DEFAULT 'monthly', day_of_month INTEGER NOT NULL DEFAULT 1, " +
  'due_days INTEGER NOT NULL DEFAULT 30, ' +
  "mode TEXT NOT NULL DEFAULT 'auto', next_run TEXT, active INTEGER NOT NULL DEFAULT 1, " +
  'last_run TEXT, created_at TEXT NOT NULL DEFAULT (datetime(\'now\')))';

export async function ensureTable(env) { try { await env.DB.prepare(RECURRING_DDL).run(); } catch (e) {} }

function pad4(n) { return ('000' + n).slice(-4); }
function todayISO() { return new Date().toISOString().slice(0, 10); }
function addMonths(cycle) { return ({ monthly: 1, bimonthly: 2, quarterly: 3, halfyear: 6, yearly: 12 })[cycle] || 1; }
function clampDay(y, m, dom) { const last = new Date(Date.UTC(y, m + 1, 0)).getUTCDate(); return (dom >= 99 || dom > last) ? last : Math.max(1, dom); }
function ymd(y, m, d) { return new Date(Date.UTC(y, m, d)).toISOString().slice(0, 10); }
export function addDays(iso, n) { const d = new Date(iso + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + (Number(n) || 0)); return d.toISOString().slice(0, 10); }

// fromISO の次の発生日（cycle ヶ月後の day_of_month）
export function advanceRun(fromISO, cycle, dom) {
  const d = new Date(fromISO + 'T00:00:00Z');
  let y = d.getUTCFullYear(), m = d.getUTCMonth() + addMonths(cycle);
  y += Math.floor(m / 12); m = ((m % 12) + 12) % 12;
  return ymd(y, m, clampDay(y, m, dom));
}
// 新規登録時の初回生成日: 今月の dom が未来ならそれ、過ぎていれば来月の dom
export function initialNextRun(dom) {
  const now = new Date(); const t = now.toISOString().slice(0, 10);
  let y = now.getUTCFullYear(), m = now.getUTCMonth();
  let cand = ymd(y, m, clampDay(y, m, dom));
  if (cand < t) { m += 1; if (m > 11) { m = 0; y += 1; } cand = ymd(y, m, clampDay(y, m, dom)); }
  return cand;
}

async function createInvoiceFromTemplate(env, uid, t, items) {
  const c = calcTotals(items);
  const today = todayISO();
  const due = (t.due_days != null) ? addDays(today, t.due_days) : null;
  const status = (t.mode === 'draft') ? 'draft' : 'pending';
  let docNo = null;
  if (status !== 'draft') {
    await env.DB.prepare('UPDATE users SET invoice_seq = invoice_seq + 1 WHERE id = ?').bind(uid).run();
    const uu = await env.DB.prepare('SELECT invoice_seq FROM users WHERE id = ?').bind(uid).first();
    docNo = 'INV-' + new Date().getFullYear() + '-' + pad4((uu && uu.invoice_seq) || 1);
  }
  // 宛先メール（取引先マスタ）と公開リンク用トークンをスナップショット。
  let clientEmail = '';
  try { const cl = await env.DB.prepare('SELECT email FROM clients WHERE id=?').bind(t.client_id || 0).first(); clientEmail = (cl && cl.email) || ''; } catch (e) {}
  const shareToken = (status !== 'draft') ? randToken() : null;
  const ins = await env.DB.prepare(
    'INSERT INTO documents (user_id, client_id, type, doc_no, status, issue_date, due_date, subtotal, tax, withholding, total, payable, bank, notes, recipient_email, share_token) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
  ).bind(uid, t.client_id || null, 'invoice', docNo, status, today, due,
    c.subtotal, c.tax, c.withholding, c.total, c.payable, t.bank || '', t.notes || '', clientEmail || null, shareToken).run();
  const docId = ins.meta.last_row_id;
  const stmts = items.map(function (it, i) {
    return env.DB.prepare('INSERT INTO line_items (document_id, name, qty, unit, unit_price, tax_rate, withholding, sort_order) VALUES (?,?,?,?,?,?,?,?)')
      .bind(docId, it.name || '', Number(it.qty) || 0, it.unit || '', Math.round(Number(it.unit_price) || 0), Number(it.tax_rate) || 0, Number(it.withholding) === 1 ? 1 : 0, i);
  });
  if (stmts.length) await env.DB.batch(stmts);
  return { id: docId, doc_no: docNo, share_token: shareToken, payable: c.payable, due_date: due, client_email: clientEmail };
}

// 生成した請求書のオンラインリンクを宛先へ自動メール（auto_send かつ宛先メールあり・自動発行のみ）。
async function autoSendLink(env, uid, t, created) {
  try {
    if (!(t.auto_send && t.mode !== 'draft' && created && created.share_token && created.client_email)) return;
    const u = await env.DB.prepare('SELECT company_name, email FROM users WHERE id=?').bind(uid).first() || {};
    const link = 'https://free-bizdocs.com/i/' + created.share_token;
    const opts = {
      lang: 'ja', kind: 'notice', senderName: u.company_name || '', docNo: created.doc_no,
      amount: created.payable, dueDate: created.due_date, link: link, message: t.notes || '',
    };
    await sendMail(env, {
      to: created.client_email, fromName: u.company_name || 'Free BizDoc', replyTo: u.email || '',
      subject: (u.company_name ? (u.company_name + ' より') : '') + '請求書のご案内' + (created.doc_no ? '（' + created.doc_no + '）' : ''),
      html: invoiceEmailHtml(opts), text: invoiceEmailText(opts),
    });
  } catch (e) { /* メール失敗でも生成は成功扱い */ }
}

// 期日到来分（next_run <= 今日）を1件ずつ生成し next_run を未来へ。生成件数を返す。
// auto_send 指定のテンプレは生成後にオンラインリンクを宛先へメール。
export async function generateDueForUser(env, uid) {
  try { await ensureTable(env); await ensureCols(env); } catch (e) { return 0; }
  const today = todayISO();
  let rows = [];
  try { rows = (await env.DB.prepare('SELECT * FROM recurring WHERE user_id=? AND active=1 AND next_run IS NOT NULL AND next_run<=?').bind(uid, today).all()).results || []; }
  catch (e) { return 0; }
  let made = 0;
  for (const t of rows) {
    try {
      const items = JSON.parse(t.items_json || '[]');
      if (!items.length) continue;
      const created = await createInvoiceFromTemplate(env, uid, t, items);
      await autoSendLink(env, uid, t, created);
      let nr = t.next_run, guard = 0;
      do { nr = advanceRun(nr, t.cycle, t.day_of_month); guard++; } while (nr <= today && guard < 60);
      await env.DB.prepare('UPDATE recurring SET next_run=?, last_run=? WHERE id=?').bind(nr, today, t.id).run();
      made++;
    } catch (e) { /* 1件の失敗で全体を止めない */ }
  }
  return made;
}

// cron 用: 全ユーザー横断で期日到来分を生成（auto_send はメール送付）。
export async function generateDueAllUsers(env) {
  try { await ensureTable(env); await ensureCols(env); } catch (e) { return { users: 0, made: 0 }; }
  const today = todayISO();
  let uids = [];
  try { uids = (await env.DB.prepare('SELECT DISTINCT user_id FROM recurring WHERE active=1 AND next_run IS NOT NULL AND next_run<=?').bind(today).all()).results || []; }
  catch (e) { return { users: 0, made: 0 }; }
  let made = 0;
  for (const r of uids) {
    try { made += await generateDueForUser(env, r.user_id); } catch (e) {}
  }
  return { users: uids.length, made: made };
}

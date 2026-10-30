// 認証ユーザーが、オンライン請求書リンクを取引先へメール送信する。
import { json, currentUserId, randToken, normalizeEmail } from '../../../_lib.js';
import { ensureCols } from '../../../_schema.js';
import { sendMail, invoiceEmailHtml, invoiceEmailText } from '../../../_mail.js';

function validEmail(e) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e); }

export async function onRequestPost(context) {
  const { env, params, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  const id = params.id;
  let b = {};
  try { b = await request.json(); } catch (e) {}

  const doc = await env.DB.prepare(
    `SELECT d.*, c.name AS client_name, c.email AS client_email
     FROM documents d LEFT JOIN clients c ON c.id = d.client_id
     WHERE d.id = ? AND d.user_id = ?`
  ).bind(id, uid).first();
  if (!doc) return json({ error: 'not found' }, 404);
  if (doc.type !== 'invoice' || doc.status === 'draft') return json({ error: 'この書類はオンライン送付の対象外です' }, 400);

  // トークン未発行なら発行
  let token = doc.share_token;
  if (!token) { token = randToken(); try { await env.DB.prepare('UPDATE documents SET share_token=? WHERE id=? AND user_id=?').bind(token, id, uid).run(); } catch (e) {} }

  const to = normalizeEmail(b.to || doc.recipient_email || doc.client_email || '');
  if (!validEmail(to)) return json({ error: '送付先メールアドレスを入力してください' }, 400);
  // 宛先を書類・取引先に保存
  try { await env.DB.prepare('UPDATE documents SET recipient_email=? WHERE id=? AND user_id=?').bind(to, id, uid).run(); } catch (e) {}
  if (doc.client_id) { try { await env.DB.prepare('UPDATE clients SET email=? WHERE id=? AND user_id=?').bind(to, doc.client_id, uid).run(); } catch (e) {} }

  const u = await env.DB.prepare('SELECT company_name, email FROM users WHERE id=?').bind(uid).first() || {};
  if (!env.RESEND_API_KEY) return json({ error: 'メール送信は現在利用できません' }, 500);

  const link = 'https://free-bizdocs.com/i/' + token;
  const opts = {
    lang: 'ja', kind: 'notice', senderName: u.company_name || '', docNo: doc.doc_no,
    amount: Math.max(0, (doc.payable || 0) - (doc.paid_total || 0)), dueDate: doc.due_date,
    link: link, message: (b.message || '').toString().slice(0, 2000),
  };
  const r = await sendMail(env, {
    to: to, fromName: u.company_name || 'Free BizDoc', replyTo: u.email || '',
    subject: (b.subject || ((u.company_name ? (u.company_name + ' より') : '') + '請求書のご案内' + (doc.doc_no ? '（' + doc.doc_no + '）' : ''))).toString().slice(0, 200),
    html: invoiceEmailHtml(opts), text: invoiceEmailText(opts),
  });
  if (!r.ok) return json({ ok: false, error: '送信に失敗しました。時間をおいてお試しください', detail: r.error }, 502);
  return json({ ok: true, to: to, link: link });
}

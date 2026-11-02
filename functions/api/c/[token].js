// 公開 取引先ポータルAPI（認証不要）。/api/c/<portal_token> → その取引先の全書類一覧。
import { json } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';

export async function onRequestGet(context) {
  const { env, params } = context;
  await ensureCols(env);
  const token = params.token;
  if (!token || token.length < 10) return json({ ok: false, error: 'not found' }, 404);
  const client = await env.DB.prepare('SELECT id, user_id, name, honorific FROM clients WHERE portal_token = ?').bind(token).first();
  if (!client) return json({ ok: false, error: 'not found' }, 404);

  const user = await env.DB.prepare('SELECT company_name, logo FROM users WHERE id = ?').bind(client.user_id).first() || {};
  const rows = (await env.DB.prepare(
    `SELECT type, doc_no, status, issue_date, due_date, total, payable, paid_total, share_token, viewed_at, accepted_at
     FROM documents
     WHERE client_id = ? AND user_id = ? AND status <> 'draft' AND share_token IS NOT NULL
       AND type IN ('invoice','quote')
     ORDER BY issue_date DESC, id DESC`
  ).bind(client.id, client.user_id).all()).results || [];

  const docs = rows.map(function (r) {
    return {
      type: r.type, doc_no: r.doc_no, status: r.status,
      issue_date: r.issue_date, due_date: r.due_date,
      amount: (r.type === 'quote') ? r.total : r.payable,
      paid_total: r.paid_total || 0,
      remaining: Math.max(0, (r.payable || 0) - (r.paid_total || 0)),
      link: 'https://free-bizdocs.com/i/' + r.share_token,
      accepted: !!r.accepted_at,
    };
  });
  return json({
    ok: true, client_name: client.name, honorific: client.honorific || '',
    sender_name: user.company_name || '', logo: user.logo || '', docs: docs,
  });
}

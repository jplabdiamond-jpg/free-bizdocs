import { json, currentUserId } from '../_lib.js';
import { generateDueForUser } from './_recgen.js';

function today() { return new Date().toISOString().slice(0, 10); }
function monthStart() { return new Date().toISOString().slice(0, 7) + '-01'; }

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);

  // 定期請求: 期日到来分をログイン時に自動生成（失敗してもダッシュボードは表示）
  try { await generateDueForUser(env, uid); } catch (e) {}
  const t = today();
  const m = monthStart();

  const month = await env.DB.prepare(
    "SELECT COALESCE(SUM(payable),0) AS amount, COUNT(*) AS cnt FROM documents WHERE user_id = ? AND type='invoice' AND status!='draft' AND issue_date >= ?"
  ).bind(uid, m).first();

  const unpaid = await env.DB.prepare(
    "SELECT COALESCE(SUM(payable - paid_total),0) AS amount, COUNT(*) AS cnt FROM documents WHERE user_id = ? AND type='invoice' AND status IN ('pending','partial')"
  ).bind(uid).first();

  const overdue = await env.DB.prepare(
    "SELECT COALESCE(SUM(payable - paid_total),0) AS amount, COUNT(*) AS cnt FROM documents WHERE user_id = ? AND type='invoice' AND status IN ('pending','partial') AND due_date < ?"
  ).bind(uid, t).first();

  const paid = await env.DB.prepare(
    `SELECT COALESCE(SUM(p.amount),0) AS amount
     FROM payments p JOIN documents d ON d.id = p.document_id
     WHERE d.user_id = ? AND p.paid_date >= ?`
  ).bind(uid, m).first();

  const recent = (await env.DB.prepare(
    `SELECT d.id, d.doc_no, d.status, d.issue_date, d.due_date, d.payable, c.name AS client_name
     FROM documents d LEFT JOIN clients c ON c.id = d.client_id
     WHERE d.user_id = ? AND d.type='invoice' ORDER BY d.id DESC LIMIT 6`
  ).bind(uid).all()).results || [];
  recent.forEach(function (r) {
    r.overdue = (r.status === 'pending' || r.status === 'partial') && r.due_date && r.due_date < t;
  });

  return json({
    month_amount: month.amount, month_count: month.cnt,
    unpaid_amount: unpaid.amount, unpaid_count: unpaid.cnt,
    overdue_amount: overdue.amount, overdue_count: overdue.cnt,
    paid_amount: paid.amount,
    recent: recent,
  });
}

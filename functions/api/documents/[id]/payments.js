import { json, currentUserId } from '../../../_lib.js';

const TOLERANCE = 550; // 振込手数料の誤差許容（円）

export async function onRequestPost(context) {
  const { env, params, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const id = params.id;
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const amount = Math.round(Number(b.amount) || 0);
  if (!amount) return json({ error: '入金額を入力してください' }, 400);

  const doc = await env.DB.prepare(
    'SELECT * FROM documents WHERE id = ? AND user_id = ?'
  ).bind(id, uid).first();
  if (!doc) return json({ error: 'not found' }, 404);

  await env.DB.prepare(
    'INSERT INTO payments (document_id, paid_date, amount, method, memo) VALUES (?, ?, ?, ?, ?)'
  ).bind(id, b.paid_date || new Date().toISOString().slice(0, 10), amount, b.method || '銀行振込', b.memo || '').run();

  const paidTotal = (doc.paid_total || 0) + amount;
  const remaining = (doc.payable || 0) - paidTotal;
  let status = doc.status;
  if (remaining <= TOLERANCE) status = 'paid';
  else if (paidTotal > 0) status = 'partial';

  await env.DB.prepare(
    'UPDATE documents SET paid_total = ?, status = ? WHERE id = ? AND user_id = ?'
  ).bind(paidTotal, status, id, uid).run();

  return json({ ok: true, paid_total: paidTotal, status: status, remaining: Math.max(0, remaining) });
}

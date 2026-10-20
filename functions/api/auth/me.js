import { json, currentUserId, FREE_DOC_LIMIT } from '../../_lib.js';

export async function onRequestGet(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ authed: false });
  const u = await env.DB.prepare('SELECT id, email, plan FROM users WHERE id = ?').bind(uid).first();
  if (!u) return json({ authed: false });

  // Stripe で支払い済みだが登録前だった場合の照合（webhook が stripe_pending に記録）。
  let plan = u.plan || 'free';
  if (plan !== 'pro' && u.email) {
    try {
      const pend = await env.DB.prepare('SELECT customer_id FROM stripe_pending WHERE email = ?').bind(u.email).first();
      if (pend) {
        await env.DB.prepare('UPDATE users SET plan = ?, stripe_customer_id = ? WHERE id = ?')
          .bind('pro', pend.customer_id || null, u.id).run();
        await env.DB.prepare('DELETE FROM stripe_pending WHERE email = ?').bind(u.email).run();
        plan = 'pro';
      }
    } catch (e) { /* stripe_pending 未作成環境でも落とさない */ }
  }
  const pro = (plan === 'pro');

  const docTypes = {};
  const r1 = (await env.DB.prepare('SELECT type, COUNT(*) AS n FROM documents WHERE user_id = ? GROUP BY type').bind(uid).all()).results || [];
  r1.forEach(function (r) { docTypes[r.type] = (docTypes[r.type] || 0) + r.n; });
  const r2 = (await env.DB.prepare('SELECT type, COUNT(*) AS n FROM saved_docs WHERE user_id = ? GROUP BY type').bind(uid).all()).results || [];
  r2.forEach(function (r) { docTypes[r.type] = (docTypes[r.type] || 0) + r.n; });

  let used = 0;
  Object.keys(docTypes).forEach(function (k) { used += docTypes[k]; });

  return json({
    authed: true, email: u.email, plan: plan,
    doc_count: used,
    limit: pro ? null : FREE_DOC_LIMIT,
    remaining: pro ? null : Math.max(0, FREE_DOC_LIMIT - used),
    doc_types: docTypes,
  });
}

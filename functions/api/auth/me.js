import { json, currentUserId, FREE_DOC_LIMIT } from '../../_lib.js';

export async function onRequestGet(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ authed: false });
  const u = await env.DB.prepare('SELECT id, email, plan FROM users WHERE id = ?').bind(uid).first();
  if (!u) return json({ authed: false });
  const pro = (u.plan === 'pro');

  const docTypes = {};
  const r1 = (await env.DB.prepare('SELECT type, COUNT(*) AS n FROM documents WHERE user_id = ? GROUP BY type').bind(uid).all()).results || [];
  r1.forEach(function (r) { docTypes[r.type] = (docTypes[r.type] || 0) + r.n; });
  const r2 = (await env.DB.prepare('SELECT type, COUNT(*) AS n FROM saved_docs WHERE user_id = ? GROUP BY type').bind(uid).all()).results || [];
  r2.forEach(function (r) { docTypes[r.type] = (docTypes[r.type] || 0) + r.n; });

  let used = 0;
  Object.keys(docTypes).forEach(function (k) { used += docTypes[k]; });

  return json({
    authed: true, email: u.email, plan: u.plan || 'free',
    doc_count: used,
    limit: pro ? null : FREE_DOC_LIMIT,
    remaining: pro ? null : Math.max(0, FREE_DOC_LIMIT - used),
    doc_types: docTypes,
  });
}

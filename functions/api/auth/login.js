import { json, verifyPassword, makeSession, sessionCookie, normalizeEmail } from '../../_lib.js';

export async function onRequestPost(context) {
  const { request, env } = context;
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const email = normalizeEmail(b.email);
  const pw = String(b.password || '');
  const u = await env.DB.prepare('SELECT id, password_hash, pw_salt, plan FROM users WHERE email = ?').bind(email).first();
  if (!u || !u.password_hash) return json({ error: 'メールアドレスまたはパスワードが違います' }, 401);
  const ok = await verifyPassword(pw, u.pw_salt, u.password_hash);
  if (!ok) return json({ error: 'メールアドレスまたはパスワードが違います' }, 401);
  const token = await makeSession(env.SESSION_SECRET, u.id);
  return new Response(JSON.stringify({ ok: true, email: email, plan: u.plan || 'free' }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'Set-Cookie': sessionCookie(token, 60 * 60 * 24 * 30),
    },
  });
}

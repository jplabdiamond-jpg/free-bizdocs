import { json, hashPassword, makeSession, sessionCookie, normalizeEmail, recordSignupAttrib } from '../../_lib.js';

export async function onRequestPost(context) {
  const { request, env } = context;
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const email = normalizeEmail(b.email);
  const pw = String(b.password || '');
  if (!email || email.indexOf('@') < 1 || email.indexOf('.') < 0) {
    return json({ error: '有効なメールアドレスを入力してください' }, 400);
  }
  if (pw.length < 8) return json({ error: 'パスワードは8文字以上にしてください' }, 400);

  const existing = await env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(email).first();
  if (existing) return json({ error: 'このメールアドレスは既に登録されています' }, 409);

  const { salt, hash } = await hashPassword(pw);
  const r = await env.DB.prepare(
    "INSERT INTO users (email, company_name, plan, password_hash, pw_salt, invoice_seq) VALUES (?, '', 'free', ?, ?, 0)"
  ).bind(email, hash, salt).run();
  const uid = r.meta.last_row_id;
  await recordSignupAttrib(env, request, uid); // 獲得ファネル: 流入元を記録
  const token = await makeSession(env.SESSION_SECRET, uid);
  return new Response(JSON.stringify({ ok: true, email: email, plan: 'free' }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'Set-Cookie': sessionCookie(token, 60 * 60 * 24 * 30),
    },
  });
}

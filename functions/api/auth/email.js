// メールアドレス変更（ログイン必須＋パスワード再確認）。重複チェックつき。
import { json, currentUserId, verifyPassword, normalizeEmail } from '../../_lib.js';

export async function onRequestPost(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'ログインが必要です', code: 'auth' }, 401);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const email = normalizeEmail(b.email);
  if (!email || email.indexOf('@') < 1 || email.indexOf('.') < 0) {
    return json({ error: '有効なメールアドレスを入力してください', code: 'bad_email' }, 400);
  }
  const u = await env.DB.prepare('SELECT email, password_hash, pw_salt FROM users WHERE id = ?').bind(uid).first();
  if (!u) return json({ error: 'ユーザーが見つかりません', code: 'auth' }, 401);
  if (email === normalizeEmail(u.email)) return json({ error: '現在と同じメールアドレスです', code: 'same' }, 400);
  if (u.password_hash) {
    const ok = await verifyPassword(String(b.password || ''), u.pw_salt, u.password_hash);
    if (!ok) return json({ error: 'パスワードが違います', code: 'wrong_password' }, 400);
  }
  const taken = await env.DB.prepare('SELECT id FROM users WHERE email = ? AND id <> ?').bind(email, uid).first();
  if (taken) return json({ error: 'このメールアドレスは既に使われています', code: 'taken' }, 409);
  await env.DB.prepare('UPDATE users SET email = ? WHERE id = ?').bind(email, uid).run();
  return json({ ok: true, email: email });
}

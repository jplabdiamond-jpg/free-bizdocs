// パスワード変更（ログイン必須）。Google専用アカウント（未設定）は「初回設定」として現在PW不要。
import { json, currentUserId, verifyPassword, hashPassword } from '../../_lib.js';

export async function onRequestPost(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'ログインが必要です', code: 'auth' }, 401);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const next = String(b.next || '');
  if (next.length < 8) return json({ error: '新しいパスワードは8文字以上にしてください', code: 'weak' }, 400);
  const u = await env.DB.prepare('SELECT password_hash, pw_salt FROM users WHERE id = ?').bind(uid).first();
  if (!u) return json({ error: 'ユーザーが見つかりません', code: 'auth' }, 401);
  if (u.password_hash) {
    const ok = await verifyPassword(String(b.current || ''), u.pw_salt, u.password_hash);
    if (!ok) return json({ error: '現在のパスワードが違います', code: 'wrong_current' }, 400);
  }
  const { salt, hash } = await hashPassword(next);
  await env.DB.prepare('UPDATE users SET password_hash = ?, pw_salt = ? WHERE id = ?').bind(hash, salt, uid).run();
  return json({ ok: true, had_password: !!u.password_hash });
}

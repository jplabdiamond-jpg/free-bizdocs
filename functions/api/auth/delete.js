// 退会（論理削除＋30日猶予）。deleted_at を記録しログアウト。
// 猶予期間中に再ログインすると復元（login/google側で deleted_at をクリア）。
// 期限超過分は cron が完全削除する。
import { json, currentUserId, verifyPassword } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';

export async function onRequestPost(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'ログインが必要です', code: 'auth' }, 401);
  await ensureCols(env); // deleted_at 列を保証
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const u = await env.DB.prepare('SELECT password_hash, pw_salt FROM users WHERE id = ?').bind(uid).first();
  if (!u) return json({ error: 'ユーザーが見つかりません', code: 'auth' }, 401);
  if (u.password_hash) {
    const ok = await verifyPassword(String(b.password || ''), u.pw_salt, u.password_hash);
    if (!ok) return json({ error: 'パスワードが違います', code: 'wrong_password' }, 400);
  }
  await env.DB.prepare("UPDATE users SET deleted_at = datetime('now') WHERE id = ? AND deleted_at IS NULL").bind(uid).run();
  return new Response(JSON.stringify({ ok: true, purge_days: 30 }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'Set-Cookie': 'sess=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0',
    },
  });
}

// PRO 事前登録（ウェイティングリスト）。メールを保存。認証不要。
import { json } from '../_lib.js';

export async function onRequestPost(context) {
  const { env, request } = context;
  let body = {};
  try { body = await request.json(); } catch (e) {}
  const email = String(body.email || '').trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || email.length > 200) {
    return json({ error: 'メールアドレスの形式が正しくありません' }, 400);
  }
  const note = String(body.note || '').slice(0, 300);
  try {
    await env.DB.prepare('INSERT OR IGNORE INTO waitlist (email, note, ts) VALUES (?, ?, ?)')
      .bind(email, note, Math.floor(Date.now() / 1000)).run();
  } catch (e) {
    return json({ error: '登録に失敗しました。時間をおいてお試しください。' }, 500);
  }
  return json({ ok: true });
}

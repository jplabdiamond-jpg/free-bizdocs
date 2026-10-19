// お問い合わせ受付。名前・メール・本文をD1に保存。認証不要。
import { json } from '../_lib.js';

export async function onRequestPost(context) {
  const { env, request } = context;
  let body = {};
  try { body = await request.json(); } catch (e) {}
  const name = String(body.name || '').trim().slice(0, 100);
  const email = String(body.email || '').trim();
  const text = String(body.body || '').trim().slice(0, 2000);
  if (!name) return json({ error: 'お名前を入力してください' }, 400);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || email.length > 200) {
    return json({ error: 'メールアドレスの形式が正しくありません' }, 400);
  }
  if (text.length < 5) return json({ error: 'お問い合わせ内容を入力してください' }, 400);
  try {
    await env.DB.prepare('INSERT INTO contacts (name, email, body, ts) VALUES (?, ?, ?, ?)')
      .bind(name, email, text, Math.floor(Date.now() / 1000)).run();
  } catch (e) {
    return json({ error: '送信に失敗しました。時間をおいてお試しください。' }, 500);
  }
  return json({ ok: true });
}

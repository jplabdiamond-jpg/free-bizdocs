// ご意見箱: 名前・種別・内容を受け付け（メール不要）。認証不要。
// 保存: D1 feedback テーブル（常時）。
// 通知: 環境変数 RESEND_API_KEY と FEEDBACK_TO が設定されていれば、その宛先へメール送信（任意・設定後に有効化）。
import { json } from '../_lib.js';

export async function onRequestPost(context) {
  const { env, request } = context;
  let body = {};
  try { body = await request.json(); } catch (e) {}
  const name = String(body.name || '').trim().slice(0, 100);
  const kind = (String(body.kind || '').trim().slice(0, 40)) || 'その他';
  const text = String(body.body || '').trim().slice(0, 2000);
  if (!name) return json({ error: 'お名前（ニックネーム可）を入力してください' }, 400);
  if (text.length < 3) return json({ error: '内容を入力してください' }, 400);

  const now = Math.floor(Date.now() / 1000);

  // 1) D1へ保存（常時・控え）
  let stored = false;
  try {
    await env.DB.prepare('INSERT INTO feedback (name, kind, body, ts) VALUES (?, ?, ?, ?)')
      .bind(name, kind, text, now).run();
    stored = true;
  } catch (e) { /* 保存失敗は後段で判定 */ }

  // 2) メール通知（RESEND_API_KEY と FEEDBACK_TO が設定されている場合のみ・ベストエフォート）
  if (env.RESEND_API_KEY && env.FEEDBACK_TO) {
    const esc = (s) => String(s || '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    const when = new Date(now * 1000).toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' });
    try {
      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { 'authorization': 'Bearer ' + env.RESEND_API_KEY, 'content-type': 'application/json' },
        body: JSON.stringify({
          from: env.FEEDBACK_FROM || 'Free BizDoc <feedback@free-bizdocs.com>',
          to: [env.FEEDBACK_TO],
          subject: '【Free BizDoc】フィードバック（' + kind + '）',
          text: '種別: ' + kind + '\nお名前: ' + name + '\n受付: ' + when + '\n\n' + text,
          html: '<p><b>種別:</b> ' + esc(kind) + '<br><b>お名前:</b> ' + esc(name) + '<br><b>受付:</b> ' + esc(when) + '</p><hr><p style="white-space:pre-wrap">' + esc(text) + '</p>'
        })
      });
    } catch (e) { /* メール失敗は送信成功扱い（控えはD1にある） */ }
  }

  if (!stored && !(env.RESEND_API_KEY && env.FEEDBACK_TO)) {
    return json({ error: '送信に失敗しました。時間をおいてお試しください。' }, 500);
  }
  return json({ ok: true });
}

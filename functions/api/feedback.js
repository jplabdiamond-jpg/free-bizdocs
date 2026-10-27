// ご意見箱: 名前・種別・内容を受け付け（メール不要）。認証不要。
// 保存: D1 feedback テーブル（常時）。
// 通知: 環境変数 RESEND_API_KEY と FEEDBACK_TO が設定されていれば、その宛先へメール送信（任意・設定後に有効化）。
import { json } from '../_lib.js';

// テーブル自動作成＋列の自動追加（Mac非依存・初回でも落とさない）。
// page=どのページから/lang=言語 を保存し、要望の文脈を残す。
const FEEDBACK_DDL = 'CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, kind TEXT, body TEXT, ts INTEGER, page TEXT, lang TEXT)';
let _migrated = false;
async function ensureTable(env) {
  if (_migrated) return;
  try { await env.DB.prepare(FEEDBACK_DDL).run(); } catch (e) {}
  // 既存テーブルに列が無い場合だけ追加（重複は無視）
  try { await env.DB.prepare('ALTER TABLE feedback ADD COLUMN page TEXT').run(); } catch (e) {}
  try { await env.DB.prepare('ALTER TABLE feedback ADD COLUMN lang TEXT').run(); } catch (e) {}
  _migrated = true;
}

export async function onRequestPost(context) {
  const { env, request } = context;
  let body = {};
  try { body = await request.json(); } catch (e) {}
  const lang = (String(body.lang || '').trim().toLowerCase() === 'en') ? 'en' : 'ja';
  // 名前は任意（摩擦を下げる）。未入力なら匿名扱い。
  const name = String(body.name || '').trim().slice(0, 100) || (lang === 'en' ? 'Anonymous' : '匿名');
  const kind = (String(body.kind || '').trim().slice(0, 40)) || (lang === 'en' ? 'Request' : '要望');
  const text = String(body.body || '').trim().slice(0, 2000);
  const page = String(body.page || '').trim().slice(0, 160);
  const minLen = (lang === 'en') ? 2 : 2;
  if (text.length < minLen) return json({ error: lang === 'en' ? 'Please enter your request.' : '内容を入力してください' }, 400);

  const now = Math.floor(Date.now() / 1000);

  // 1) D1へ保存（常時・控え）
  await ensureTable(env);
  let stored = false;
  try {
    await env.DB.prepare('INSERT INTO feedback (name, kind, body, ts, page, lang) VALUES (?, ?, ?, ?, ?, ?)')
      .bind(name, kind, text, now, page, lang).run();
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
          subject: '【Free BizDoc】' + (lang === 'en' ? 'Request/Feedback' : 'フィードバック') + '（' + kind + (page ? ' / ' + page : '') + '）',
          text: '種別: ' + kind + '\n言語: ' + lang + '\nページ: ' + (page || '-') + '\nお名前: ' + name + '\n受付: ' + when + '\n\n' + text,
          html: '<p><b>種別:</b> ' + esc(kind) + '<br><b>言語:</b> ' + esc(lang) + '<br><b>ページ:</b> ' + esc(page || '-') + '<br><b>お名前:</b> ' + esc(name) + '<br><b>受付:</b> ' + esc(when) + '</p><hr><p style="white-space:pre-wrap">' + esc(text) + '</p>'
        })
      });
    } catch (e) { /* メール失敗は送信成功扱い（控えはD1にある） */ }
  }

  if (!stored && !(env.RESEND_API_KEY && env.FEEDBACK_TO)) {
    return json({ error: '送信に失敗しました。時間をおいてお試しください。' }, 500);
  }
  return json({ ok: true });
}

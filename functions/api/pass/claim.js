// 都度払い（1日パス）の引き換え。Stripe の決済成功リダイレクト（?session_id=cs_...）から呼ぶ。
// webhook が day_pass に記録済みなら、24h 有効の署名 Cookie(fb_pass) を発行（アカウント不要）。
import { json, makePassToken, passCookie } from '../../_lib.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const url = new URL(request.url);
  const sid = (url.searchParams.get('session_id') || '').slice(0, 200);
  if (sid.indexOf('cs_') !== 0) return json({ ok: false, error: 'bad session' }, 400);

  try { await env.DB.prepare('CREATE TABLE IF NOT EXISTS day_pass (session_id TEXT PRIMARY KEY, ts INTEGER)').run(); } catch (e) {}
  let row = null;
  try { row = await env.DB.prepare('SELECT session_id FROM day_pass WHERE session_id = ?').bind(sid).first(); } catch (e) {}
  // まだ webhook が届いていない可能性 → pending を返してクライアントにリトライさせる
  if (!row) return json({ ok: false, pending: true });

  const token = await makePassToken(env.SESSION_SECRET, 86400000); // 24時間
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'Set-Cookie': passCookie(token, 86400),
    },
  });
}

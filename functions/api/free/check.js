// 無料ツールのレート制限（ネットワーク単位・直近1時間に2枚まで）。認証不要。
import { json } from '../../_lib.js';

const WINDOW = 3600;  // 秒
const LIMIT = 2;

// レート制限のキー。IPv6は /64 プレフィックスで束ねる。
// （家庭用IPv6はプライバシー拡張で末尾64bitが頻繁に変わり、/128のままだと
//   制限をすり抜けてしまうため。IPv4はそのまま使う。）
export function ipKey(request) {
  const raw = (request.headers.get('CF-Connecting-IP')
    || request.headers.get('X-Forwarded-For') || 'unknown').split(',')[0].trim();
  if (raw.indexOf(':') >= 0 && raw !== 'unknown') {
    // IPv6: 先頭4グループ（/64）だけを残す
    const head = raw.split('::')[0].split(':').filter(Boolean).slice(0, 4);
    if (head.length) return 'v6/' + head.join(':') + '::/64';
  }
  return 'v4/' + raw;
}

// 残回数の確認（消費しない）
export async function onRequestGet(context) {
  const { env, request } = context;
  const ip = ipKey(request);
  const since = Math.floor(Date.now() / 1000) - WINDOW;
  const row = await env.DB.prepare('SELECT COUNT(*) AS n FROM free_usage WHERE ip = ? AND ts > ?').bind(ip, since).first();
  const used = (row && row.n) || 0;
  return json({ remaining: Math.max(0, LIMIT - used), limit: LIMIT });
}

// 1枚消費（発行の直前に呼ぶ）
export async function onRequestPost(context) {
  const { env, request } = context;
  const ip = ipKey(request);
  const now = Math.floor(Date.now() / 1000);
  const since = now - WINDOW;
  const row = await env.DB.prepare('SELECT COUNT(*) AS n, MIN(ts) AS oldest FROM free_usage WHERE ip = ? AND ts > ?').bind(ip, since).first();
  const used = (row && row.n) || 0;
  if (used >= LIMIT) {
    const oldest = (row && row.oldest) || now;
    const retryMin = Math.max(1, Math.ceil((oldest + WINDOW - now) / 60));
    return json({ ok: false, remaining: 0, retry_min: retryMin, limit: LIMIT }, 429);
  }
  await env.DB.prepare('INSERT INTO free_usage (ip, ts) VALUES (?, ?)').bind(ip, now).run();
  // 古い行を掃除（ベストエフォート）
  try { await env.DB.prepare('DELETE FROM free_usage WHERE ts < ?').bind(since - WINDOW).run(); } catch (e) {}
  return json({ ok: true, remaining: Math.max(0, LIMIT - used - 1), limit: LIMIT });
}

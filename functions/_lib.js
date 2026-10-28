// 共通ライブラリ: レスポンス・認証(アカウント)・パスワード・税計算

export function json(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}

// ---- hex / bytes ----
function bytesToHex(buf) {
  const b = new Uint8Array(buf); let s = '';
  for (let i = 0; i < b.length; i++) s += b[i].toString(16).padStart(2, '0');
  return s;
}
function hexToBytes(hex) {
  const a = new Uint8Array((hex || '').length / 2);
  for (let i = 0; i < a.length; i++) a[i] = parseInt(hex.substr(i * 2, 2), 16);
  return a;
}
function b64url(buf) {
  return btoa(String.fromCharCode.apply(null, new Uint8Array(buf)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

// ---- 署名セッション（ユーザーIDを格納）----
async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(msg));
  return b64url(sig);
}
export async function makeSession(secret, uid) {
  const exp = Date.now() + 1000 * 60 * 60 * 24 * 30; // 30日
  const payload = String(uid) + '.' + exp;
  const sig = await hmac(secret, payload);
  return payload + '.' + sig;
}
// 有効なら user_id(Number)、無効なら null
export async function verifySession(secret, token) {
  if (!token) return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const payload = parts[0] + '.' + parts[1];
  const expected = await hmac(secret, payload);
  if (expected !== parts[2]) return null;
  const exp = parseInt(parts[1], 10);
  if (!exp || Date.now() >= exp) return null;
  const uid = parseInt(parts[0], 10);
  return uid || null;
}
export function getCookie(request, name) {
  const c = request.headers.get('Cookie') || '';
  const m = c.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}
export function sessionCookie(value, maxAge) {
  return 'sess=' + encodeURIComponent(value) + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=' + maxAge;
}

// 都度払い（1日パス）: 決済確認後に 24h 有効の署名トークンを発行。アカウント不要。
// token = "<expiryMs>.<hmac>"。無料枠リミッターがこれを見て解放する。
export async function makePassToken(secret, ms) {
  const exp = Date.now() + (ms || 86400000); // 既定24時間
  const sig = await hmac(secret, 'pass.' + exp);
  return exp + '.' + sig;
}
// 有効なら expiryMs(Number)、無効なら 0
export async function verifyPassToken(secret, token) {
  if (!token) return 0;
  const parts = token.split('.');
  if (parts.length !== 2) return 0;
  const exp = parseInt(parts[0], 10);
  if (!exp || Date.now() >= exp) return 0;
  const expected = await hmac(secret, 'pass.' + parts[0]);
  if (expected !== parts[1]) return 0;
  return exp;
}
export function passCookie(value, maxAge) {
  return 'fb_pass=' + encodeURIComponent(value) + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=' + maxAge;
}
// リクエストからログイン中 user_id を取得（未ログインは null）
export async function currentUserId(request, env) {
  return await verifySession(env.SESSION_SECRET, getCookie(request, 'sess'));
}

// 獲得ファネル: 登録時にファーストタッチ流入元(fb_ft Cookie)をD1へ保存。
// テーブルは自動作成（Mac非依存）。失敗しても登録本体は止めない。
export const ATTRIB_DDL = 'CREATE TABLE IF NOT EXISTS signup_attrib (user_id INTEGER PRIMARY KEY, source TEXT, medium TEXT, campaign TEXT, landing TEXT, ts TEXT)';
export async function recordSignupAttrib(env, request, uid) {
  try {
    if (!env || !env.DB || !uid) return;
    let o = {};
    try {
      const raw = getCookie(request, 'fb_ft');
      if (raw) {
        const s = raw.replace(/-/g, '+').replace(/_/g, '/');
        o = JSON.parse(decodeURIComponent(escape(atob(s))));
      }
    } catch (e) { o = {}; }
    const src = String(o.s || 'direct').slice(0, 80);
    const med = String(o.m || '').slice(0, 80);
    const camp = String(o.c || '').slice(0, 80);
    const land = String(o.l || '').slice(0, 120);
    await env.DB.batch([
      env.DB.prepare(ATTRIB_DDL),
      env.DB.prepare('INSERT OR IGNORE INTO signup_attrib (user_id, source, medium, campaign, landing, ts) VALUES (?,?,?,?,?,?)')
        .bind(uid, src, med, camp, land, new Date().toISOString()),
    ]);
  } catch (e) { /* 計測失敗は無視 */ }
}

// ---- パスワード（PBKDF2-SHA256）----
const PBKDF2_ITERS = 100000;
async function pbkdf2Hex(password, saltHex) {
  const keyMat = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt: hexToBytes(saltHex), iterations: PBKDF2_ITERS, hash: 'SHA-256' },
    keyMat, 256);
  return bytesToHex(bits);
}
export async function hashPassword(password) {
  const salt = bytesToHex(crypto.getRandomValues(new Uint8Array(16)));
  const hash = await pbkdf2Hex(password, salt);
  return { salt, hash };
}
export async function verifyPassword(password, saltHex, hashHex) {
  if (!saltHex || !hashHex) return false;
  const h = await pbkdf2Hex(password, saltHex);
  // 長さ一致＋定数時間ぽい比較
  if (h.length !== hashHex.length) return false;
  let diff = 0;
  for (let i = 0; i < h.length; i++) diff |= h.charCodeAt(i) ^ hashHex.charCodeAt(i);
  return diff === 0;
}
export function normalizeEmail(e) {
  return String(e || '').trim().toLowerCase();
}

// ---- 税計算エンジン（サーバー側が正）----
// items: [{ qty, unit_price, tax_rate(10|8|0), withholding(0|1) }]
export function calcTotals(items) {
  let sub10 = 0, sub8 = 0, sub0 = 0, whBase = 0, subtotal = 0;
  const lines = (items || []).map(function (it) {
    const qty = Number(it.qty) || 0;
    const price = Math.round(Number(it.unit_price) || 0);
    const amount = Math.round(qty * price);
    const rate = Number(it.tax_rate);
    if (rate === 10) sub10 += amount;
    else if (rate === 8) sub8 += amount;
    else sub0 += amount;
    if (Number(it.withholding) === 1) whBase += amount;
    subtotal += amount;
    return { amount: amount };
  });
  const tax10 = Math.floor(sub10 * 0.10);
  const tax8 = Math.floor(sub8 * 0.08);
  const tax = tax10 + tax8;
  let withholding = 0;
  if (whBase > 0) {
    withholding = whBase <= 1000000
      ? Math.floor(whBase * 0.1021)
      : Math.floor((whBase - 1000000) * 0.2042) + 102100;
  }
  const total = subtotal + tax;
  const payable = total - withholding;
  return { sub10, sub8, sub0, tax10, tax8, tax, subtotal, withholding, total, payable, lines };
}

// 無料プランの保存上限
export const FREE_DOC_LIMIT = 5;

import { verifySession, getCookie } from './_lib.js';

// 認証ゲート: アプリ各ページと保護APIを、ログイン中のみ許可。
export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  // www → apex 301
  if (url.hostname === 'www.free-bizdocs.com') {
    url.hostname = 'free-bizdocs.com';
    return Response.redirect(url.toString(), 301);
  }
  const p = url.pathname;

  // --- 紹介/流入計測（utm付きのページ遷移を第一者でD1に記録。応答はブロックしない）---
  try {
    if (request.method === 'GET' && url.searchParams.get('utm_source')
        && !p.startsWith('/api/')
        && !/\.(?:css|js|png|jpe?g|webp|svg|ico|woff2?|ttf|json|xml|txt|map)$/i.test(p)) {
      context.waitUntil(logReferral(env, url, request));
    }
  } catch (e) { /* 計測失敗は無視（本体に影響させない） */ }

  // --- 言語ルーティング（ブラウザ言語で日本語 / English を振り分け）---
  // 手動切替（?lang=ja|en）はCookieに記憶し、以後は自動判定より優先する。
  const qlang = url.searchParams.get('lang');
  if (qlang === 'ja' || qlang === 'en') {
    url.searchParams.delete('lang');
    const dest = url.origin + url.pathname + url.search + url.hash;
    return new Response(null, {
      status: 302,
      headers: {
        'Location': dest,
        'Set-Cookie': `site_lang=${qlang}; Path=/; Max-Age=31536000; SameSite=Lax`,
        'Cache-Control': 'no-store',
      },
    });
  }
  // トップ（apex ルート）のみ自動振り分け。各ツール/記事の直リンク・検索流入はそのまま。
  if (p === '/' && request.method === 'GET') {
    const choice = getCookie(request, 'site_lang');
    if (choice === 'en') {
      return new Response(null, { status: 302, headers: { 'Location': url.origin + '/en/', 'Cache-Control': 'no-store', 'Vary': 'Cookie' } });
    }
    if (!choice) {
      // Accept-Language の最優先タグが日本語でなければ英語版へ（ヘッダー無しのbot等は振り分けない）
      const al = request.headers.get('Accept-Language') || '';
      const primary = al.split(',')[0].trim().toLowerCase().split('-')[0];
      if (primary && primary !== 'ja') {
        return new Response(null, { status: 302, headers: { 'Location': url.origin + '/en/', 'Cache-Control': 'no-store', 'Vary': 'Accept-Language' } });
      }
    }
  }

  // 旧 .html URL を新クリーンURLへ 301
  const LEGACY = { '/free.html': '/invoice', '/ryoshusho.html': '/receipt', '/nouhinsho.html': '/delivery', '/mitsumorisho.html': '/quote', '/hacchusho.html': '/purchase-order' };
  if (LEGACY[p]) return Response.redirect(url.origin + LEGACY[p], 301);

  // 公開API（認証・無料ツール・問い合わせ等）
  const PUBLIC_API = ['/api/auth/signup', '/api/auth/login', '/api/auth/logout', '/api/auth/me', '/api/auth/google/start', '/api/auth/google/callback', '/api/waitlist', '/api/contact', '/api/feedback', '/api/stripe/webhook'];
  if (PUBLIC_API.indexOf(p) >= 0) return next();
  if (p.startsWith('/api/free/')) return next();

  // 保護対象のアプリページ（クリーンURL・.html 両方）
  const APP_PAGES = ['/dashboard', '/invoice-list', '/invoice-create', '/quotes', '/recurring', '/reports', '/payments', '/referrals', '/feedback-admin'];
  const pageKey = p.replace(/\.html$/, '');
  const isAppPage = APP_PAGES.indexOf(pageKey) >= 0;
  const isApi = p.startsWith('/api/');

  // 保護対象でなければ公開（トップ・ツール・ブログ・料金・法務など）
  if (!isAppPage && !isApi) {
    // 獲得ファネル: 初回のHTML閲覧でファーストタッチ流入元を記録（既にあれば触らない）
    if (request.method === 'GET' && !getCookie(request, 'fb_ft')
        && !/\.(?:css|js|png|jpe?g|webp|svg|ico|woff2?|ttf|json|xml|txt|map)$/i.test(p)) {
      const res = await next();
      try {
        const ct = res.headers.get('content-type') || '';
        if (ct.indexOf('text/html') >= 0) {
          const h = new Headers(res.headers);
          h.append('Set-Cookie', firstTouchCookie(url, request));
          return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
        }
      } catch (e) { /* 失敗しても本体は返す */ }
      return res;
    }
    return next();
  }

  // ここからは認証が必要
  const uid = await verifySession(env.SESSION_SECRET, getCookie(request, 'sess'));
  if (uid) return next();

  if (isApi) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), {
      status: 401, headers: { 'content-type': 'application/json' },
    });
  }
  // 未認証のアプリページ → ログインへ
  return Response.redirect(url.origin + '/login', 302);
}

// 紹介/流入の第一者ロガー（D1 referral_hits。テーブルは自動作成＝Mac非依存）
const REFERRAL_DDL = 'CREATE TABLE IF NOT EXISTS referral_hits (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, day TEXT, path TEXT, utm_source TEXT, utm_medium TEXT, utm_campaign TEXT, ref_host TEXT, country TEXT)';
async function logReferral(env, url, request) {
  try {
    if (!env || !env.DB) return;
    const g = (k) => (url.searchParams.get(k) || '').slice(0, 80);
    let refHost = '';
    try { const r = request.headers.get('Referer'); if (r) refHost = new URL(r).hostname.slice(0, 120); } catch (e) {}
    const country = (request.cf && request.cf.country) ? String(request.cf.country).slice(0, 4) : '';
    const now = new Date();
    const day = new Date(now.getTime() + 9 * 3600 * 1000).toISOString().slice(0, 10); // JST日付
    await env.DB.batch([
      env.DB.prepare(REFERRAL_DDL),
      env.DB.prepare('INSERT INTO referral_hits (ts, day, path, utm_source, utm_medium, utm_campaign, ref_host, country) VALUES (?,?,?,?,?,?,?,?)')
        .bind(now.toISOString(), day, url.pathname.slice(0, 160), g('utm_source'), g('utm_medium'), g('utm_campaign'), refHost, country),
    ]);
  } catch (e) { /* 無視 */ }
}

export { REFERRAL_DDL };

// 獲得ファネル: ファーストタッチ流入元を server 側 Cookie(fb_ft) に符号化。
// utm_source 優先、無ければ外部参照元ドメイン、どちらも無ければ direct。
function b64url(str) {
  return btoa(unescape(encodeURIComponent(str))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function firstTouchCookie(url, request) {
  const g = (k) => (url.searchParams.get(k) || '').slice(0, 80);
  let s = g('utm_source'), m = g('utm_medium'), c = g('utm_campaign');
  if (!s) {
    try {
      const r = request.headers.get('Referer');
      if (r) {
        const rh = new URL(r).hostname;
        if (rh && !/(^|\.)free-bizdocs\.com$/i.test(rh)) { s = rh.slice(0, 80); m = 'referral'; }
      }
    } catch (e) {}
  }
  if (!s) s = 'direct';
  const v = b64url(JSON.stringify({ s: s, m: m, c: c, l: url.pathname.slice(0, 120) }));
  return 'fb_ft=' + v + '; Path=/; Max-Age=7776000; SameSite=Lax; Secure; HttpOnly';
}

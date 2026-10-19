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
  // 旧 .html URL を新クリーンURLへ 301
  const LEGACY = { '/free.html': '/invoice', '/ryoshusho.html': '/receipt', '/nouhinsho.html': '/delivery', '/mitsumorisho.html': '/quote', '/hacchusho.html': '/purchase-order' };
  if (LEGACY[p]) return Response.redirect(url.origin + LEGACY[p], 301);

  // 公開API（認証・無料ツール・問い合わせ等）
  const PUBLIC_API = ['/api/auth/signup', '/api/auth/login', '/api/auth/logout', '/api/auth/me', '/api/auth/google/start', '/api/auth/google/callback', '/api/waitlist', '/api/contact', '/api/feedback'];
  if (PUBLIC_API.indexOf(p) >= 0) return next();
  if (p.startsWith('/api/free/')) return next();

  // 保護対象のアプリページ（クリーンURL・.html 両方）
  const APP_PAGES = ['/dashboard', '/invoice-list', '/invoice-create', '/quotes', '/recurring', '/reports', '/payments'];
  const pageKey = p.replace(/\.html$/, '');
  const isAppPage = APP_PAGES.indexOf(pageKey) >= 0;
  const isApi = p.startsWith('/api/');

  // 保護対象でなければ公開（トップ・ツール・ブログ・料金・法務など）
  if (!isAppPage && !isApi) return next();

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

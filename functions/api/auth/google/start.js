// Google OAuth: 認可リクエストへリダイレクト
const CLIENT_ID = '934709740515-p6pe9kbt5fqrr9iprc1kbtjmttg2igu2.apps.googleusercontent.com';
const REDIRECT = 'https://free-bizdocs.com/api/auth/google/callback';

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  let next = url.searchParams.get('next') || '';
  if (!/^\/(en\/account|en\/pricing|dashboard)$/.test(next)) next = '';
  const rnd = crypto.getRandomValues(new Uint8Array(16));
  let state = '';
  for (let i = 0; i < rnd.length; i++) state += rnd[i].toString(16).padStart(2, '0');
  const q = new URLSearchParams({
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT,
    response_type: 'code',
    scope: 'openid email profile',
    access_type: 'online',
    prompt: 'select_account',
    include_granted_scopes: 'true',
    state: state,
  });
  const h = new Headers();
  h.append('Location', 'https://accounts.google.com/o/oauth2/v2/auth?' + q.toString());
  h.append('Set-Cookie', 'gstate=' + state + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=600');
  if (next) h.append('Set-Cookie', 'gnext=' + encodeURIComponent(next) + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=600');
  return new Response(null, { status: 302, headers: h });
}

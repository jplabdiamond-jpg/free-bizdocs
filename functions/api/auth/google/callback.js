import { getCookie, makeSession, sessionCookie, normalizeEmail } from '../../../_lib.js';

const CLIENT_ID = '934709740515-p6pe9kbt5fqrr9iprc1kbtjmttg2igu2.apps.googleusercontent.com';
const REDIRECT = 'https://free-bizdocs.com/api/auth/google/callback';

function redir(path) { return new Response(null, { status: 302, headers: { 'Location': path } }); }
function decodeJwtPayload(seg) {
  let s = seg.replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  const bin = atob(s);
  try { return JSON.parse(decodeURIComponent(escape(bin))); } catch (e) { return JSON.parse(bin); }
}

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  const cs = getCookie(request, 'gstate');
  if (url.searchParams.get('error')) return redir('/login?err=google');
  if (!code) return redir('/login?err=google');
  if (!state || state !== cs) return redir('/login?err=state');

  let email = '';
  try {
    const tok = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code: code,
        client_id: CLIENT_ID,
        client_secret: env.GOOGLE_CLIENT_SECRET || '',
        redirect_uri: REDIRECT,
        grant_type: 'authorization_code',
      }).toString(),
    });
    const tj = await tok.json();
    if (!tj || !tj.id_token) return redir('/login?err=token');
    const payload = decodeJwtPayload(tj.id_token.split('.')[1]);
    if (!payload.email || payload.email_verified === false) return redir('/login?err=email');
    email = normalizeEmail(payload.email);
  } catch (e) { return redir('/login?err=exchange'); }

  let u = await env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(email).first();
  let uid;
  if (u) { uid = u.id; }
  else {
    const r = await env.DB.prepare(
      "INSERT INTO users (email, company_name, plan, invoice_seq) VALUES (?, '', 'free', 0)"
    ).bind(email).run();
    uid = r.meta.last_row_id;
  }
  const token = await makeSession(env.SESSION_SECRET, uid);
  // ログイン後の遷移先（英語フローは /en/account 等）。安全な自サイトパスのみ許可。
  let dest = '/dashboard';
  let gn = getCookie(request, 'gnext') || '';
  try { gn = decodeURIComponent(gn); } catch (e) {}
  if (gn && /^\/(en\/account|en\/pricing|dashboard)$/.test(gn)) dest = gn;
  const h = new Headers();
  h.append('Location', dest);
  h.append('Set-Cookie', sessionCookie(token, 60 * 60 * 24 * 30));
  h.append('Set-Cookie', 'gstate=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0');
  h.append('Set-Cookie', 'gnext=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0');
  return new Response(null, { status: 302, headers: h });
}

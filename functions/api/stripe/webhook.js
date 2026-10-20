// Stripe webhook: 入金（サブスク開始）で plan='pro'、解約で 'free' に自動反映。
// 署名検証は STRIPE_WEBHOOK_SECRET を使った HMAC-SHA256（Stripe の t=...,v1=... 形式）。
import { json, normalizeEmail } from '../../_lib.js';

function toHex(buf) {
  const b = new Uint8Array(buf); let s = '';
  for (let i = 0; i < b.length; i++) s += b[i].toString(16).padStart(2, '0');
  return s;
}
function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
async function verifyStripeSig(payload, sigHeader, secret, toleranceSec) {
  if (!sigHeader) return false;
  let t = null; const v1 = [];
  sigHeader.split(',').forEach(function (kv) {
    const i = kv.indexOf('=');
    if (i < 0) return;
    const k = kv.slice(0, i).trim(), v = kv.slice(i + 1).trim();
    if (k === 't') t = v;
    else if (k === 'v1') v1.push(v);
  });
  if (!t || !v1.length) return false;
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const mac = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(t + '.' + payload));
  const expected = toHex(mac);
  if (!v1.some(function (v) { return timingSafeEqual(v, expected); })) return false;
  if (toleranceSec) {
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - parseInt(t, 10)) > toleranceSec) return false;
  }
  return true;
}

async function grantPro(env, email, customerId) {
  if (!email) return;
  const u = await env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(email).first();
  if (u) {
    await env.DB.prepare('UPDATE users SET plan = ?, stripe_customer_id = ? WHERE id = ?')
      .bind('pro', customerId || null, u.id).run();
  } else {
    // まだアカウント登録前に支払った場合。登録/ログイン時に me.js が照合して昇格する。
    await env.DB.prepare(
      'INSERT INTO stripe_pending (email, customer_id) VALUES (?, ?) ' +
      'ON CONFLICT(email) DO UPDATE SET customer_id = excluded.customer_id'
    ).bind(email, customerId || null).run();
  }
}
async function revokePro(env, customerId) {
  if (!customerId) return;
  await env.DB.prepare("UPDATE users SET plan = 'free' WHERE stripe_customer_id = ?").bind(customerId).run();
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const secret = env.STRIPE_WEBHOOK_SECRET || '';
  if (!secret) return json({ error: 'webhook not configured' }, 500);

  const payload = await request.text();
  const sig = request.headers.get('stripe-signature');
  const valid = await verifyStripeSig(payload, sig, secret, 300);
  if (!valid) return json({ error: 'invalid signature' }, 400);

  let event;
  try { event = JSON.parse(payload); } catch (e) { return json({ error: 'bad json' }, 400); }
  const obj = (event.data && event.data.object) || {};

  try {
    if (event.type === 'checkout.session.completed') {
      // サブスク決済のみ対象（単発購入は無視）
      if (obj.mode === 'subscription' || obj.subscription) {
        const email = normalizeEmail((obj.customer_details && obj.customer_details.email) || obj.customer_email || '');
        await grantPro(env, email, obj.customer || null);
      }
    } else if (event.type === 'customer.subscription.deleted') {
      await revokePro(env, obj.customer || null);
    } else if (event.type === 'customer.subscription.updated') {
      const st = obj.status;
      if (st === 'canceled' || st === 'unpaid' || st === 'incomplete_expired') {
        await revokePro(env, obj.customer || null);
      } else if (st === 'active' || st === 'trialing') {
        // 再開・支払い成功時に pro を維持/復帰
        if (obj.customer) {
          await env.DB.prepare("UPDATE users SET plan = 'pro' WHERE stripe_customer_id = ?").bind(obj.customer).run();
        }
      }
    }
  } catch (e) {
    // DB エラー時は 500 を返し、Stripe 側の自動リトライに任せる
    return json({ error: 'handler error' }, 500);
  }
  return json({ received: true });
}

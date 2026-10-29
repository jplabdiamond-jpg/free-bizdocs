// 書類PDFをメールで送信（Resend）。無料でも送れるが、無料枠（ネットワーク単位・直近1時間に2件）で
// レート制限してスパムを防止。1日パス(fb_pass)またはPROログイン中は無制限。認証不要。
import { json, verifyPassToken, getCookie, currentUserId, normalizeEmail } from '../_lib.js';
import { ipKey } from './free/check.js';

const WINDOW = 3600, LIMIT = 2;

function validEmail(e) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(e); }

export async function onRequestPost(context) {
  const { env, request } = context;
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const lang = (String(b.lang || '').toLowerCase() === 'en') ? 'en' : 'ja';
  const T = (ja, en) => (lang === 'en' ? en : ja);

  const to = normalizeEmail(String(b.to || '').trim());
  if (!validEmail(to)) return json({ error: T('有効なメールアドレスを入力してください', 'Enter a valid email address.') }, 400);

  const pdf = String(b.pdf || '');
  if (pdf.length < 100) return json({ error: T('PDFの生成に失敗しました', 'Could not read the PDF.') }, 400);
  if (pdf.length > 12000000) return json({ error: T('ファイルが大きすぎます', 'The file is too large.') }, 413);

  const filename = (String(b.filename || 'document').replace(/[^\w.\- ]+/g, '').slice(0, 80) || 'document') + (/\.pdf$/i.test(b.filename || '') ? '' : '.pdf');
  const subject = (String(b.subject || '').trim().slice(0, 200)) || T('書類のご送付', 'Your document');
  const bodyText = String(b.body || '').trim().slice(0, 4000);
  const fromName = (String(b.from_name || '').trim().slice(0, 60)) || 'Free BizDoc';
  const replyTo = normalizeEmail(String(b.reply_to || '').trim());

  // レート制限（1日パス/PRO は免除）
  const pass = await verifyPassToken(env.SESSION_SECRET, getCookie(request, 'fb_pass'));
  let isPro = false;
  const uid = await currentUserId(request, env);
  if (uid) { try { const u = await env.DB.prepare('SELECT plan FROM users WHERE id=?').bind(uid).first(); isPro = !!(u && u.plan === 'pro'); } catch (e) {} }

  let remaining = 999;
  if (!pass && !isPro) {
    const ip = ipKey(request);
    const now = Math.floor(Date.now() / 1000), since = now - WINDOW;
    const row = await env.DB.prepare('SELECT COUNT(*) AS n, MIN(ts) AS oldest FROM free_usage WHERE ip=? AND ts>?').bind(ip, since).first();
    const used = (row && row.n) || 0;
    if (used >= LIMIT) {
      const oldest = (row && row.oldest) || now;
      const retry = Math.max(1, Math.ceil((oldest + WINDOW - now) / 60));
      return json({ ok: false, error: T('無料ツールは1時間に2件までです', 'The free tool allows 2 per hour.'), retry_min: retry }, 429);
    }
    await env.DB.prepare('INSERT INTO free_usage (ip, ts) VALUES (?, ?)').bind(ip, now).run();
    remaining = Math.max(0, LIMIT - used - 1);
  }

  if (!env.RESEND_API_KEY) return json({ error: T('メール送信は現在利用できません', 'Email sending is not available right now.') }, 500);

  // 送信元は検証済みドメイン(free-bizdocs.com)。表示名に発行者名、Reply-To に発行者メール。
  const fromAddr = env.SEND_FROM_ADDR || 'docs@free-bizdocs.com';
  const esc = (s) => String(s || '').replace(/[<>&]/g, (c) => ({ '<': '', '>': '', '&': '&amp;' }[c] || c));
  const from = esc(fromName) + ' <' + fromAddr + '>';
  const htmlEsc = (s) => String(s || '').replace(/[<>&]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));

  // 受け取り側にも Free BizDoc を知ってもらうブランドフッター（ロゴ＋概要＋無料で作れるリンク）
  const siteUrl = (lang === 'en' ? 'https://free-bizdocs.com/en/' : 'https://free-bizdocs.com/') + '?utm_source=email&utm_medium=document&utm_campaign=doc_email';
  const overview = T(
    'Free BizDoc は、請求書・見積書・納品書・領収書などのビジネス書類を<b style="color:#1766e6">登録不要・無料</b>で作成できるサービスです。インボイス・源泉徴収にも対応。',
    'Free BizDoc lets anyone create invoices, estimates, receipts and more — <b style="color:#1766e6">free, with no sign-up</b>. Correct tax for the US, UK, Australia and Canada.'
  );
  const ctaLabel = T('無料で書類を作る →', 'Create a document free →');
  const footer =
    '<div style="margin-top:28px;padding:20px;background:#f4f8ff;border:1px solid #dde8fb;border-radius:14px">'
    + '<img src="https://free-bizdocs.com/logo.png" alt="Free BizDoc" width="150" height="29" style="display:block;border:0;height:auto;width:150px;margin-bottom:11px">'
    + '<div style="font-size:13px;line-height:1.75;color:#4a5a6b">' + overview + '</div>'
    + '<a href="' + siteUrl + '" style="display:inline-block;margin-top:13px;background:#1766e6;color:#ffffff;text-decoration:none;font-weight:800;font-size:14px;border-radius:10px;padding:11px 20px">' + ctaLabel + '</a>'
    + '</div>'
    + '<div style="font-size:11.5px;color:#9aa7b4;margin-top:12px">'
    + T('このメールは送信者が Free BizDoc（free-bizdocs.com）を使って送信しました。', 'This email was sent by the sender using Free BizDoc (free-bizdocs.com).') + '</div>';

  const htmlBody =
    '<div style="max-width:560px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a2330">'
    + '<div style="font-size:15px;line-height:1.85;white-space:pre-wrap">'
    + (bodyText ? htmlEsc(bodyText) : T('書類を添付してお送りします。ご確認ください。', 'Please find the document attached.'))
    + '</div>'
    + footer
    + '</div>';

  const textOverview = T(
    'Free BizDoc — 請求書・見積書・領収書などを登録不要・無料で作成',
    'Free BizDoc — create invoices, estimates, receipts and more, free with no sign-up'
  );
  const payload = {
    from: from,
    to: [to],
    subject: subject,
    text: (bodyText || T('書類を添付してお送りします。ご確認ください。', 'Please find the document attached.'))
      + '\n\n— ' + textOverview + '\n' + siteUrl,
    html: htmlBody,
    attachments: [{ filename: filename, content: pdf }],
  };
  if (validEmail(replyTo)) payload.reply_to = replyTo;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'authorization': 'Bearer ' + env.RESEND_API_KEY, 'content-type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) {
      let detail = ''; try { detail = (await r.json()).message || ''; } catch (e) {}
      return json({ ok: false, error: T('送信に失敗しました。時間をおいてお試しください', 'Could not send. Please try again later.'), detail: detail }, 502);
    }
  } catch (e) {
    return json({ ok: false, error: T('送信に失敗しました。時間をおいてお試しください', 'Could not send. Please try again later.') }, 502);
  }

  return json({ ok: true, remaining: remaining, pass: !!pass || isPro });
}

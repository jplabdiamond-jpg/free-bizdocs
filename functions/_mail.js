// Resend 経由のメール送信（共有）。ブランドフッター・請求書リンク付きメール本文を生成。
// cron（リマインド/定期自動送付）と「支払いました」通知から利用。

function esc(s) { return String(s || '').replace(/[<>&]/g, (c) => ({ '<': '', '>': '', '&': '&amp;' }[c] || c)); }
function htmlEsc(s) { return String(s || '').replace(/[<>&]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c])); }

// 受け取り側に Free BizDoc を知ってもらうブランドフッター（send.js と同一デザイン）。
export function brandFooter(lang) {
  const T = (ja, en) => (lang === 'en' ? en : ja);
  const siteUrl = (lang === 'en' ? 'https://free-bizdocs.com/en/' : 'https://free-bizdocs.com/') + '?utm_source=email&utm_medium=invoice&utm_campaign=online_invoice';
  const overview = T(
    'Free BizDoc は、請求書・見積書・納品書・領収書などのビジネス書類を<b style="color:#1766e6">登録不要・無料</b>で作成できるサービスです。インボイス・源泉徴収にも対応。',
    'Free BizDoc lets anyone create invoices, estimates, receipts and more — <b style="color:#1766e6">free, with no sign-up</b>. Correct tax for the US, UK, Australia and Canada.'
  );
  const ctaLabel = T('無料で書類を作る →', 'Create a document free →');
  return '<div style="margin-top:28px;padding:20px;background:#f4f8ff;border:1px solid #dde8fb;border-radius:14px">'
    + '<img src="https://free-bizdocs.com/logo.png" alt="Free BizDoc" width="150" height="29" style="display:block;border:0;height:auto;width:150px;margin-bottom:11px">'
    + '<div style="font-size:13px;line-height:1.75;color:#4a5a6b">' + overview + '</div>'
    + '<a href="' + siteUrl + '" style="display:inline-block;margin-top:13px;background:#1766e6;color:#ffffff;text-decoration:none;font-weight:800;font-size:14px;border-radius:10px;padding:11px 20px">' + ctaLabel + '</a>'
    + '</div>'
    + '<div style="font-size:11.5px;color:#9aa7b4;margin-top:12px">'
    + T('このメールは送信者が Free BizDoc（free-bizdocs.com）を使って送信しました。', 'This email was sent by the sender using Free BizDoc (free-bizdocs.com).') + '</div>';
}

// Resend でメール送信。成功: {ok:true}、失敗: {ok:false, error}
export async function sendMail(env, opts) {
  if (!env || !env.RESEND_API_KEY) return { ok: false, error: 'no_api_key' };
  const fromAddr = env.SEND_FROM_ADDR || 'docs@free-bizdocs.com';
  const from = esc(String(opts.fromName || 'Free BizDoc').slice(0, 60)) + ' <' + fromAddr + '>';
  const payload = {
    from: from,
    to: [opts.to],
    subject: String(opts.subject || '').slice(0, 200),
    html: opts.html || '',
    text: opts.text || '',
  };
  if (opts.replyTo && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(opts.replyTo)) payload.reply_to = opts.replyTo;
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'authorization': 'Bearer ' + env.RESEND_API_KEY, 'content-type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) { let d = ''; try { d = (await r.json()).message || ''; } catch (e) {} return { ok: false, error: d || ('http_' + r.status) }; }
    return { ok: true };
  } catch (e) { return { ok: false, error: 'fetch_failed' }; }
}

function yen(n, lang) {
  const v = Math.round(Number(n) || 0);
  return (lang === 'en') ? ('¥' + v.toLocaleString('en-US')) : ('¥' + v.toLocaleString('ja-JP'));
}

// オンライン請求書リンク付きのメール本文（請求案内・リマインド共通）。
// opts: { lang, kind:'notice'|'reminder', senderName, docNo, amount, dueDate, link, message, overdue }
export function invoiceEmailHtml(opts) {
  const lang = (opts.lang === 'en') ? 'en' : 'ja';
  const T = (ja, en) => (lang === 'en' ? en : ja);
  const link = String(opts.link || '');
  const sender = htmlEsc(opts.senderName || '');
  const amount = yen(opts.amount, lang);
  const title = (opts.kind === 'reminder')
    ? (opts.overdue ? T('お支払い期限が過ぎています', 'Your payment is overdue')
                    : T('お支払い期限が近づいています', 'Your payment is due soon'))
    : T('請求書のご案内', 'Invoice from ' + (opts.senderName || 'your supplier'));
  const lead = (opts.kind === 'reminder')
    ? T('下記のお支払いがまだ確認できておりません。ご確認をお願いいたします。',
        'We have not yet confirmed the payment below. Please take a moment to review it.')
    : T((opts.senderName || '') + ' 様より請求書が発行されました。下記よりご確認・お支払いいただけます。',
        (opts.senderName || 'Your supplier') + ' has issued an invoice. You can review and pay it below.');
  const rows = [];
  if (opts.docNo) rows.push([T('請求書番号', 'Invoice No.'), htmlEsc(opts.docNo)]);
  rows.push([T('ご請求金額', 'Amount due'), '<b style="color:#0f2744">' + amount + '</b>']);
  if (opts.dueDate) rows.push([T('お支払い期限', 'Due date'), htmlEsc(opts.dueDate) + (opts.overdue ? ' <span style="color:#d64545;font-weight:700">(' + T('期限超過', 'overdue') + ')</span>' : '')]);
  const rowsHtml = rows.map(function (r) {
    return '<tr><td style="padding:6px 12px 6px 0;color:#6b7a8d;font-size:13px;white-space:nowrap">' + r[0] + '</td>'
      + '<td style="padding:6px 0;color:#1a2330;font-size:14px">' + r[1] + '</td></tr>';
  }).join('');
  return '<div style="max-width:560px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a2330">'
    + '<div style="font-size:18px;font-weight:800;color:#0f2744;margin-bottom:6px">' + title + '</div>'
    + '<div style="font-size:14.5px;line-height:1.8;color:#3a4a5b">' + lead + '</div>'
    + (opts.message ? '<div style="margin-top:12px;padding:12px 14px;background:#f7f9fc;border-radius:10px;font-size:13.5px;line-height:1.8;white-space:pre-wrap;color:#3a4a5b">' + htmlEsc(opts.message) + '</div>' : '')
    + '<table style="margin:16px 0;border-collapse:collapse">' + rowsHtml + '</table>'
    + (link ? '<a href="' + link + '" style="display:inline-block;background:#1766e6;color:#ffffff;text-decoration:none;font-weight:800;font-size:15px;border-radius:11px;padding:13px 26px">' + T('請求書を開く・お支払い →', 'View & pay invoice →') + '</a>'
            + '<div style="font-size:11.5px;color:#9aa7b4;margin-top:8px">' + T('ボタンが開かない場合: ', 'If the button does not work: ') + '<a href="' + link + '" style="color:#1766e6">' + link + '</a></div>' : '')
    + brandFooter(lang)
    + '</div>';
}

export function invoiceEmailText(opts) {
  const lang = (opts.lang === 'en') ? 'en' : 'ja';
  const T = (ja, en) => (lang === 'en' ? en : ja);
  const parts = [];
  if (opts.kind === 'reminder') parts.push(T('お支払いのご確認のお願い', 'Payment reminder'));
  else parts.push(T('請求書のご案内', 'Invoice'));
  if (opts.docNo) parts.push(T('請求書番号: ', 'Invoice No.: ') + opts.docNo);
  parts.push(T('ご請求金額: ', 'Amount due: ') + yen(opts.amount, lang));
  if (opts.dueDate) parts.push(T('お支払い期限: ', 'Due date: ') + opts.dueDate);
  if (opts.message) parts.push('\n' + opts.message);
  if (opts.link) parts.push('\n' + T('請求書を開く・お支払い: ', 'View & pay: ') + opts.link);
  parts.push('\n— Free BizDoc (free-bizdocs.com)');
  return parts.join('\n');
}

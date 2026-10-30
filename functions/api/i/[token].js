// 公開オンライン請求書API（認証不要）。
// GET  /api/i/<token>      → 請求書データ（画面表示・PDF生成用）
// POST /api/i/<token>      → 取引先が「支払いました」と報告 → 発行者へ通知メール
import { json } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';
import { sendMail, brandFooter } from '../../_mail.js';

async function findDoc(env, token) {
  if (!token || token.length < 10) return null;
  return await env.DB.prepare(
    `SELECT d.*, c.name AS client_name, c.honorific, c.reg_number AS client_reg, c.address AS client_address
     FROM documents d LEFT JOIN clients c ON c.id = d.client_id
     WHERE d.share_token = ?`
  ).bind(token).first();
}

export async function onRequestGet(context) {
  const { env, params } = context;
  await ensureCols(env);
  const doc = await findDoc(env, params.token);
  if (!doc || doc.status === 'draft') return json({ ok: false, error: 'not found' }, 404);

  const items = (await env.DB.prepare('SELECT * FROM line_items WHERE document_id = ? ORDER BY sort_order').bind(doc.id).all()).results || [];
  const user = await env.DB.prepare('SELECT company_name, company_addr, reg_number, default_bank, paylink FROM users WHERE id = ?').bind(doc.user_id).first() || {};
  const paylink = (doc.paylink && /^https?:\/\//i.test(doc.paylink)) ? doc.paylink
    : ((user.paylink && /^https?:\/\//i.test(user.paylink)) ? user.paylink : '');

  const co = {
    company_name: user.company_name || '', company_addr: user.company_addr || '',
    reg_number: user.reg_number || '', default_bank: user.default_bank || '', paylink: paylink,
  };
  // render() が参照する書類フィールドのみを公開（内部IDやメール等は返さない）。
  const safeDoc = {
    type: doc.type, doc_no: doc.doc_no, status: doc.status,
    issue_date: doc.issue_date, due_date: doc.due_date,
    subtotal: doc.subtotal, tax: doc.tax, withholding: doc.withholding,
    total: doc.total, payable: doc.payable, paid_total: doc.paid_total,
    bank: doc.bank, notes: doc.notes,
    client_name: doc.client_name, honorific: doc.honorific,
    client_reg: doc.client_reg, client_address: doc.client_address,
  };
  const remaining = Math.max(0, (doc.payable || 0) - (doc.paid_total || 0));
  return json({
    ok: true, doc: safeDoc, items: items, company: co, kind: (doc.type || 'invoice'),
    paylink: paylink, status: doc.status, remaining: remaining,
    paid: doc.status === 'paid', payer_reported: doc.payer_reported || null,
    sender_name: user.company_name || '',
  });
}

export async function onRequestPost(context) {
  const { env, params } = context;
  await ensureCols(env);
  const doc = await findDoc(env, params.token);
  if (!doc || doc.status === 'draft') return json({ ok: false, error: 'not found' }, 404);
  if (doc.status === 'paid') return json({ ok: true, already: true });

  const now = new Date().toISOString();
  // 連打スパム防止: 直近1時間に報告済みなら通知を再送しない。
  let notify = true;
  if (doc.payer_reported) {
    try { if (Date.now() - Date.parse(doc.payer_reported) < 3600000) notify = false; } catch (e) {}
  }
  try { await env.DB.prepare('UPDATE documents SET payer_reported=? WHERE id=?').bind(now, doc.id).run(); } catch (e) {}

  if (notify) {
    try {
      const u = await env.DB.prepare('SELECT email, company_name FROM users WHERE id=?').bind(doc.user_id).first();
      if (u && u.email) {
        const yen = '¥' + (Math.round(doc.payable || 0)).toLocaleString('ja-JP');
        const payUrl = 'https://free-bizdocs.com/payments';
        const html = '<div style="max-width:560px;margin:0 auto;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a2330">'
          + '<div style="font-size:18px;font-weight:800;color:#0f2744;margin-bottom:6px">取引先がお支払いを報告しました</div>'
          + '<div style="font-size:14.5px;line-height:1.8;color:#3a4a5b">'
          + '「' + (doc.client_name || '取引先') + '」様が、オンライン請求書で<b>支払い済み</b>と報告しました。入金をご確認のうえ、消込（入金記録）をお願いします。</div>'
          + '<table style="margin:16px 0;border-collapse:collapse">'
          + '<tr><td style="padding:6px 12px 6px 0;color:#6b7a8d;font-size:13px">請求書番号</td><td style="padding:6px 0;font-size:14px">' + (doc.doc_no || '—') + '</td></tr>'
          + '<tr><td style="padding:6px 12px 6px 0;color:#6b7a8d;font-size:13px">金額</td><td style="padding:6px 0;font-size:14px"><b>' + yen + '</b></td></tr>'
          + '</table>'
          + '<a href="' + payUrl + '" style="display:inline-block;background:#1766e6;color:#fff;text-decoration:none;font-weight:800;font-size:15px;border-radius:11px;padding:13px 26px">入金管理を開く →</a>'
          + brandFooter('ja') + '</div>';
        await sendMail(env, {
          to: u.email, fromName: 'Free BizDoc', subject: '【入金報告】' + (doc.client_name || '取引先') + ' 様 / ' + (doc.doc_no || '請求書'),
          html: html, text: '取引先「' + (doc.client_name || '') + '」様がお支払いを報告しました。入金管理: ' + payUrl,
        });
      }
    } catch (e) { /* 通知失敗でも報告自体は成功 */ }
  }
  return json({ ok: true });
}

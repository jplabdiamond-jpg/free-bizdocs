// 売上レポート: ログインユーザーの発行データ(documents/line_items/payments)から年次集計。
import { json, currentUserId } from '../_lib.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);

  const url = new URL(request.url);
  async function q(sql, binds) {
    try { return (await env.DB.prepare(sql).bind(...binds).all()).results || []; } catch (e) { return []; }
  }
  async function q1(sql, binds) {
    try { return await env.DB.prepare(sql).bind(...binds).first(); } catch (e) { return null; }
  }

  // データのある年の一覧
  const yearRows = await q(
    "SELECT DISTINCT substr(issue_date,1,4) AS y FROM documents WHERE user_id=? AND type='invoice' AND status!='draft' AND issue_date IS NOT NULL AND issue_date!='' ORDER BY y DESC",
    [uid]
  );
  const years = yearRows.map(function (r) { return r.y; }).filter(Boolean);
  let year = (url.searchParams.get('year') || '').match(/^\d{4}$/) ? url.searchParams.get('year') : '';
  if (!year) year = years[0] || String(new Date().getFullYear());

  // 合計
  const tot = (await q1(
    "SELECT COALESCE(SUM(subtotal),0) sales, COALESCE(SUM(total),0) total, COALESCE(SUM(withholding),0) wh, COUNT(*) cnt FROM documents WHERE user_id=? AND type='invoice' AND status!='draft' AND substr(issue_date,1,4)=?",
    [uid, year]
  )) || { sales: 0, total: 0, wh: 0, cnt: 0 };

  // 月次売上（税抜）
  const monthlyRows = await q(
    "SELECT substr(issue_date,1,7) ym, COALESCE(SUM(subtotal),0) sales FROM documents WHERE user_id=? AND type='invoice' AND status!='draft' AND substr(issue_date,1,4)=? GROUP BY ym ORDER BY ym",
    [uid, year]
  );
  const monthMap = {}; monthlyRows.forEach(function (r) { monthMap[r.ym] = r.sales; });
  const monthly = [];
  for (let mo = 1; mo <= 12; mo++) { const ym = year + '-' + String(mo).padStart(2, '0'); monthly.push({ ym: ym, month: mo, sales: monthMap[ym] || 0 }); }

  // 取引先別（上位）
  const byClient = await q(
    "SELECT COALESCE(NULLIF(c.name,''),'（取引先未設定）') name, COALESCE(SUM(d.subtotal),0) sales FROM documents d LEFT JOIN clients c ON c.id=d.client_id WHERE d.user_id=? AND d.type='invoice' AND d.status!='draft' AND substr(d.issue_date,1,4)=? GROUP BY c.id ORDER BY sales DESC LIMIT 8",
    [uid, year]
  );

  // 税区分別（line_items の税率ごと）
  const taxRows = await q(
    "SELECT li.tax_rate rate, COALESCE(SUM(li.qty*li.unit_price),0) base FROM line_items li JOIN documents d ON d.id=li.document_id WHERE d.user_id=? AND d.type='invoice' AND d.status!='draft' AND substr(d.issue_date,1,4)=? GROUP BY li.tax_rate",
    [uid, year]
  );
  let base10 = 0, base8 = 0, base0 = 0;
  taxRows.forEach(function (r) { const rt = Number(r.rate); if (rt === 10) base10 += r.base; else if (rt === 8) base8 += r.base; else base0 += r.base; });

  // 平均入金日数（発行日→最終入金日）
  const payd = await q1(
    `SELECT AVG(julianday(pd.maxdate) - julianday(d.issue_date)) days
     FROM documents d
     JOIN (SELECT document_id, MAX(paid_date) maxdate FROM payments WHERE paid_date IS NOT NULL AND paid_date!='' GROUP BY document_id) pd ON pd.document_id = d.id
     WHERE d.user_id=? AND d.type='invoice' AND d.status='paid' AND substr(d.issue_date,1,4)=? AND d.issue_date IS NOT NULL AND d.issue_date!=''`,
    [uid, year]
  );
  const avgPayDays = (payd && payd.days != null) ? Math.round(payd.days * 10) / 10 : null;

  const cnt = tot.cnt || 0;
  const avgInvoice = cnt > 0 ? Math.round((tot.total || 0) / cnt) : 0;

  return json({
    ok: true, year: year, years: years,
    sales: tot.sales || 0, total: tot.total || 0, withholding: tot.wh || 0,
    doc_count: cnt, avg_invoice: avgInvoice, avg_pay_days: avgPayDays,
    monthly: monthly,
    by_client: byClient,
    tax: { base10: base10, base8: base8, base0: base0 },
  });
}

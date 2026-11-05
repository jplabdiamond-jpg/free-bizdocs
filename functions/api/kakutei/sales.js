import { json, currentUserId } from '../../_lib.js';

// 売上集計に使える書類タイプ（既定は請求書のみ。領収書は任意で追加）
var SALES_TYPES = { invoice: 1, receipt: 1 };

// GET /api/kakutei/sales?year=2025&types=invoice[,receipt]
// ログインユーザーが発行した書類を、指定年（西暦）の発行日で集計して返す。
// 下書き(draft)は除外。税込(total)・税抜(subtotal)の両方を返す。
export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);

  const url = new URL(request.url);
  const year = parseInt(url.searchParams.get('year'), 10);
  if (!year || year < 2000 || year > 2100) return json({ error: 'year (西暦) が必要です' }, 400);

  let types = (url.searchParams.get('types') || 'invoice')
    .split(',').map(function (s) { return s.trim(); })
    .filter(function (t) { return SALES_TYPES[t]; });
  if (!types.length) types = ['invoice'];

  const from = year + '-01-01';
  const to = year + '-12-31';
  const ph = types.map(function () { return '?'; }).join(',');
  const sql =
    'SELECT type, COUNT(*) AS n, COALESCE(SUM(total),0) AS incl, COALESCE(SUM(subtotal),0) AS excl ' +
    'FROM documents ' +
    "WHERE user_id = ? AND status != 'draft' AND type IN (" + ph + ') ' +
    'AND issue_date >= ? AND issue_date <= ? ' +
    'GROUP BY type';
  const binds = [uid].concat(types).concat([from, to]);

  let results = [];
  try {
    const q = await env.DB.prepare(sql).bind(...binds).all();
    results = q.results || [];
  } catch (e) {
    return json({ error: 'query_failed' }, 500);
  }

  let incl = 0, excl = 0, count = 0; const byType = {};
  results.forEach(function (r) {
    incl += r.incl; excl += r.excl; count += r.n;
    byType[r.type] = { n: r.n, incl: r.incl, excl: r.excl };
  });

  return json({ year: year, types: types, from: from, to: to, count: count, total_incl: incl, total_excl: excl, byType: byType });
}

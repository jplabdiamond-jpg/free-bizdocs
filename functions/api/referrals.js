// 紹介/流入の集計（オーナーのみ閲覧）。第一者計測 referral_hits を直近30日で集計。
import { json, currentUserId } from '../_lib.js';

const OWNER_IDS = [1]; // オーナー（さね）のアカウント user_id
const DDL = 'CREATE TABLE IF NOT EXISTS referral_hits (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, day TEXT, path TEXT, utm_source TEXT, utm_medium TEXT, utm_campaign TEXT, ref_host TEXT, country TEXT)';

export async function onRequestGet(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  if (OWNER_IDS.indexOf(uid) < 0) return json({ error: 'forbidden' }, 403);

  try { await env.DB.prepare(DDL).run(); } catch (e) { /* 初回でテーブル未作成でも落とさない */ }

  const since = new Date(Date.now() + 9 * 3600 * 1000 - 30 * 864e5).toISOString().slice(0, 10);
  async function q(sql) {
    try { return (await env.DB.prepare(sql).bind(since).all()).results || []; } catch (e) { return []; }
  }
  const bySource = await q("SELECT COALESCE(NULLIF(utm_source,''),'(なし)') AS k, COUNT(*) AS n FROM referral_hits WHERE day>=? GROUP BY k ORDER BY n DESC LIMIT 50");
  const byCampaign = await q("SELECT COALESCE(NULLIF(utm_campaign,''),'(なし)') AS k, COUNT(*) AS n FROM referral_hits WHERE day>=? GROUP BY k ORDER BY n DESC LIMIT 50");
  const byMedium = await q("SELECT COALESCE(NULLIF(utm_medium,''),'(なし)') AS k, COUNT(*) AS n FROM referral_hits WHERE day>=? GROUP BY k ORDER BY n DESC LIMIT 50");
  const byRef = await q("SELECT COALESCE(NULLIF(ref_host,''),'(直接/なし)') AS k, COUNT(*) AS n FROM referral_hits WHERE day>=? GROUP BY k ORDER BY n DESC LIMIT 50");
  const byPath = await q("SELECT path AS k, COUNT(*) AS n FROM referral_hits WHERE day>=? GROUP BY path ORDER BY n DESC LIMIT 30");
  const daily = await q("SELECT day AS k, COUNT(*) AS n FROM referral_hits WHERE day>=? GROUP BY day ORDER BY day DESC LIMIT 30");

  let total = 0; bySource.forEach(function (r) { total += r.n; });
  return json({ ok: true, since, total, bySource, byCampaign, byMedium, byRef, byPath, daily });
}

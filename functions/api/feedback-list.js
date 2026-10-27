// 要望・フィードバックの一覧（オーナーのみ閲覧）。D1 feedback を新しい順に返す。
import { json, currentUserId } from '../_lib.js';

const OWNER_IDS = [1]; // オーナー（さね）の user_id
const DDL = 'CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, kind TEXT, body TEXT, ts INTEGER, page TEXT, lang TEXT)';

export async function onRequestGet(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  if (OWNER_IDS.indexOf(uid) < 0) return json({ error: 'forbidden' }, 403);

  try { await env.DB.prepare(DDL).run(); } catch (e) {}
  // 旧テーブルに列が無くても落とさない（非破壊マイグレーション）
  for (const col of ['page TEXT', 'lang TEXT', 'status TEXT', 'note TEXT', 'updated_at INTEGER']) {
    try { await env.DB.prepare('ALTER TABLE feedback ADD COLUMN ' + col).run(); } catch (e) {}
  }

  async function q(sql) {
    try { return (await env.DB.prepare(sql).all()).results || []; } catch (e) { return []; }
  }
  const items = await q("SELECT id, name, kind, body, ts, page, lang, COALESCE(NULLIF(status,''),'open') AS status, note, updated_at FROM feedback ORDER BY id DESC LIMIT 300");
  const byKind = await q("SELECT COALESCE(NULLIF(kind,''),'(なし)') AS k, COUNT(*) AS n FROM feedback GROUP BY k ORDER BY n DESC");
  const byLang = await q("SELECT COALESCE(NULLIF(lang,''),'(不明)') AS k, COUNT(*) AS n FROM feedback GROUP BY k ORDER BY n DESC");
  let total = 0; byKind.forEach(function (r) { total += r.n; });
  let done = 0; items.forEach(function (r) { if (r.status === 'done') done += 1; });

  return json({ ok: true, total, done, open: items.length - done, items, byKind, byLang });
}

// 要望のトリアージ更新（オーナーのみ）。status（open/done）と note を部分更新。
import { json, currentUserId } from '../_lib.js';

const OWNER_IDS = [1]; // オーナー（さね）の user_id

export async function onRequestPost(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  if (OWNER_IDS.indexOf(uid) < 0) return json({ error: 'forbidden' }, 403);

  // 列が無い旧テーブルでも落とさない
  for (const col of ['status TEXT', 'note TEXT', 'updated_at INTEGER']) {
    try { await env.DB.prepare('ALTER TABLE feedback ADD COLUMN ' + col).run(); } catch (e) {}
  }

  let b = {};
  try { b = await request.json(); } catch (e) {}
  const id = parseInt(b.id, 10);
  if (!(id > 0)) return json({ error: 'id が不正です' }, 400);

  const sets = [], vals = [];
  if (b.status !== undefined) {
    const st = (String(b.status) === 'done') ? 'done' : 'open';
    sets.push('status=?'); vals.push(st);
  }
  if (b.note !== undefined) {
    sets.push('note=?'); vals.push(String(b.note || '').slice(0, 2000));
  }
  if (!sets.length) return json({ error: '更新内容がありません' }, 400);
  sets.push('updated_at=?'); vals.push(Math.floor(Date.now() / 1000));
  vals.push(id);

  try {
    const r = await env.DB.prepare('UPDATE feedback SET ' + sets.join(', ') + ' WHERE id=?').bind(...vals).run();
    const changed = (r.meta && r.meta.changes) || 0;
    if (!changed) return json({ error: '対象が見つかりません' }, 404);
    return json({ ok: true });
  } catch (e) {
    return json({ error: '更新に失敗しました' }, 500);
  }
}

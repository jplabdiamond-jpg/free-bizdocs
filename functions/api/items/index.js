// ⑥ 品目マスタ（よく使う明細）: 一覧・追加・削除。ログイン必須。
import { json, currentUserId } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  let rows = [];
  try { rows = (await env.DB.prepare('SELECT * FROM items_master WHERE user_id=? ORDER BY name').bind(uid).all()).results || []; } catch (e) {}
  return json({ items: rows });
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const name = String(b.name || '').trim().slice(0, 120);
  if (!name) return json({ error: '品目名を入力してください' }, 400);
  const unit = String(b.unit || '').slice(0, 20);
  const price = Math.round(Number(b.unit_price) || 0);
  const tax = [0, 8, 10].indexOf(Number(b.tax_rate)) >= 0 ? Number(b.tax_rate) : 10;
  const wh = Number(b.withholding) === 1 ? 1 : 0;
  // 同名があれば更新（重複を増やさない）
  const ex = await env.DB.prepare('SELECT id FROM items_master WHERE user_id=? AND name=?').bind(uid, name).first();
  if (ex) {
    await env.DB.prepare('UPDATE items_master SET unit=?, unit_price=?, tax_rate=?, withholding=? WHERE id=? AND user_id=?').bind(unit, price, tax, wh, ex.id, uid).run();
    return json({ ok: true, id: ex.id, updated: true });
  }
  const r = await env.DB.prepare('INSERT INTO items_master (user_id, name, unit, unit_price, tax_rate, withholding) VALUES (?,?,?,?,?,?)').bind(uid, name, unit, price, tax, wh).run();
  return json({ ok: true, id: r.meta.last_row_id });
}

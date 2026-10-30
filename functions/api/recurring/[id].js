// 定期請求テンプレートの更新（有効/停止の切替・編集）と削除。
import { json, currentUserId, normalizeEmail } from '../../_lib.js';
import { ensureTable, advanceRun, initialNextRun } from '../_recgen.js';
import { ensureCols } from '../../_schema.js';

const CYCLES = { monthly: 1, bimonthly: 1, quarterly: 1, halfyear: 1, yearly: 1 };

async function own(env, uid, id) {
  return await env.DB.prepare('SELECT * FROM recurring WHERE id=? AND user_id=?').bind(id, uid).first();
}

export async function onRequestPut(context) {
  const { env, request, params } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureTable(env);
  const id = parseInt(params.id, 10);
  const cur = await own(env, uid, id);
  if (!cur) return json({ error: 'not found' }, 404);

  let b = {};
  try { b = await request.json(); } catch (e) {}

  // 有効/停止の切替だけの場合
  if (typeof b.active === 'boolean' && Object.keys(b).length === 1) {
    await env.DB.prepare('UPDATE recurring SET active=? WHERE id=? AND user_id=?').bind(b.active ? 1 : 0, id, uid).run();
    return json({ ok: true });
  }

  // 編集
  const title = (b.title != null) ? String(b.title).slice(0, 120) : cur.title;
  const items = Array.isArray(b.items) ? b.items.filter(function (it) { return it && (it.name || it.unit_price); }) : null;
  const itemsJson = items ? JSON.stringify(items) : cur.items_json;
  const cycle = CYCLES[b.cycle] ? b.cycle : cur.cycle;
  let dom = parseInt(b.day_of_month, 10); if (!(dom >= 1 && dom <= 31) && dom !== 99) dom = cur.day_of_month;
  let dueDays = parseInt(b.due_days, 10); if (!(dueDays >= 0 && dueDays <= 180)) dueDays = cur.due_days;
  const mode = (b.mode === 'draft' || b.mode === 'auto') ? b.mode : cur.mode;
  const active = (typeof b.active === 'boolean') ? (b.active ? 1 : 0) : cur.active;
  const autoSend = (b.auto_send !== undefined) ? (b.auto_send ? 1 : 0) : (cur.auto_send ? 1 : 0);
  // 起算日を変えたら next_run を再計算（過去で止まらないように）
  const nextRun = (dom !== cur.day_of_month) ? initialNextRun(dom) : cur.next_run;

  await ensureCols(env);
  // 宛先メールが指定されたら取引先マスタへ保存
  if (b.recipient_email !== undefined && cur.client_id) {
    try { await env.DB.prepare('UPDATE clients SET email=? WHERE id=? AND user_id=?').bind(normalizeEmail(b.recipient_email), cur.client_id, uid).run(); } catch (e) {}
  }
  await env.DB.prepare(
    'UPDATE recurring SET title=?, items_json=?, bank=?, notes=?, cycle=?, day_of_month=?, due_days=?, mode=?, active=?, next_run=?, auto_send=? WHERE id=? AND user_id=?'
  ).bind(title, itemsJson, (b.bank != null ? String(b.bank) : cur.bank), (b.notes != null ? String(b.notes) : cur.notes),
    cycle, dom, dueDays, mode, active, nextRun, autoSend, id, uid).run();
  return json({ ok: true, next_run: nextRun });
}

export async function onRequestDelete(context) {
  const { env, request, params } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureTable(env);
  const id = parseInt(params.id, 10);
  await env.DB.prepare('DELETE FROM recurring WHERE id=? AND user_id=?').bind(id, uid).run();
  return json({ ok: true });
}

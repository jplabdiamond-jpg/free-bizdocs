// 定期請求テンプレートの一覧・作成。一覧取得時に期日到来分を自動生成（遅延生成）。
import { json, currentUserId, calcTotals } from '../../_lib.js';
import { ensureTable, generateDueForUser, initialNextRun } from '../_recgen.js';
import { ensureCols } from '../../_schema.js';

function todayISO() { return new Date().toISOString().slice(0, 10); }
const CYCLES = { monthly: 1, bimonthly: 1, quarterly: 1, halfyear: 1, yearly: 1 };

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);

  await ensureTable(env);
  let generated = 0;
  try { generated = await generateDueForUser(env, uid); } catch (e) {}

  let rows = [];
  try {
    rows = (await env.DB.prepare(
      'SELECT r.*, c.name AS client_name, c.email AS client_email FROM recurring r LEFT JOIN clients c ON c.id=r.client_id WHERE r.user_id=? ORDER BY r.active DESC, r.next_run'
    ).bind(uid).all()).results || [];
  } catch (e) {}

  const t = todayISO();
  let dueCount = 0;
  const list = rows.map(function (r) {
    let amount = 0;
    try { amount = calcTotals(JSON.parse(r.items_json || '[]')).total; } catch (e) {}
    const due = r.active && r.next_run && r.next_run <= t;
    if (due) dueCount++;
    return {
      id: r.id, title: r.title, client_id: r.client_id, client_name: r.client_name,
      cycle: r.cycle, day_of_month: r.day_of_month, due_days: r.due_days, mode: r.mode,
      next_run: r.next_run, active: r.active, last_run: r.last_run, amount: amount,
      auto_send: r.auto_send ? 1 : 0, client_email: r.client_email || '',
    };
  });
  return json({ ok: true, recurring: list, generated: generated, due_today: dueCount });
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);

  const u = await env.DB.prepare('SELECT plan FROM users WHERE id=?').bind(uid).first();
  if (!u || u.plan !== 'pro') return json({ error: '定期請求はPROプランの機能です。', upsell: true }, 403);

  await ensureTable(env);
  await ensureCols(env);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const items = Array.isArray(b.items) ? b.items.filter(function (it) { return it && (it.name || it.unit_price); }) : [];
  if (!items.length) return json({ error: '明細を入力してください' }, 400);

  // 取引先: client_id 優先、無ければ名前から find-or-create
  let clientId = b.client_id || null;
  if (!clientId && b.client_name && String(b.client_name).trim()) {
    const nm = String(b.client_name).trim();
    const ex = await env.DB.prepare('SELECT id FROM clients WHERE user_id=? AND name=?').bind(uid, nm).first();
    if (ex) clientId = ex.id;
    else { const ci = await env.DB.prepare('INSERT INTO clients (user_id, name, honorific, email) VALUES (?,?,?,?)').bind(uid, nm, '御中', String(b.recipient_email || '').trim().toLowerCase()).run(); clientId = ci.meta.last_row_id; }
  }
  // 宛先メールが指定されたら取引先マスタへ保存（自動送付・リマインドに使用）
  if (clientId && b.recipient_email !== undefined && String(b.recipient_email || '').trim()) {
    try { await env.DB.prepare('UPDATE clients SET email=? WHERE id=? AND user_id=?').bind(String(b.recipient_email).trim().toLowerCase(), clientId, uid).run(); } catch (e) {}
  }

  const cycle = CYCLES[b.cycle] ? b.cycle : 'monthly';
  let dom = parseInt(b.day_of_month, 10); if (!(dom >= 1 && dom <= 31) && dom !== 99) dom = 1;
  let dueDays = parseInt(b.due_days, 10); if (!(dueDays >= 0 && dueDays <= 180)) dueDays = 30;
  const mode = (b.mode === 'draft') ? 'draft' : 'auto';
  const autoSend = (b.auto_send ? 1 : 0);
  const nextRun = initialNextRun(dom);

  const r = await env.DB.prepare(
    'INSERT INTO recurring (user_id, client_id, title, items_json, bank, notes, cycle, day_of_month, due_days, mode, next_run, active, auto_send) VALUES (?,?,?,?,?,?,?,?,?,?,?,1,?)'
  ).bind(uid, clientId, String(b.title || '').slice(0, 120), JSON.stringify(items), String(b.bank || ''), String(b.notes || ''), cycle, dom, dueDays, mode, nextRun, autoSend).run();
  return json({ ok: true, id: r.meta.last_row_id, next_run: nextRun });
}

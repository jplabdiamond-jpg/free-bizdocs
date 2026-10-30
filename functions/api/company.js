import { json, currentUserId } from '../_lib.js';
import { ensureCols } from '../_schema.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  const user = await env.DB.prepare('SELECT id, email, company_name, company_addr, reg_number, default_bank, plan, invoice_seq, paylink, auto_remind FROM users WHERE id = ?').bind(uid).first();
  return json({ company: user });
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  await env.DB.prepare(
    'UPDATE users SET company_name = ?, company_addr = ?, reg_number = ?, default_bank = ? WHERE id = ?'
  ).bind(
    String(b.company_name || ''), String(b.company_addr || ''),
    String(b.reg_number || ''), String(b.default_bank || ''), uid
  ).run();
  if (b.paylink !== undefined) {
    try { await env.DB.prepare('UPDATE users SET paylink=? WHERE id=?').bind(String(b.paylink || '').slice(0, 400), uid).run(); } catch (e) {}
  }
  if (b.auto_remind !== undefined) {
    try { await env.DB.prepare('UPDATE users SET auto_remind=? WHERE id=?').bind(b.auto_remind ? 1 : 0, uid).run(); } catch (e) {}
  }
  return json({ ok: true });
}

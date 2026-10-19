import { json, currentUserId } from '../_lib.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const user = await env.DB.prepare('SELECT id, email, company_name, company_addr, reg_number, default_bank, plan, invoice_seq FROM users WHERE id = ?').bind(uid).first();
  return json({ company: user });
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  await env.DB.prepare(
    'UPDATE users SET company_name = ?, company_addr = ?, reg_number = ?, default_bank = ? WHERE id = ?'
  ).bind(
    String(b.company_name || ''), String(b.company_addr || ''),
    String(b.reg_number || ''), String(b.default_bank || ''), uid
  ).run();
  return json({ ok: true });
}

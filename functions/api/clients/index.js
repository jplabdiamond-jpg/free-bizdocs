import { json, currentUserId, normalizeEmail } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  const { results } = await env.DB.prepare(
    'SELECT * FROM clients WHERE user_id = ? ORDER BY id'
  ).bind(uid).all();
  return json({ clients: results || [] });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const name = (b.name || '').trim();
  if (!name) return json({ error: '取引先名は必須です' }, 400);
  const r = await env.DB.prepare(
    'INSERT INTO clients (user_id, name, honorific, reg_number, address, default_bank, email) VALUES (?, ?, ?, ?, ?, ?, ?)'
  ).bind(uid, name, b.honorific || '御中', b.reg_number || '', b.address || '', b.default_bank || '', normalizeEmail(b.email || '')).run();
  return json({ ok: true, id: r.meta.last_row_id });
}

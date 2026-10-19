import { json, currentUserId } from '../../_lib.js';

export async function onRequestGet(context) {
  const { env, request, params } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const d = await env.DB.prepare('SELECT id, type, label, data, created_at FROM saved_docs WHERE id = ? AND user_id = ?').bind(params.id, uid).first();
  if (!d) return json({ error: 'not found' }, 404);
  let data = {};
  try { data = JSON.parse(d.data); } catch (e) {}
  return json({ id: d.id, type: d.type, label: d.label, created_at: d.created_at, data: data });
}

export async function onRequestPut(context) {
  const { env, request, params } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const own = await env.DB.prepare('SELECT id FROM saved_docs WHERE id = ? AND user_id = ?').bind(params.id, uid).first();
  if (!own) return json({ error: 'not found' }, 404);
  let body = {};
  try { body = await request.json(); } catch (e) {}
  const data = body && body.data != null ? JSON.stringify(body.data) : null;
  const label = body && typeof body.label === 'string' ? body.label : null;
  if (data == null && label == null) return json({ error: 'nothing to update' }, 400);
  if (data != null && label != null) {
    await env.DB.prepare('UPDATE saved_docs SET data = ?, label = ? WHERE id = ? AND user_id = ?').bind(data, label, params.id, uid).run();
  } else if (data != null) {
    await env.DB.prepare('UPDATE saved_docs SET data = ? WHERE id = ? AND user_id = ?').bind(data, params.id, uid).run();
  } else {
    await env.DB.prepare('UPDATE saved_docs SET label = ? WHERE id = ? AND user_id = ?').bind(label, params.id, uid).run();
  }
  return json({ ok: true, id: Number(params.id) });
}

export async function onRequestDelete(context) {
  const { env, request, params } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await env.DB.prepare('DELETE FROM saved_docs WHERE id = ? AND user_id = ?').bind(params.id, uid).run();
  return json({ ok: true });
}

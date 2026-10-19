import { json, currentUserId, FREE_DOC_LIMIT } from '../../_lib.js';

export var GENERIC_TYPES = { rirekisho:1, soufu:1, inkan:1, shokumu:1, taishoku:1, shiboudouki:1, entrysheet:1, skillsheet:1 };

async function totalSaved(env, uid) {
  const a = await env.DB.prepare('SELECT COUNT(*) AS n FROM documents WHERE user_id = ?').bind(uid).first();
  const b = await env.DB.prepare('SELECT COUNT(*) AS n FROM saved_docs WHERE user_id = ?').bind(uid).first();
  return ((a && a.n) || 0) + ((b && b.n) || 0);
}

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const url = new URL(request.url);
  const type = url.searchParams.get('type');
  let sql = 'SELECT id, type, label, created_at FROM saved_docs WHERE user_id = ?';
  const binds = [uid];
  if (type) { sql += ' AND type = ?'; binds.push(type); }
  sql += ' ORDER BY id DESC';
  const { results } = await env.DB.prepare(sql).bind(...binds).all();
  return json({ docs: results || [] });
}

export async function onRequestPost(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const type = GENERIC_TYPES[b.type] ? b.type : null;
  if (!type) return json({ error: '未対応の書類タイプです' }, 400);
  const data = b.data;
  if (!data || typeof data !== 'object') return json({ error: 'データが空です' }, 400);

  const u = await env.DB.prepare('SELECT plan FROM users WHERE id = ?').bind(uid).first();
  if (!(u && u.plan === 'pro')) {
    const n = await totalSaved(env, uid);
    if (n >= FREE_DOC_LIMIT) return json({ error: '無料プランで保存できる書類は' + FREE_DOC_LIMIT + '件までです。', upsell: true, limit: FREE_DOC_LIMIT }, 403);
  }
  const label = String(b.label || '').slice(0, 120);
  const r = await env.DB.prepare('INSERT INTO saved_docs (user_id, type, label, data) VALUES (?, ?, ?, ?)')
    .bind(uid, type, label, JSON.stringify(data)).run();
  return json({ ok: true, id: r.meta.last_row_id });
}

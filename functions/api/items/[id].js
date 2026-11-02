// ⑥ 品目マスタの削除。
import { json, currentUserId } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';

export async function onRequestDelete(context) {
  const { env, request, params } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  await env.DB.prepare('DELETE FROM items_master WHERE id=? AND user_id=?').bind(parseInt(params.id, 10), uid).run();
  return json({ ok: true });
}

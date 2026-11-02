import { json, currentUserId } from '../_lib.js';
import { ensureCols } from '../_schema.js';

export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  const user = await env.DB.prepare('SELECT id, email, company_name, company_addr, reg_number, default_bank, plan, invoice_seq, paylink, auto_remind, logo, seal, remind_before, remind_after, remind_msg FROM users WHERE id = ?').bind(uid).first();
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
  // ④ ロゴ・社印（dataURL）。空文字で削除可。上限2MBで安全側に。
  function okImg(s) { return typeof s === 'string' && (s === '' || (/^data:image\/(png|jpe?g|webp|gif);base64,/.test(s) && s.length < 2000000)); }
  if (b.logo !== undefined && okImg(b.logo)) { try { await env.DB.prepare('UPDATE users SET logo=? WHERE id=?').bind(b.logo || null, uid).run(); } catch (e) {} }
  if (b.seal !== undefined && okImg(b.seal)) { try { await env.DB.prepare('UPDATE users SET seal=? WHERE id=?').bind(b.seal || null, uid).run(); } catch (e) {} }
  // ⑦ リマインド設定（CSV日数・文面）
  function csvDays(s) { return String(s || '').split(',').map(function (x) { return parseInt(x, 10); }).filter(function (n) { return n >= 0 && n <= 180; }).slice(0, 8).join(','); }
  if (b.remind_before !== undefined) { try { await env.DB.prepare('UPDATE users SET remind_before=? WHERE id=?').bind(csvDays(b.remind_before), uid).run(); } catch (e) {} }
  if (b.remind_after !== undefined) { try { await env.DB.prepare('UPDATE users SET remind_after=? WHERE id=?').bind(csvDays(b.remind_after), uid).run(); } catch (e) {} }
  if (b.remind_msg !== undefined) { try { await env.DB.prepare('UPDATE users SET remind_msg=? WHERE id=?').bind(String(b.remind_msg || '').slice(0, 1000), uid).run(); } catch (e) {} }
  return json({ ok: true });
}

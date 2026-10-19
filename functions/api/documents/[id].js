import { json, currentUserId, calcTotals } from '../../_lib.js';

export async function onRequestGet(context) {
  const { env, params, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const id = params.id;
  const doc = await env.DB.prepare(
    `SELECT d.*, c.name AS client_name, c.honorific, c.reg_number AS client_reg, c.address AS client_address
     FROM documents d LEFT JOIN clients c ON c.id = d.client_id
     WHERE d.id = ? AND d.user_id = ?`
  ).bind(id, uid).first();
  if (!doc) return json({ error: 'not found' }, 404);
  const items = (await env.DB.prepare(
    'SELECT * FROM line_items WHERE document_id = ? ORDER BY sort_order'
  ).bind(id).all()).results || [];
  const payments = (await env.DB.prepare(
    'SELECT * FROM payments WHERE document_id = ? ORDER BY id'
  ).bind(id).all()).results || [];
  const user = await env.DB.prepare('SELECT id, email, company_name, company_addr, reg_number, default_bank FROM users WHERE id = ?').bind(uid).first();
  return json({ document: doc, items: items, payments: payments, company: user });
}

export async function onRequestPut(context) {
  const { env, params, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const id = params.id;
  const cur = await env.DB.prepare('SELECT * FROM documents WHERE id = ? AND user_id = ?').bind(id, uid).first();
  if (!cur) return json({ error: 'not found' }, 404);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const items = Array.isArray(b.items) ? b.items : [];
  if (!items.length) return json({ error: '明細が空です' }, 400);
  const status = b.status === 'draft' ? 'draft' : 'pending';

  // 自社情報（任意・受け取ったら更新）
  if (b.company && typeof b.company === 'object') {
    const u = await env.DB.prepare('SELECT company_name FROM users WHERE id = ?').bind(uid).first();
    await env.DB.prepare('UPDATE users SET company_name=?, company_addr=?, reg_number=?, default_bank=? WHERE id=?')
      .bind(String(b.company.company_name || (u && u.company_name) || ''), String(b.company.company_addr || ''),
            String(b.company.reg_number || ''), String(b.company.default_bank || ''), uid).run();
  }

  // 取引先: client_id 優先、無ければ client_name から find-or-create
  let clientId = b.client_id || cur.client_id || null;
  if (b.client_name && String(b.client_name).trim()) {
    const nm = String(b.client_name).trim();
    const ex = await env.DB.prepare('SELECT id FROM clients WHERE user_id=? AND name=?').bind(uid, nm).first();
    if (ex) clientId = ex.id;
    else {
      const ci = await env.DB.prepare('INSERT INTO clients (user_id, name, honorific) VALUES (?, ?, ?)')
        .bind(uid, nm, b.honorific || '御中').run();
      clientId = ci.meta.last_row_id;
    }
  }

  const c = calcTotals(items);
  // 番号は維持（編集で採番しない）。下書き→確定で番号未設定なら従来番号のまま。
  await env.DB.prepare(
    `UPDATE documents SET client_id=?, status=?, issue_date=?, due_date=?, subtotal=?, tax=?, withholding=?, total=?, payable=?, bank=?, notes=? WHERE id=? AND user_id=?`
  ).bind(
    clientId, status,
    b.issue_date || cur.issue_date, (b.due_date !== undefined ? b.due_date : cur.due_date),
    c.subtotal, c.tax, c.withholding, c.total, c.payable,
    (b.bank !== undefined ? b.bank : cur.bank), (b.notes !== undefined ? b.notes : cur.notes),
    id, uid
  ).run();

  // 明細を入れ替え
  const stmts = [env.DB.prepare('DELETE FROM line_items WHERE document_id = ?').bind(id)];
  items.forEach(function (it, i) {
    stmts.push(env.DB.prepare(
      'INSERT INTO line_items (document_id, name, qty, unit, unit_price, tax_rate, withholding, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    ).bind(id, it.name || '', Number(it.qty) || 0, it.unit || '',
      Math.round(Number(it.unit_price) || 0), Number(it.tax_rate) || 0,
      Number(it.withholding) === 1 ? 1 : 0, i));
  });
  await env.DB.batch(stmts);

  return json({ ok: true, id: Number(id), doc_no: cur.doc_no, type: cur.type, totals: c });
}

export async function onRequestDelete(context) {
  const { env, params, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  const id = params.id;
  const doc = await env.DB.prepare('SELECT id FROM documents WHERE id = ? AND user_id = ?').bind(id, uid).first();
  if (!doc) return json({ error: 'not found' }, 404);
  await env.DB.batch([
    env.DB.prepare('DELETE FROM line_items WHERE document_id = ?').bind(id),
    env.DB.prepare('DELETE FROM payments WHERE document_id = ?').bind(id),
    env.DB.prepare('DELETE FROM documents WHERE id = ? AND user_id = ?').bind(id, uid),
  ]);
  return json({ ok: true });
}

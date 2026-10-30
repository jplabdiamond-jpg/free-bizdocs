import { json, calcTotals, currentUserId, FREE_DOC_LIMIT, randToken, normalizeEmail } from '../../_lib.js';
import { ensureCols } from '../../_schema.js';

function pad4(n) { return ('000' + n).slice(-4); }
function today() { return new Date().toISOString().slice(0, 10); }

var TYPES = { invoice: 1, quote: 1, delivery: 1, po: 1, receipt: 1 };
var PREFIX = { quote: 'Q', delivery: 'DN', po: 'PO', receipt: 'RCT' };

// 一覧（?type=invoice&status=pending）
export async function onRequestGet(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  const url = new URL(request.url);
  const type = TYPES[url.searchParams.get('type')] ? url.searchParams.get('type') : 'invoice';
  const status = url.searchParams.get('status');
  let sql = `SELECT d.*, c.name AS client_name
             FROM documents d LEFT JOIN clients c ON c.id = d.client_id
             WHERE d.user_id = ? AND d.type = ?`;
  const binds = [uid, type];
  if (status === 'unpaid') {
    sql += " AND d.status IN ('pending','partial')";
  } else if (status && status !== 'all') {
    sql += ' AND d.status = ?'; binds.push(status);
  }
  sql += ' ORDER BY d.id DESC';
  const { results } = await env.DB.prepare(sql).bind(...binds).all();
  const t = today();
  const rows = (results || []).map(function (r) {
    r.overdue = (r.status === 'pending' || r.status === 'partial') && r.due_date && r.due_date < t;
    return r;
  });
  return json({ documents: rows });
}

// 作成（5書類タイプ対応・税計算・採番・無料は5件まで）
export async function onRequestPost(context) {
  const { env, request } = context;
  const uid = await currentUserId(request, env);
  if (!uid) return json({ error: 'unauthorized' }, 401);
  await ensureCols(env);
  let b = {};
  try { b = await request.json(); } catch (e) {}
  const type = TYPES[b.type] ? b.type : 'invoice';
  const status = b.status === 'draft' ? 'draft' : 'pending';
  const items = Array.isArray(b.items) ? b.items : [];
  if (!items.length) return json({ error: '明細が空です' }, 400);

  // 無料プランの保存上限
  const u = await env.DB.prepare('SELECT plan, invoice_seq, company_name FROM users WHERE id = ?').bind(uid).first();
  const isPro = u && u.plan === 'pro';
  if (!isPro) {
    const cd = await env.DB.prepare('SELECT COUNT(*) AS n FROM documents WHERE user_id = ?').bind(uid).first();
    const cs = await env.DB.prepare('SELECT COUNT(*) AS n FROM saved_docs WHERE user_id = ?').bind(uid).first();
    const total = ((cd && cd.n) || 0) + ((cs && cs.n) || 0);
    if (total >= FREE_DOC_LIMIT) {
      return json({ error: '無料プランで保存できる書類は' + FREE_DOC_LIMIT + '件までです。', upsell: true, limit: FREE_DOC_LIMIT }, 403);
    }
  }

  // 自社情報（任意・受け取ったら更新）。決済リンク(paylink)も既定として保存。
  if (b.company && typeof b.company === 'object') {
    await env.DB.prepare('UPDATE users SET company_name=?, company_addr=?, reg_number=?, default_bank=? WHERE id=?')
      .bind(String(b.company.company_name || u.company_name || ''), String(b.company.company_addr || ''),
            String(b.company.reg_number || ''), String(b.company.default_bank || ''), uid).run();
    if (b.company.paylink !== undefined) {
      try { await env.DB.prepare('UPDATE users SET paylink=? WHERE id=?').bind(String(b.company.paylink || '').slice(0, 400), uid).run(); } catch (e) {}
    }
  }

  const recipientEmail = normalizeEmail(b.recipient_email || '');
  const docPaylink = (b.paylink !== undefined) ? String(b.paylink || '').slice(0, 400)
    : (b.company && b.company.paylink !== undefined ? String(b.company.paylink || '').slice(0, 400) : '');

  // 取引先: client_id 優先、無ければ client_name から find-or-create。宛先メールがあれば取引先に保存。
  let clientId = b.client_id || null;
  if (!clientId && b.client_name && String(b.client_name).trim()) {
    const nm = String(b.client_name).trim();
    const ex = await env.DB.prepare('SELECT id FROM clients WHERE user_id=? AND name=?').bind(uid, nm).first();
    if (ex) clientId = ex.id;
    else {
      const ci = await env.DB.prepare('INSERT INTO clients (user_id, name, honorific, email) VALUES (?, ?, ?, ?)')
        .bind(uid, nm, b.honorific || '御中', recipientEmail).run();
      clientId = ci.meta.last_row_id;
    }
  }
  if (clientId && recipientEmail) {
    try { await env.DB.prepare('UPDATE clients SET email=? WHERE id=? AND user_id=?').bind(recipientEmail, clientId, uid).run(); } catch (e) {}
  }

  const c = calcTotals(items);

  // 採番（下書きは番号なし／タイプ別・ユーザー単位）
  let docNo = null;
  if (status !== 'draft') {
    const year = new Date().getFullYear();
    if (type === 'invoice') {
      await env.DB.prepare('UPDATE users SET invoice_seq = invoice_seq + 1 WHERE id = ?').bind(uid).run();
      const uu = await env.DB.prepare('SELECT invoice_seq FROM users WHERE id = ?').bind(uid).first();
      docNo = 'INV-' + year + '-' + pad4(uu.invoice_seq);
    } else {
      const q = await env.DB.prepare("SELECT COUNT(*) AS n FROM documents WHERE user_id = ? AND type = ? AND doc_no IS NOT NULL").bind(uid, type).first();
      docNo = PREFIX[type] + '-' + year + '-' + pad4((q.n || 0) + 1);
    }
  }

  // 確定（下書き以外）の請求書には公開リンク用トークンを発行。
  const shareToken = (status !== 'draft' && type === 'invoice') ? randToken() : null;

  const ins = await env.DB.prepare(
    `INSERT INTO documents
     (user_id, client_id, type, doc_no, status, issue_date, due_date, subtotal, tax, withholding, total, payable, bank, notes, source_doc_id, recipient_email, paylink, share_token)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).bind(
    uid, clientId, type, docNo, status,
    b.issue_date || today(), b.due_date || null,
    c.subtotal, c.tax, c.withholding, c.total, c.payable,
    b.bank || '', b.notes || '', b.source_doc_id || null,
    recipientEmail || null, docPaylink || null, shareToken
  ).run();
  const docId = ins.meta.last_row_id;

  const stmts = items.map(function (it, i) {
    return env.DB.prepare(
      'INSERT INTO line_items (document_id, name, qty, unit, unit_price, tax_rate, withholding, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    ).bind(docId, it.name || '', Number(it.qty) || 0, it.unit || '',
      Math.round(Number(it.unit_price) || 0), Number(it.tax_rate) || 0,
      Number(it.withholding) === 1 ? 1 : 0, i);
  });
  if (stmts.length) await env.DB.batch(stmts);

  return json({ ok: true, id: docId, doc_no: docNo, type: type, totals: c, share_token: shareToken });
}

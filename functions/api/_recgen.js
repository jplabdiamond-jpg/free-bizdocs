// 定期請求の共有ロジック: テーブル定義・日付計算・テンプレから請求書生成・期日到来分の自動生成。
import { calcTotals } from '../_lib.js';

export const RECURRING_DDL =
  'CREATE TABLE IF NOT EXISTS recurring (' +
  'id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, client_id INTEGER, ' +
  "title TEXT DEFAULT '', items_json TEXT NOT NULL, bank TEXT DEFAULT '', notes TEXT DEFAULT '', " +
  "cycle TEXT NOT NULL DEFAULT 'monthly', day_of_month INTEGER NOT NULL DEFAULT 1, " +
  'due_days INTEGER NOT NULL DEFAULT 30, ' +
  "mode TEXT NOT NULL DEFAULT 'auto', next_run TEXT, active INTEGER NOT NULL DEFAULT 1, " +
  'last_run TEXT, created_at TEXT NOT NULL DEFAULT (datetime(\'now\')))';

export async function ensureTable(env) { try { await env.DB.prepare(RECURRING_DDL).run(); } catch (e) {} }

function pad4(n) { return ('000' + n).slice(-4); }
function todayISO() { return new Date().toISOString().slice(0, 10); }
function addMonths(cycle) { return ({ monthly: 1, bimonthly: 2, quarterly: 3, halfyear: 6, yearly: 12 })[cycle] || 1; }
function clampDay(y, m, dom) { const last = new Date(Date.UTC(y, m + 1, 0)).getUTCDate(); return (dom >= 99 || dom > last) ? last : Math.max(1, dom); }
function ymd(y, m, d) { return new Date(Date.UTC(y, m, d)).toISOString().slice(0, 10); }
export function addDays(iso, n) { const d = new Date(iso + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + (Number(n) || 0)); return d.toISOString().slice(0, 10); }

// fromISO の次の発生日（cycle ヶ月後の day_of_month）
export function advanceRun(fromISO, cycle, dom) {
  const d = new Date(fromISO + 'T00:00:00Z');
  let y = d.getUTCFullYear(), m = d.getUTCMonth() + addMonths(cycle);
  y += Math.floor(m / 12); m = ((m % 12) + 12) % 12;
  return ymd(y, m, clampDay(y, m, dom));
}
// 新規登録時の初回生成日: 今月の dom が未来ならそれ、過ぎていれば来月の dom
export function initialNextRun(dom) {
  const now = new Date(); const t = now.toISOString().slice(0, 10);
  let y = now.getUTCFullYear(), m = now.getUTCMonth();
  let cand = ymd(y, m, clampDay(y, m, dom));
  if (cand < t) { m += 1; if (m > 11) { m = 0; y += 1; } cand = ymd(y, m, clampDay(y, m, dom)); }
  return cand;
}

async function createInvoiceFromTemplate(env, uid, t, items) {
  const c = calcTotals(items);
  const today = todayISO();
  const due = (t.due_days != null) ? addDays(today, t.due_days) : null;
  const status = (t.mode === 'draft') ? 'draft' : 'pending';
  let docNo = null;
  if (status !== 'draft') {
    await env.DB.prepare('UPDATE users SET invoice_seq = invoice_seq + 1 WHERE id = ?').bind(uid).run();
    const uu = await env.DB.prepare('SELECT invoice_seq FROM users WHERE id = ?').bind(uid).first();
    docNo = 'INV-' + new Date().getFullYear() + '-' + pad4((uu && uu.invoice_seq) || 1);
  }
  const ins = await env.DB.prepare(
    'INSERT INTO documents (user_id, client_id, type, doc_no, status, issue_date, due_date, subtotal, tax, withholding, total, payable, bank, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
  ).bind(uid, t.client_id || null, 'invoice', docNo, status, today, due,
    c.subtotal, c.tax, c.withholding, c.total, c.payable, t.bank || '', t.notes || '').run();
  const docId = ins.meta.last_row_id;
  const stmts = items.map(function (it, i) {
    return env.DB.prepare('INSERT INTO line_items (document_id, name, qty, unit, unit_price, tax_rate, withholding, sort_order) VALUES (?,?,?,?,?,?,?,?)')
      .bind(docId, it.name || '', Number(it.qty) || 0, it.unit || '', Math.round(Number(it.unit_price) || 0), Number(it.tax_rate) || 0, Number(it.withholding) === 1 ? 1 : 0, i);
  });
  if (stmts.length) await env.DB.batch(stmts);
  return { id: docId, doc_no: docNo };
}

// 期日到来分（next_run <= 今日）を1件ずつ生成し next_run を未来へ。生成件数を返す。
export async function generateDueForUser(env, uid) {
  try { await ensureTable(env); } catch (e) { return 0; }
  const today = todayISO();
  let rows = [];
  try { rows = (await env.DB.prepare('SELECT * FROM recurring WHERE user_id=? AND active=1 AND next_run IS NOT NULL AND next_run<=?').bind(uid, today).all()).results || []; }
  catch (e) { return 0; }
  let made = 0;
  for (const t of rows) {
    try {
      const items = JSON.parse(t.items_json || '[]');
      if (!items.length) continue;
      await createInvoiceFromTemplate(env, uid, t, items);
      let nr = t.next_run, guard = 0;
      do { nr = advanceRun(nr, t.cycle, t.day_of_month); guard++; } while (nr <= today && guard < 60);
      await env.DB.prepare('UPDATE recurring SET next_run=?, last_run=? WHERE id=?').bind(nr, today, t.id).run();
      made++;
    } catch (e) { /* 1件の失敗で全体を止めない */ }
  }
  return made;
}

-- 請求Hub スキーマ（Cloudflare D1 / SQLite）。金額はすべて整数（円）。
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT,
  company_name TEXT NOT NULL DEFAULT 'サンプルデザイン',
  company_addr TEXT DEFAULT '',
  reg_number TEXT DEFAULT '',          -- インボイス登録番号 T+13桁
  default_bank TEXT DEFAULT '',
  password_hash TEXT,
  pw_salt TEXT,
  plan TEXT NOT NULL DEFAULT 'free',          -- free / pro
  invoice_seq INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL DEFAULT 1,
  name TEXT NOT NULL,
  honorific TEXT NOT NULL DEFAULT '御中',
  reg_number TEXT DEFAULT '',
  address TEXT DEFAULT '',
  default_bank TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL DEFAULT 1,
  client_id INTEGER,
  type TEXT NOT NULL DEFAULT 'invoice',          -- invoice / quote / delivery
  doc_no TEXT,
  status TEXT NOT NULL DEFAULT 'pending',         -- draft / pending / partial / paid
  issue_date TEXT,
  due_date TEXT,
  subtotal INTEGER NOT NULL DEFAULT 0,            -- 税抜合計
  tax INTEGER NOT NULL DEFAULT 0,                 -- 消費税合計
  withholding INTEGER NOT NULL DEFAULT 0,         -- 源泉徴収税
  total INTEGER NOT NULL DEFAULT 0,               -- 税込合計
  payable INTEGER NOT NULL DEFAULT 0,             -- 差引請求額（total - withholding）
  paid_total INTEGER NOT NULL DEFAULT 0,          -- 入金済み累計
  bank TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  source_doc_id INTEGER,                          -- 見積→請求の変換元
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS line_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL,
  name TEXT NOT NULL DEFAULT '',
  qty REAL NOT NULL DEFAULT 1,
  unit TEXT DEFAULT '',
  unit_price INTEGER NOT NULL DEFAULT 0,
  tax_rate INTEGER NOT NULL DEFAULT 10,           -- 10 / 8 / 0
  withholding INTEGER NOT NULL DEFAULT 0,         -- 0/1 源泉対象
  sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL,
  paid_date TEXT,
  amount INTEGER NOT NULL DEFAULT 0,
  method TEXT DEFAULT '銀行振込',
  memo TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_docs_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_docs_client ON documents(client_id);
CREATE INDEX IF NOT EXISTS idx_items_doc ON line_items(document_id);
CREATE INDEX IF NOT EXISTS idx_pay_doc ON payments(document_id);

CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  body TEXT NOT NULL,
  ts INTEGER NOT NULL
);

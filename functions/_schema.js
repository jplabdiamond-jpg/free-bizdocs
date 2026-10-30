// オンライン請求書・自動送付/リマインド用のスキーマ拡張（Mac非依存）。
// 既存テーブルに列を追加。ALTER は冪等でないため try/catch で「既に存在」を無視。
// アイソレート内はモジュール変数でキャッシュし、初回のみ実行する。
let _done = false;

const ALTERS = [
  // 宛先メール（取引先マスタ・書類スナップショット）
  'ALTER TABLE clients ADD COLUMN email TEXT',
  'ALTER TABLE documents ADD COLUMN recipient_email TEXT',
  // 公開オンライン請求書リンク
  'ALTER TABLE documents ADD COLUMN share_token TEXT',
  // 決済リンク（書類ごとの上書き。無ければユーザー既定を使う）
  'ALTER TABLE documents ADD COLUMN paylink TEXT',
  // リマインド送信日（1日1回に絞るスロットル）と累計回数
  'ALTER TABLE documents ADD COLUMN last_reminder TEXT',
  'ALTER TABLE documents ADD COLUMN remind_count INTEGER NOT NULL DEFAULT 0',
  // 取引先が「支払いました」と報告した日時
  'ALTER TABLE documents ADD COLUMN payer_reported TEXT',
  // ユーザー既定の決済リンクと、未入金リマインドのオプトイン
  'ALTER TABLE users ADD COLUMN paylink TEXT',
  'ALTER TABLE users ADD COLUMN auto_remind INTEGER NOT NULL DEFAULT 0',
  // 定期請求: 生成時に宛先へオンライン請求書リンクを自動メールするか
  'ALTER TABLE recurring ADD COLUMN auto_send INTEGER NOT NULL DEFAULT 0',
];

export async function ensureCols(env) {
  if (_done || !env || !env.DB) return;
  for (const a of ALTERS) {
    try { await env.DB.prepare(a).run(); } catch (e) { /* 既存列は無視 */ }
  }
  _done = true;
}

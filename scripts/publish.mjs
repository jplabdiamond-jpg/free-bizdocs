#!/usr/bin/env node
/*
 * Free BizDoc クラウド自動公開スクリプト（GitHub Actions で実行）
 * - 1回の実行で最大1本公開。1日3本・各2時間以上・ランダム時刻スロット。
 * - 公開対象: CSV status「未」かつ img-src/<slug>.png あり かつ _drafts/<slug>.html あり。
 * - 画像は cwebp で webp 変換。本文を blog/ へ移動、blog.html 先頭にカード、sitemap 追加、CSV を済に更新。
 * - デプロイ/commit/IndexNow はワークフロー側で行う。本スクリプトは判定とファイル生成のみ。
 * - 結果を publish-result.json に出力（{published, slug, url, title, reason}）。
 */
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

const CSV = 'blog/eyecatch_titles.csv';
const BLOG_INDEX = 'blog.html';
const SITEMAP = 'sitemap.xml';
const STATE = 'blog/publish-state.json';
const DRAFTS = 'blog/_drafts';
const IMGSRC = 'blog/img-src';
const IMGOUT = 'blog/img';
const RESULT = 'publish-result.json';

const FORCE = (process.env.PUBLISH_MODE || '').trim() === 'force';
const MAX_PER_DAY = 3;
const MIN_GAP_SEC = 2 * 3600;

const nowEpoch = Math.floor(Date.now() / 1000);
const dj = new Date(Date.now() + 9 * 3600 * 1000); // JST
const today = dj.toISOString().slice(0, 10);
const nowMin = dj.getUTCHours() * 60 + dj.getUTCMinutes();
const jdateJP = `${dj.getUTCFullYear()}年${dj.getUTCMonth() + 1}月${dj.getUTCDate()}日`;

const writeResult = (o) => fs.writeFileSync(RESULT, JSON.stringify(o));
const saveState = (s) => fs.writeFileSync(STATE, JSON.stringify(s, null, 2) + '\n');
const randInt = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
function genSlots() {
  const s1 = 540 + randInt(0, 180);          // 09:00-12:00
  const s2 = Math.min(s1 + 120 + randInt(0, 120), 1320);
  const s3 = Math.min(s2 + 120 + randInt(0, 120), 1350);
  return [s1, s2, s3].sort((a, b) => a - b);
}

let state = { day: '', count: 0, lastEpoch: 0, slots: [] };
if (fs.existsSync(STATE)) { try { state = JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch {} }
if (state.day !== today) { state.day = today; state.count = 0; state.slots = genSlots(); }

// --- 公開可否判定 ---
if (state.count >= MAX_PER_DAY) { saveState(state); writeResult({ published: false, reason: 'daily-cap' }); process.exit(0); }
const due = FORCE ? state.count + 1 : state.slots.filter((m) => m <= nowMin).length;
if (state.count >= Math.min(due, MAX_PER_DAY)) { saveState(state); writeResult({ published: false, reason: 'not-due' }); process.exit(0); }
if (!FORCE && (nowEpoch - (state.lastEpoch || 0)) < MIN_GAP_SEC) { saveState(state); writeResult({ published: false, reason: 'gap' }); process.exit(0); }

// --- 公開対象を選ぶ（priority 昇順 = ファイル行順） ---
const lines = fs.readFileSync(CSV, 'utf8').split(/\r?\n/);
const header = lines[0];
const rows = lines.slice(1).filter((l) => l.trim());
let pickIdx = -1, pick = null;
for (let i = 0; i < rows.length; i++) {
  const c = rows[i].split(',');
  const [prio, cat, title, slug, tool, status] = c;
  if (status !== '未') continue;
  if (fs.existsSync(path.join('blog', slug + '.html'))) continue;      // 既に公開済みHTMLがあればスキップ（二重公開防止）
  if (!fs.existsSync(path.join(IMGSRC, slug + '.png'))) continue;      // 画像なしは公開しない
  if (!fs.existsSync(path.join(DRAFTS, slug + '.html'))) continue;     // 本文ドラフトなしは公開しない
  pickIdx = i; pick = { prio, cat, title, slug, tool }; break;
}
if (!pick) { saveState(state); writeResult({ published: false, reason: 'no-ready-article' }); process.exit(0); }

const slug = pick.slug;

// --- 画像 webp 変換 ---
execSync(`cwebp -q 82 "${IMGSRC}/${slug}.png" -o "${IMGOUT}/${slug}.webp"`, { stdio: 'inherit' });

// --- 本文: カード情報抽出・日付差し込み・blog/ へ移動 ---
let html = fs.readFileSync(path.join(DRAFTS, slug + '.html'), 'utf8');
let cardTag = pick.cat, cardH2 = pick.title, cardDesc = '';
const cm = html.match(/<!--CARD([\s\S]*?)-->/);
if (cm) {
  const g = (k) => { const m = cm[1].match(new RegExp(k + '\\s*=\\s*([^|]*?)\\s*(?:\\||$)', 'm')); return m ? m[1].trim() : ''; };
  cardTag = g('tag') || cardTag; cardH2 = g('h2') || cardH2; cardDesc = g('desc') || cardDesc;
}
html = html.replace(/__PUBDATE__/g, today).replace(/__PUBDATE_JP__/g, jdateJP);
fs.writeFileSync(path.join('blog', slug + '.html'), html);
fs.rmSync(path.join(DRAFTS, slug + '.html'));

// --- blog.html: 一覧先頭にカード追加 ---
let idx = fs.readFileSync(BLOG_INDEX, 'utf8');
const card = `<a class="bcard" href="/blog/${slug}"><img class="th" src="/blog/img/${slug}.webp" alt="" loading="lazy" width="400" height="225"><span class="tag">${cardTag}</span><h2>${cardH2}</h2><p>${cardDesc}…</p><time class="bdate">${today.replace(/-/g, '.')}</time></a>`;
idx = idx.replace(/<div class="blist">\s*\n?/, (m) => m + card + '\n');
fs.writeFileSync(BLOG_INDEX, idx);

// --- sitemap.xml: </urlset> の前に追加 ---
let sm = fs.readFileSync(SITEMAP, 'utf8');
const entry = `  <url><loc>https://free-bizdocs.com/blog/${slug}</loc><lastmod>${today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n`;
sm = sm.replace(/<\/urlset>/, entry + '</urlset>');
fs.writeFileSync(SITEMAP, sm);

// --- CSV: status を済に ---
const c = rows[pickIdx].split(','); c[5] = '済'; rows[pickIdx] = c.join(',');
fs.writeFileSync(CSV, [header, ...rows].join('\n') + '\n');

// --- 状態更新 ---
state.count += 1; state.lastEpoch = nowEpoch; saveState(state);

writeResult({ published: true, slug, url: `https://free-bizdocs.com/blog/${slug}`, title: cardH2 });
console.log('PUBLISHED', slug);

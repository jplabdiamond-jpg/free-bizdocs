#!/usr/bin/env node
/*
 * Free BizDoc 英語ブログ 自動公開スクリプト（GitHub Actions で実行）。
 * JA の scripts/publish.mjs と独立。EN 記事は画像不要（インラインヒーロー）。
 * - 公開対象: en/blog/_drafts/<slug>.html があり、en/blog/<slug>.html が未作成のもの。
 *   ファイル名（slug）昇順で1本選ぶ。先頭に <!--ENCARD tag=|h2=|desc=|c1=|c2=--> を期待。
 * - 公開処理: __PUBDATE__(ISO)/__PUBDATE_EN__(例 "Oct 19, 2026") を当日に置換し
 *   en/blog/<slug>.html へ移動、en/blog.html の #blist 先頭にカード、sitemap に追加。
 * - ペース: 1回最大1本 / 1日最大3本 / 各2時間以上 / ランダム時刻スロット（blog/publish-state-en.json）。
 * - 結果を publish-result-en.json に出力。デプロイ/commit/IndexNow はワークフロー側。
 */
import fs from 'node:fs';
import path from 'node:path';

const DRAFTS = 'en/blog/_drafts';
const BLOG_DIR = 'en/blog';
const BLOG_INDEX = 'en/blog.html';
const SITEMAP = 'sitemap.xml';
const STATE = 'blog/publish-state-en.json';
const RESULT = 'publish-result-en.json';

const FORCE = (process.env.PUBLISH_MODE || '').trim() === 'force';
const MAX_PER_DAY = 3;
const MIN_GAP_SEC = 2 * 3600;

const nowEpoch = Math.floor(Date.now() / 1000);
const dj = new Date(Date.now() + 9 * 3600 * 1000); // JST
const today = dj.toISOString().slice(0, 10);
const nowMin = dj.getUTCHours() * 60 + dj.getUTCMinutes();
const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const dEN = (() => { const [y, m, d] = today.split('-'); return `${MON[+m - 1]} ${+d}, ${y}`; })();

const writeResult = (o) => fs.writeFileSync(RESULT, JSON.stringify(o));
const saveState = (s) => fs.writeFileSync(STATE, JSON.stringify(s, null, 2) + '\n');
const randInt = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
function genSlots() {
  const s1 = 540 + randInt(0, 180);
  const s2 = Math.min(s1 + 120 + randInt(0, 120), 1320);
  const s3 = Math.min(s2 + 120 + randInt(0, 120), 1350);
  return [s1, s2, s3].sort((a, b) => a - b);
}

let state = { day: '', count: 0, lastEpoch: 0, slots: [] };
if (fs.existsSync(STATE)) { try { state = JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch {} }
if (state.day !== today) { state.day = today; state.count = 0; state.slots = genSlots(); }

if (state.count >= MAX_PER_DAY) { saveState(state); writeResult({ published: false, reason: 'daily-cap' }); process.exit(0); }
const due = FORCE ? state.count + 1 : state.slots.filter((m) => m <= nowMin).length;
if (state.count >= Math.min(due, MAX_PER_DAY)) { saveState(state); writeResult({ published: false, reason: 'not-due' }); process.exit(0); }
if (!FORCE && (nowEpoch - (state.lastEpoch || 0)) < MIN_GAP_SEC) { saveState(state); writeResult({ published: false, reason: 'gap' }); process.exit(0); }

// --- 公開対象（draft があり、公開済みHTMLが無いもの。slug 昇順で1本） ---
let drafts = [];
try { drafts = fs.readdirSync(DRAFTS).filter((f) => f.endsWith('.html')).sort(); } catch {}
let slug = null;
for (const f of drafts) {
  const s = f.replace(/\.html$/, '');
  if (fs.existsSync(path.join(BLOG_DIR, s + '.html'))) continue; // 二重公開防止
  slug = s; break;
}
if (!slug) { saveState(state); writeResult({ published: false, reason: 'no-ready-article' }); process.exit(0); }

// --- 本文: ENCARD 抽出・日付差し込み・移動 ---
let htmlDoc = fs.readFileSync(path.join(DRAFTS, slug + '.html'), 'utf8');
let tag = 'Guides', h2 = slug, desc = '', c1 = '#13263b', c2 = '#2f5a8a';
const cm = htmlDoc.match(/<!--ENCARD([\s\S]*?)-->/);
if (cm) {
  const g = (k) => { const m = cm[1].match(new RegExp(k + '\\s*=\\s*([^|]*?)\\s*(?:\\||$)', 'm')); return m ? m[1].trim() : ''; };
  tag = g('tag') || tag; h2 = g('h2') || h2; desc = g('desc') || desc; c1 = g('c1') || c1; c2 = g('c2') || c2;
}
htmlDoc = htmlDoc.replace(/__PUBDATE__/g, today).replace(/__PUBDATE_EN__/g, dEN);
fs.writeFileSync(path.join(BLOG_DIR, slug + '.html'), htmlDoc);
fs.rmSync(path.join(DRAFTS, slug + '.html'));

// --- en/blog.html: #blist 先頭にカード追加 ---
let idx = fs.readFileSync(BLOG_INDEX, 'utf8');
const card = `<a class="bcard" href="/en/blog/${slug}"><span class="cstripe" style="background:linear-gradient(120deg,${c1},${c2})"></span><span class="tag">${tag}</span><h2>${h2}</h2><p>${desc}</p><span class="go">Read &rarr;</span></a>`;
idx = idx.replace(/(<div class="bgrid" id="blist">)/, (m) => m + card);
fs.writeFileSync(BLOG_INDEX, idx);

// --- sitemap.xml: </urlset> の前に追加 ---
let sm = fs.readFileSync(SITEMAP, 'utf8');
const entry = `  <url><loc>https://free-bizdocs.com/en/blog/${slug}</loc><lastmod>${today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n`;
sm = sm.replace(/<\/urlset>/, entry + '</urlset>');
fs.writeFileSync(SITEMAP, sm);

state.count += 1; state.lastEpoch = nowEpoch; saveState(state);
writeResult({ published: true, slug, url: `https://free-bizdocs.com/en/blog/${slug}`, title: h2 });
console.log('PUBLISHED EN', slug);

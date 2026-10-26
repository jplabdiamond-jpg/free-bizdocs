#!/usr/bin/env node
/*
 * Free BizDoc 英語ブログ 自動公開スクリプト（GitHub Actions で実行）。
 * JA の scripts/publish.mjs と独立。EN 記事は画像不要（記事別 og:image 内蔵）。
 * - 公開対象: en/blog/_drafts/<slug>.html があり、en/blog/<slug>.html が未作成のもの。
 * - ペース: 1日最大3本 / ランダム時刻スロット。通常は1回1本（各2時間以上）。
 *   キャッチアップ: 定期実行が遅れている日は1回で不足分（最大3本）をまとめて公開。
 * - カテゴリ輪番で巡回。結果を publish-result-en.json に出力。
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

let state = { day: '', count: 0, lastEpoch: 0, slots: [], rot: 0, todayCats: [] };
if (fs.existsSync(STATE)) { try { state = JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch {} }
if (state.day !== today) { state.day = today; state.count = 0; state.slots = genSlots(); state.todayCats = []; }
if (typeof state.rot !== 'number') state.rot = 0;
if (!Array.isArray(state.todayCats)) state.todayCats = [];

// --- 不足分（toPublish） ---
const due = state.slots.filter((m) => m <= nowMin).length;
const target = FORCE ? state.count + 1 : Math.min(due, MAX_PER_DAY);
const toPublish = Math.min(target, MAX_PER_DAY) - state.count;
if (toPublish <= 0) { saveState(state); writeResult({ published: false, reason: state.count >= MAX_PER_DAY ? 'daily-cap' : 'not-due' }); process.exit(0); }
if (!FORCE && toPublish === 1 && (nowEpoch - (state.lastEpoch || 0)) < MIN_GAP_SEC) {
  saveState(state); writeResult({ published: false, reason: 'gap' }); process.exit(0);
}

const CATS = ['Invoicing', 'Getting paid', 'Quoting', 'Tax', 'Purchasing', 'Industries'];
function draftCat(s) {
  try {
    const h = fs.readFileSync(path.join(DRAFTS, s + '.html'), 'utf8');
    const cm = h.match(/<!--ENCARD([\s\S]*?)-->/);
    if (cm) { const m = cm[1].match(/tag\s*=\s*([^|]*?)\s*(?:\||$)/m); if (m && m[1].trim()) return m[1].trim(); }
  } catch {}
  return 'Guides';
}
function selectSlug() {
  let allDrafts = [];
  try { allDrafts = fs.readdirSync(DRAFTS).filter((f) => f.endsWith('.html')).map((f) => f.replace(/\.html$/, '')).sort(); } catch {}
  const avail = {};
  for (const s of allDrafts) {
    if (fs.existsSync(path.join(BLOG_DIR, s + '.html'))) continue;
    (avail[draftCat(s)] = avail[draftCat(s)] || []).push(s);
  }
  const extra = Object.keys(avail).filter((c) => !CATS.includes(c) && avail[c].length);
  let pickCat = null, step = 0;
  const rot = ((state.rot % CATS.length) + CATS.length) % CATS.length;
  for (let i = 0; i < CATS.length; i++) { const c = CATS[(rot + i) % CATS.length]; if ((avail[c] || []).length && !state.todayCats.includes(c)) { pickCat = c; step = i + 1; break; } }
  if (!pickCat) { for (let i = 0; i < CATS.length; i++) { const c = CATS[(rot + i) % CATS.length]; if ((avail[c] || []).length) { pickCat = c; step = i + 1; break; } } }
  if (!pickCat && extra.length) { pickCat = extra[0]; step = 1; }
  if (!pickCat) return null;
  const slug = avail[pickCat][0];
  state.rot = (((state.rot % CATS.length) + CATS.length) % CATS.length + step) % CATS.length;
  state.todayCats.push(pickCat);
  return slug;
}

function publishOne(slug) {
  let htmlDoc = fs.readFileSync(path.join(DRAFTS, slug + '.html'), 'utf8');
  let tag = 'Guides', h2 = slug, desc = '';
  const cm = htmlDoc.match(/<!--ENCARD([\s\S]*?)-->/);
  if (cm) {
    const g = (k) => { const m = cm[1].match(new RegExp(k + '\\s*=\\s*([^|]*?)\\s*(?:\\||$)', 'm')); return m ? m[1].trim() : ''; };
    tag = g('tag') || tag; h2 = g('h2') || h2; desc = g('desc') || desc;
  }
  htmlDoc = htmlDoc.replace(/__PUBDATE__/g, today).replace(/__PUBDATE_EN__/g, dEN);
  fs.writeFileSync(path.join(BLOG_DIR, slug + '.html'), htmlDoc);
  fs.rmSync(path.join(DRAFTS, slug + '.html'));
  let idx = fs.readFileSync(BLOG_INDEX, 'utf8');
  const card = `<a class="bcard" href="/en/blog/${slug}"><span class="bthumb"><img src="/en/blog/og/${slug}.jpg" alt="" loading="lazy" width="1200" height="630"></span><span class="bbody"><span class="tag">${tag}</span><h2>${h2}</h2><p>${desc}</p><span class="go">Read &rarr;</span></span></a>`;
  idx = idx.replace(/(<div class="bgrid" id="blist">)/, (m) => m + card);
  fs.writeFileSync(BLOG_INDEX, idx);
  let sm = fs.readFileSync(SITEMAP, 'utf8');
  const entry = `  <url><loc>https://free-bizdocs.com/en/blog/${slug}</loc><lastmod>${today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n`;
  sm = sm.replace(/<\/urlset>/, entry + '</urlset>');
  fs.writeFileSync(SITEMAP, sm);
}

const published = [];
for (let k = 0; k < toPublish; k++) {
  const slug = selectSlug();
  if (!slug) break;
  publishOne(slug);
  published.push(slug);
}

if (published.length === 0) { saveState(state); writeResult({ published: false, reason: 'no-ready-article' }); process.exit(0); }

state.count += published.length;
state.lastEpoch = nowEpoch;
saveState(state);
writeResult({ published: true, count: published.length, slugs: published, slug: published[0] });
console.log('PUBLISHED EN', published.join(' '));

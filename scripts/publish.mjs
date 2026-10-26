#!/usr/bin/env node
/*
 * Free BizDoc クラウド自動公開スクリプト（GitHub Actions で実行）
 * - 1日3本・ランダム時刻スロット。通常は1回1本（各2時間以上あける）。
 * - キャッチアップ: GitHubの定期実行が間引かれ遅れている日は、1回の実行で不足分（最大3本まで）をまとめて公開する。
 * - 公開対象: CSV status「未」かつ _drafts/<slug>.html あり（画像はバンクがあればwebp変換、無ければ自動生成）。
 * - デプロイ/commit/IndexNow はワークフロー側。本スクリプトは判定とファイル生成のみ。
 * - 結果を publish-result.json に出力（{published, count, slugs:[...], slug, reason}）。
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
  const s1 = 540 + randInt(0, 180);
  const s2 = Math.min(s1 + 120 + randInt(0, 120), 1320);
  const s3 = Math.min(s2 + 120 + randInt(0, 120), 1350);
  return [s1, s2, s3].sort((a, b) => a - b);
}

let state = { day: '', count: 0, lastEpoch: 0, slots: [] };
if (fs.existsSync(STATE)) { try { state = JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch {} }
if (state.day !== today) { state.day = today; state.count = 0; state.slots = genSlots(); }

// --- 何本公開すべきか（target）と不足分（toPublish）---
const due = state.slots.filter((m) => m <= nowMin).length;              // 今の時刻までに来たスロット数
let target = FORCE ? state.count + 1 : Math.min(due, MAX_PER_DAY);
let toPublish = Math.min(target, MAX_PER_DAY) - state.count;
if (toPublish <= 0) { saveState(state); writeResult({ published: false, reason: state.count >= MAX_PER_DAY ? 'daily-cap' : 'not-due' }); process.exit(0); }
// 丁度1本（オンスケジュール）の時だけ2時間間隔を守る。2本以上（遅れ）はキャッチアップで間隔を無視。
if (!FORCE && toPublish === 1 && (nowEpoch - (state.lastEpoch || 0)) < MIN_GAP_SEC) {
  saveState(state); writeResult({ published: false, reason: 'gap' }); process.exit(0);
}

// --- CSV ---
const lines = fs.readFileSync(CSV, 'utf8').split(/\r?\n/);
const header = lines[0];
const rows = lines.slice(1).filter((l) => l.trim());

function findNext() {
  for (let i = 0; i < rows.length; i++) {
    const c = rows[i].split(',');
    const [prio, cat, title, slug, tool, status] = c;
    if (status !== '未') continue;
    if (fs.existsSync(path.join('blog', slug + '.html'))) continue;   // 公開済みHTMLあり→スキップ
    if (!fs.existsSync(path.join(DRAFTS, slug + '.html'))) continue;  // 本文ドラフトなし→スキップ
    return { i, prio, cat, title, slug, tool };
  }
  return null;
}

function publishOne(pick) {
  const slug = pick.slug;
  let html = fs.readFileSync(path.join(DRAFTS, slug + '.html'), 'utf8');
  let cardTag = pick.cat, cardH2 = pick.title, cardDesc = '', styleJson = '';
  const cm = html.match(/<!--CARD([\s\S]*?)-->/);
  if (cm) {
    const g = (k) => { const m = cm[1].match(new RegExp(k + '\\s*=\\s*([^|]*?)\\s*(?:\\||$)', 'm')); return m ? m[1].trim() : ''; };
    cardTag = g('tag') || cardTag; cardH2 = g('h2') || cardH2; cardDesc = g('desc') || cardDesc;
    const style = {};
    const tcolor = g('tcolor'); if (tcolor) style.colors = tcolor.split(',').map((s) => s.trim());
    const tweight = g('tweight'); if (tweight) style.weight = parseInt(tweight, 10);
    const tscale = g('tscale'); if (tscale) style.scale = parseFloat(tscale);
    const fontk = g('font'); if (fontk) style.font = fontk;
    const pill = g('pill'); if (pill) style.pill = pill;
    const emph = g('emph'); if (emph) style.emph = emph;
    const emphcolor = g('emphcolor'); if (emphcolor) style.emphcolor = emphcolor;
    const en = g('en'); if (en) style.en = en;
    if (Object.keys(style).length) styleJson = JSON.stringify(style);
  }
  // 画像
  if (fs.existsSync(path.join(IMGSRC, slug + '.png'))) {
    execSync(`cwebp -q 82 "${IMGSRC}/${slug}.png" -o "${IMGOUT}/${slug}.webp"`, { stdio: 'inherit' });
  } else {
    const a = [slug, pick.title, pick.cat, IMGOUT + '/' + slug + '.webp'];
    if (styleJson) a.push(styleJson);
    execSync('python3 scripts/gen-eyecatch.py ' + a.map((s) => JSON.stringify(s)).join(' '), { stdio: 'inherit' });
  }
  // 本文 → blog/
  html = html.replace(/__PUBDATE__/g, today).replace(/__PUBDATE_JP__/g, jdateJP);
  fs.writeFileSync(path.join('blog', slug + '.html'), html);
  fs.rmSync(path.join(DRAFTS, slug + '.html'));
  // 一覧カード
  let idx = fs.readFileSync(BLOG_INDEX, 'utf8');
  const card = `<a class="bcard" href="/blog/${slug}"><img class="th" src="/blog/img/${slug}.webp" alt="" loading="lazy" width="400" height="225"><span class="tag">${cardTag}</span><h2>${cardH2}</h2><p>${cardDesc}…</p><time class="bdate">${today.replace(/-/g, '.')}</time></a>`;
  idx = idx.replace(/<div class="blist">\s*\n?/, (m) => m + card + '\n');
  fs.writeFileSync(BLOG_INDEX, idx);
  // sitemap
  let sm = fs.readFileSync(SITEMAP, 'utf8');
  const entry = `  <url><loc>https://free-bizdocs.com/blog/${slug}</loc><lastmod>${today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n`;
  sm = sm.replace(/<\/urlset>/, entry + '</urlset>');
  fs.writeFileSync(SITEMAP, sm);
  // CSV（メモリ上で済に）
  const c = rows[pick.i].split(','); c[5] = '済'; rows[pick.i] = c.join(',');
  return slug;
}

const published = [];
for (let k = 0; k < toPublish; k++) {
  const pick = findNext();
  if (!pick) break;
  published.push(publishOne(pick));
}

if (published.length === 0) { saveState(state); writeResult({ published: false, reason: 'no-ready-article' }); process.exit(0); }

fs.writeFileSync(CSV, [header, ...rows].join('\n') + '\n');
state.count += published.length;
state.lastEpoch = nowEpoch;
saveState(state);
writeResult({ published: true, count: published.length, slugs: published, slug: published[0] });
console.log('PUBLISHED', published.join(' '));

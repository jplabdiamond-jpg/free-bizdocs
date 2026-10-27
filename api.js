// 共通: API通信・整形・税計算・PDF生成
window.API = (function () {
  async function req(path, method, body) {
    var opt = { method: method || 'GET', headers: {} };
    if (body !== undefined) { opt.headers['content-type'] = 'application/json'; opt.body = JSON.stringify(body); }
    var r = await fetch(path, opt);
    if (r.status === 401) { location.href = '/login'; throw new Error('unauthorized'); }
    var j = await r.json().catch(function () { return {}; });
    if (!r.ok) { var e = new Error(j.error || ('HTTP ' + r.status)); e.status = r.status; e.data = j; throw e; }
    return j;
  }
  function yen(n) { return '¥' + (Math.round(Number(n) || 0)).toLocaleString('ja-JP'); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }

  // 埋め込みフォントに無い記号を、同義の収録済み文字へ簡易変換（PDF描画用）
  var GLYPH_SUB = { '○': '〇', '◯': '〇', '●': '〇', '△': '〇', '▲': '〇', '▽': '〇', '□': '〇', '■': '〇', '◇': '〇', '◆': '〇', '※': '*', '℡': 'TEL', '～': '~', '★': '*', '☆': '*' };
  // ---- カラーテーマ（モノクロ＋5色）----
  var THEME_DEFS = {
    mono:   { ac: [0.12, 0.12, 0.13], head: [0.15, 0.15, 0.16], band: [0.93, 0.93, 0.93], zebra: [0.955, 0.955, 0.955] },
    blue:   { ac: [0.09, 0.40, 0.90], head: [0.11, 0.20, 0.40], band: [0.92, 0.95, 0.99], zebra: [0.96, 0.975, 0.995] },
    red:    { ac: [0.80, 0.16, 0.18], head: [0.36, 0.10, 0.11], band: [0.99, 0.94, 0.94], zebra: [0.995, 0.97, 0.97] },
    green:  { ac: [0.09, 0.50, 0.33], head: [0.08, 0.28, 0.20], band: [0.92, 0.98, 0.95], zebra: [0.96, 0.99, 0.975] },
    purple: { ac: [0.42, 0.22, 0.68], head: [0.22, 0.13, 0.36], band: [0.96, 0.94, 0.99], zebra: [0.975, 0.965, 0.995] },
    orange: { ac: [0.88, 0.46, 0.08], head: [0.45, 0.25, 0.05], band: [0.99, 0.95, 0.90], zebra: [0.995, 0.975, 0.95] }
  };
  function themeCols(name) {
    var P = window.PDFLib, rgb = P.rgb, d = THEME_DEFS[name] || THEME_DEFS.mono, b = d.ac;
    function mw(p) { return [b[0]*p + (1-p), b[1]*p + (1-p), b[2]*p + (1-p)]; } // 淡い背景（白寄せ）
    function dk(p) { return [b[0]*p, b[1]*p, b[2]*p]; }                        // 濃い線・文字（黒寄せ）
    var a = dk(0.82), hd = mw(0.12), bd = mw(0.09), zb = mw(0.045);
    return {
      ink: rgb(0.1, 0.1, 0.12), mut: rgb(0.42, 0.42, 0.42), line: rgb(0.72, 0.72, 0.72),
      ac: rgb(a[0], a[1], a[2]), head: rgb(hd[0], hd[1], hd[2]),
      band: rgb(bd[0], bd[1], bd[2]), zebra: rgb(zb[0], zb[1], zb[2]),
      mono: (name === 'mono' || !name)
    };
  }
  function sani(s) { return String(s == null ? '' : s).replace(/[○◯●△▲▽□■◇◆※℡～★☆]/g, function (c) { return GLYPH_SUB[c]; }); }

  // ---- 画像（ロゴ・印影）埋め込み共通 ----
  function _durlToBytes(durl) { var i = durl.indexOf(','); var bin = atob(durl.slice(i + 1)); var u = new Uint8Array(bin.length); for (var k = 0; k < bin.length; k++) u[k] = bin.charCodeAt(k); return { bytes: u, png: /image\/png/i.test(durl.slice(0, i)) }; }
  async function _embedImg(pdf, durl) { if (!durl || typeof durl !== 'string' || durl.indexOf('data:') !== 0) return null; try { var d = _durlToBytes(durl); return d.png ? await pdf.embedPng(d.bytes) : await pdf.embedJpg(d.bytes); } catch (e) { return null; } }
  function _fit(img, maxW, maxH) { var sc = Math.min(maxW / img.width, maxH / img.height); return { w: img.width * sc, h: img.height * sc }; }

  // 書類タイプ定義（請求書/見積書/納品書/発注書/領収書）
  // t:表題 en:英字 num:番号ラベル amount:金額ボックス total:合計ラベル
  // due:支払期限を出す wh:源泉徴収を出す bank:振込先を出す receipt:領収書特有要素
  var KINDS = {
    invoice:  { t: '請求書', en: 'INVOICE',        num: '請求書番号', amount: 'ご請求金額（税込）', total: '差引ご請求額', due: true,  wh: true,  bank: true,  receipt: false },
    quote:    { t: '見積書', en: 'QUOTE',          num: '見積番号',   amount: 'お見積金額（税込）', total: '合計（税込）',   due: false, wh: false, bank: false, receipt: false },
    delivery: { t: '納品書', en: 'DELIVERY NOTE',  num: '納品書番号', amount: '納品金額（税込）',   total: '合計（税込）',   due: false, wh: false, bank: false, receipt: false },
    po:       { t: '発注書', en: 'PURCHASE ORDER', num: '発注番号',   amount: 'ご発注金額（税込）', total: '合計（税込）',   due: false, wh: false, bank: false, receipt: false },
    receipt:  { t: '領収書', en: 'RECEIPT',        num: '領収書番号', amount: '領収金額（税込）',   total: '合計（税込）',   due: false, wh: false, bank: false, receipt: true }
  };
  function kindCfg(kind) { return KINDS[kind] || KINDS.invoice; }

  // 税計算（サーバーと同一ロジック）
  function calc(items) {
    var sub10 = 0, sub8 = 0, sub0 = 0, whBase = 0, subtotal = 0;
    (items || []).forEach(function (it) {
      var qty = Number(it.qty) || 0, price = Math.round(Number(it.unit_price) || 0);
      var amount = Math.round(qty * price), rate = Number(it.tax_rate);
      if (rate === 10) sub10 += amount; else if (rate === 8) sub8 += amount; else sub0 += amount;
      if (Number(it.withholding) === 1) whBase += amount;
      subtotal += amount;
    });
    var tax10 = Math.floor(sub10 * 0.10), tax8 = Math.floor(sub8 * 0.08), tax = tax10 + tax8;
    var withholding = 0;
    if (whBase > 0) withholding = whBase <= 1000000 ? Math.floor(whBase * 0.1021) : Math.floor((whBase - 1000000) * 0.2042) + 102100;
    var total = subtotal + tax;
    return { sub10: sub10, sub8: sub8, sub0: sub0, tax10: tax10, tax8: tax8, tax: tax, subtotal: subtotal, withholding: withholding, total: total, payable: total - withholding };
  }

  // ---- PDF生成 ----
  var _libReady = null, _fontBytes = null;
  function loadScript(src) {
    return new Promise(function (res, rej) {
      var s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = function () { rej(new Error('load fail ' + src)); };
      document.head.appendChild(s);
    });
  }
  async function ensureLib() {
    if (_libReady) return _libReady;
    _libReady = (async function () {
      if (!window.PDFLib) await loadScript('https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js');
      if (!window.fontkit) await loadScript('https://cdn.jsdelivr.net/npm/@pdf-lib/fontkit@1.1.1/dist/fontkit.umd.min.js');
      if (!_fontBytes) _fontBytes = await fetch('/fonts/noto-jp.ttf', { cache: 'force-cache' }).then(function (r) { return r.arrayBuffer(); });
    })();
    return _libReady;
  }
  // ---- 出力の受け渡し（通常=ダウンロード／プレビュー時=PDFデータを横取り）----
  var _cap = null, _pvRun = null, _dl = 0, _pvMode = false;
  function _deliver(url, blob, name) {
    if (_cap) { var f = _cap; _cap = null; f(blob); return; }
    var a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
  }
  // ダウンロード実行中はプレビューを止め、プレビュー生成中ならその完了を待つ
  function _guardDl(fn) {
    return async function () {
      _dl++; try { if (_pvRun) { try { await _pvRun; } catch (e) {} } return await fn.apply(this, arguments); } finally { _dl--; }
    };
  }
  var _pdfjsP = null;
  function ensurePdfjs() {
    if (_pdfjsP) return _pdfjsP;
    _pdfjsP = (async function () {
      if (!window.pdfjsLib) await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js');
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    })();
    return _pdfjsP;
  }
  // host: 描画先要素 / gen: 実際のPDF生成関数を呼ぶ関数（例: function(){ return API.resignPdf(buildData()); }）
  function livePreview(host, gen, opt) {
    opt = opt || {};
    var maxPages = opt.maxPages || 3, timer = null, again = false, seq = 0;
    host.classList.add('livepv');
    if (!host.querySelector('.livepv-st')) host.insertAdjacentHTML('beforeend', '<div class="livepv-pages"></div><div class="livepv-st">プレビューを作成中…</div>');
    var pagesEl = host.querySelector('.livepv-pages'), st = host.querySelector('.livepv-st');
    async function run() {
      if (_dl) { schedule(); return; }
      if (_pvRun) { again = true; return; }
      var my = ++seq;
      st.style.opacity = '1';
      var p = (async function () {
        var blob = await new Promise(function (res, rej) {
          _cap = res; _pvMode = true;
          Promise.resolve().then(gen).then(function () { _pvMode = false; if (_cap === res) { _cap = null; res(null); } }).catch(function (e) { _pvMode = false; if (_cap === res) _cap = null; rej(e); });
        });
        if (!blob) return;
        await ensurePdfjs();
        var buf = await blob.arrayBuffer();
        var doc = await window.pdfjsLib.getDocument({ data: buf }).promise;
        var n = Math.min(doc.numPages, maxPages), frag = document.createDocumentFragment();
        var cw = Math.max(200, pagesEl.clientWidth || host.clientWidth || 360);
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        for (var i = 1; i <= n; i++) {
          var pg = await doc.getPage(i);
          var vp0 = pg.getViewport({ scale: 1 });
          var vp = pg.getViewport({ scale: (cw / vp0.width) * dpr });
          var cv = document.createElement('canvas'); cv.width = Math.floor(vp.width); cv.height = Math.floor(vp.height);
          cv.className = 'livepv-page';
          var cx = cv.getContext('2d'); cx.fillStyle = '#fff'; cx.fillRect(0, 0, cv.width, cv.height);
          await pg.render({ canvasContext: cx, viewport: vp, intent: 'print' }).promise;
          frag.appendChild(cv);
        }
        if (doc.numPages > n) { var more = document.createElement('div'); more.className = 'livepv-more'; more.textContent = '…ほか ' + (doc.numPages - n) + ' ページ'; frag.appendChild(more); }
        if (my === seq) { pagesEl.innerHTML = ''; pagesEl.appendChild(frag); }
      })();
      _pvRun = p;
      try { await p; } catch (e) { st.textContent = 'プレビューを作成できませんでした'; }
      finally { _pvRun = null; st.style.opacity = '0'; st.textContent = 'プレビューを更新中…'; if (again) { again = false; schedule(); } }
    }
    function schedule() { clearTimeout(timer); timer = setTimeout(run, opt.delay || 700); }
    if (!document.getElementById('livepv-css')) {
      var css = document.createElement('style'); css.id = 'livepv-css';
      css.textContent = '.livepv{position:relative;background:linear-gradient(180deg,#eef2f8,#e4ebf5);border:1px solid #dbe4f0;border-radius:12px;padding:14px;min-height:220px}'
        + '.livepv-pages{display:flex;flex-direction:column;gap:12px}'
        + '.livepv-page{display:block;width:100%;height:auto;background:#fff;box-shadow:0 12px 30px -16px rgba(19,38,59,.4);border:1px solid #d5deea}'
        + '.livepv-st{position:absolute;top:10px;right:12px;font-size:11px;font-weight:700;color:#5a6b7d;background:rgba(255,255,255,.92);border:1px solid #dbe4f0;border-radius:999px;padding:4px 10px;transition:opacity .2s;pointer-events:none}'
        + '.livepv-more{text-align:center;font-size:12px;color:#5a6b7d;font-weight:700}';
      document.head.appendChild(css);
    }
    // 初回プレビューはブラウザのアイドル時に実行し、pdf-lib と日本語フォント(約2.7MB)の
    // 取得を初期表示のクリティカルパスから外す（表示/操作可能までを高速化）。
    if ('requestIdleCallback' in window) { try { requestIdleCallback(function () { schedule(); }, { timeout: 2600 }); } catch (e) { schedule(); } }
    else { setTimeout(schedule, 1400); }
    return schedule;
  }
  // doc: {doc_no, issue_date, due_date, client_name, honorific, client_address, bank, notes, payable}
  // items: [{name, qty, unit, unit_price, tax_rate, withholding}]  co: {company_name, reg_number, company_addr, email, default_bank}
  async function render(doc, items, co, kind, theme) {
    await ensureLib();
    items = items || []; co = co || {};
    var K = kindCfg(kind);
    var c = calc(items);
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var page = pdf.addPage([595.28, 841.89]);
    var W = 595.28, M = 48;
    var T = themeCols(theme); var ink = T.ink, muted = T.mut, ac = T.ac, line = T.line, zebra = T.zebra, head = T.head, band = T.band;
    var yen2 = function (n) { return '¥' + (Math.round(Number(n) || 0)).toLocaleString('ja-JP'); };
    var tw = function (s, sz) { return font.widthOfTextAtSize(sani(s), sz); };
    var dr = function (s, x, y, sz, col) { page.drawText(sani(s), { x: x, y: y, size: sz, font: font, color: col || ink }); };
    var drR = function (s, xr, y, sz, col) { s = sani(s); page.drawText(s, { x: xr - font.widthOfTextAtSize(s, sz), y: y, size: sz, font: font, color: col || ink }); };
    var ell = function (s, sz, max) { s = sani(s); if (tw(s, sz) <= max) return s; while (s.length > 1 && tw(s + '…', sz) > max) s = s.slice(0, -1); return s + '…'; };
    var payable = K.wh ? c.payable : c.total;
    var y = 841.89 - M;
    dr(K.t, M, y - 22, 26, ink); dr(K.en, M + 104, y - 20, 10, ac);
    drR(K.num + ' : ' + (doc.doc_no || '—'), W - M, y - 4, 9, muted);
    drR('発行日 : ' + (doc.issue_date || ''), W - M, y - 18, 9, muted);
    if (K.due) drR('支払期限 : ' + (doc.due_date || '—'), W - M, y - 32, 9, muted);
    y -= 52; page.drawLine({ start: { x: M, y: y }, end: { x: W - M, y: y }, thickness: 1.5, color: ac }); y -= 26;
    var rx = 330;
    dr(ell((doc.client_name || '') + '　' + (doc.honorific || '御中'), 13, rx - M - 20), M, y, 13, ink); y -= 16;
    dr(ell(doc.client_address || '', 9, rx - M - 20), M, y, 9, muted);
    var yr = y + 16;
    var _lg = await _embedImg(pdf, co.logo), _sl = await _embedImg(pdf, co.seal);
    if (_lg) { var _lf = _fit(_lg, 130, 22); page.drawImage(_lg, { x: W - M - _lf.w, y: yr + 8, width: _lf.w, height: _lf.h }); }
    if (_sl) { var _sf = _fit(_sl, 42, 42); page.drawImage(_sl, { x: W - M - _sf.w, y: yr - 32, width: _sf.w, height: _sf.h }); }
    var rw = W - M - rx - (_sl ? 48 : 0);
    dr(ell(co.company_name || '', 11, rw), rx, yr, 11, ink); yr -= 13;
    if (co.reg_number) { dr(ell('登録番号 : ' + co.reg_number, 9, rw), rx, yr, 9, ac); yr -= 13; }
    dr(ell(co.company_addr || '', 8.5, rw), rx, yr, 8.5, muted); yr -= 12;
    dr(ell(co.email || '', 8.5, rw), rx, yr, 8.5, muted);
    y -= 26;
    page.drawRectangle({ x: M, y: y - 40, width: W - 2 * M, height: 40, color: band });
    dr(K.amount, M + 14, y - 26, 11, ink); drR(yen2(payable), W - M - 14, y - 28, 18, ac);
    y -= 60;
    if (K.receipt) { dr('上記正に領収いたしました。', M, y, 10, ink); y -= 22; }
    var cName = M, cQty = 360, cUnit = 398, cPrice = 452, cAmt = W - M;
    page.drawRectangle({ x: M, y: y - 22, width: W - 2 * M, height: 22, color: head });
    dr('品目・摘要', cName + 8, y - 15, 9, ink); drR('数量', cQty + 24, y - 15, 9, ink);
    dr('単位', cUnit, y - 15, 9, ink); drR('単価', cPrice + 42, y - 15, 9, ink); drR('金額', cAmt - 6, y - 15, 9, ink);
    y -= 22;
    var _items = items || [], _max = Math.max(1, Math.floor((y - (M + 150)) / 20)), _ovf = 0, _draw = _items;
    if (_items.length > _max) { _draw = _items.slice(0, _max - 1); _ovf = _items.length - _draw.length; }
    _draw.forEach(function (it, i) {
      var amt = Math.round((Number(it.qty) || 0) * (Math.round(Number(it.unit_price) || 0)));
      if (i % 2 === 1) page.drawRectangle({ x: M, y: y - 20, width: W - 2 * M, height: 20, color: zebra });
      dr(ell(it.name, 9, cQty - cName - 16), cName + 8, y - 14, 9, ink);
      drR(String(it.qty), cQty + 24, y - 14, 9); dr(it.unit || '', cUnit, y - 14, 9);
      drR(yen2(it.unit_price), cPrice + 42, y - 14, 9); drR(yen2(amt), cAmt - 6, y - 14, 9);
      page.drawLine({ start: { x: M, y: y - 20 }, end: { x: W - M, y: y - 20 }, thickness: 0.5, color: line });
      y -= 20;
    });
    if (_ovf > 0) { dr('— ほか ' + _ovf + ' 件 —', cName + 8, y - 14, 9, muted); page.drawLine({ start: { x: M, y: y - 20 }, end: { x: W - M, y: y - 20 }, thickness: 0.5, color: line }); y -= 20; }
    y -= 22; var sx = 326;
    var row = function (l, v, col, sz) { dr(l, sx, y, sz || 9.5, col); drR(yen2(v), W - M - 6, y, sz || 9.5, col); y -= 15; };
    if (c.sub10 > 0) { row('10%対象 小計', c.sub10); row('消費税（10%）', c.tax10, muted); }
    if (c.sub8 > 0) { row('8%対象 小計（軽減）', c.sub8); row('消費税（8%）', c.tax8, muted); }
    if (K.wh && c.withholding > 0) row('源泉徴収税（10.21%）', -c.withholding, ink);
    y -= 3; page.drawLine({ start: { x: sx, y: y + 6 }, end: { x: W - M, y: y + 6 }, thickness: 1, color: ac });
    y -= 13; dr(K.total, sx, y, 12, ink); drR(yen2(payable), W - M - 6, y, 13, ac); y -= 24;
    // 下部ボックス
    if (K.receipt) {
      page.drawRectangle({ x: M, y: y - 56, width: W - 2 * M, height: 56, borderColor: line, borderWidth: 0.8, color: rgb(0.985, 0.985, 0.985) });
      dr('但し書き', M + 12, y - 16, 10, ink);
      dr(ell(doc.notes ? ('但し ' + doc.notes + ' として') : '但し　　　　　　　　　として', 9.5, W - 2 * M - 110), M + 12, y - 33, 9.5, muted);
      dr('上記金額を正に領収いたしました。', M + 12, y - 48, 8.5, muted);
      if (payable >= 50000) {
        page.drawRectangle({ x: W - M - 74, y: y - 50, width: 60, height: 38, borderColor: line, borderWidth: 0.8 });
        dr('収入印紙', W - M - 68, y - 24, 8, muted); dr('（貼付）', W - M - 66, y - 37, 7.5, muted);
      }
    } else {
      page.drawRectangle({ x: M, y: y - 50, width: W - 2 * M, height: 50, borderColor: line, borderWidth: 0.8, color: rgb(0.985, 0.985, 0.985) });
      dr(K.bank ? 'お振込先' : '備考', M + 12, y - 16, 10, ink);
      if (K.bank) dr(ell(doc.bank || co.default_bank || '', 9, W - 2 * M - 28), M + 12, y - 32, 9, muted);
      if (doc.notes) dr(ell('備考 : ' + doc.notes, 8.5, W - 2 * M - 28), M + 12, y - (K.bank ? 44 : 32), 8.5, muted);
    }
    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, (doc.doc_no || kind || 'document') + '.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }
  async function invoicePdf(id) {
    var data = await req('/api/documents/' + id);
    var doc = data.document;
    var kind = (doc.type && KINDS[doc.type]) ? doc.type : 'invoice';
    await render(doc, data.items || [], data.company || {}, kind);
  }
  // ---- クラシック様式（罫線グリッド・モノクロ）----
  async function renderClassic(doc, items, co, kind, theme) {
    await ensureLib();
    var K = kindCfg(kind), c = calc(items || []);
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var W = 595.28, H = 841.89, M = 48, R = W - M;
    var T = themeCols(theme); var ink = T.ink, mut = T.mut, line = rgb(0.28, 0.28, 0.30), grayfill = T.band, ac = T.ac;
    var page = pdf.addPage([W, H]);
    var yen2 = function (n) { return '¥' + (Math.round(Number(n) || 0)).toLocaleString('ja-JP'); };
    var tw = function (ss, sz) { return font.widthOfTextAtSize(sani(ss), sz); };
    var dr = function (ss, x, y, sz, col) { page.drawText(sani(ss), { x: x, y: y, size: sz, font: font, color: col || ink }); };
    var drR = function (ss, xr, y, sz, col) { ss = sani(ss); page.drawText(ss, { x: xr - font.widthOfTextAtSize(ss, sz), y: y, size: sz, font: font, color: col || ink }); };
    var drC = function (ss, cx, y, sz, col) { dr(ss, cx - tw(ss, sz) / 2, y, sz, col); };
    var ell = function (ss, sz, max) { ss = sani(ss); if (tw(ss, sz) <= max) return ss; while (ss.length > 1 && tw(ss + '…', sz) > max) ss = ss.slice(0, -1); return ss + '…'; };
    var hl = function (x1, x2, y, t) { page.drawLine({ start: { x: x1, y: y }, end: { x: x2, y: y }, thickness: t || 0.8, color: line }); };
    var vl = function (x, y1, y2, t) { page.drawLine({ start: { x: x, y: y1 }, end: { x: x, y: y2 }, thickness: t || 0.8, color: line }); };
    var rect = function (x, yTop, w, h, t) { page.drawRectangle({ x: x, y: yTop - h, width: w, height: h, borderColor: line, borderWidth: t || 0.8 }); };
    var payable = K.wh ? c.payable : c.total;

    // タイトル（中央・下線）
    var ty = H - 58; drC(K.t, W / 2, ty, 25, ink);
    var twid = tw(K.t, 25); page.drawLine({ start: { x: W / 2 - twid / 2 - 4, y: ty - 7 }, end: { x: W / 2 + twid / 2 + 4, y: ty - 7 }, thickness: 0.8, color: ac });
    var _lgC = await _embedImg(pdf, co.logo), _slC = await _embedImg(pdf, co.seal);
    if (_lgC) { var _lfC = _fit(_lgC, 150, 20); page.drawImage(_lgC, { x: M, y: H - 82 - _lfC.h, width: _lfC.w, height: _lfC.h }); }

    // 発行日・番号（右上）
    var hy = H - 92;
    drR('発行日 ： ' + (doc.issue_date || ''), R, hy, 9.5, ink);
    drR(K.num + ' ： ' + (doc.doc_no || '—'), R, hy - 15, 9.5, ink);
    if (K.due) drR('支払期限 ： ' + (doc.due_date || '—'), R, hy - 30, 9.5, ink);

    // 宛先（左・下線）
    var ay = H - 120;
    var client = (doc.client_name || '') + '　' + (doc.honorific || '御中');
    dr(ell(client, 15, (R - 220) - M - 14), M, ay, 15, ink);
    hl(M, M + 250, ay - 7, 0.8);
    if (doc.client_address) dr(doc.client_address, M, ay - 22, 9, mut);

    // 発行元ボックス（右・印欄つき）
    var bx = R - 220, bTop = H - 134, bW = 220, bH = 72;
    rect(bx, bTop, bW, bH, 0.8);
    var iy = bTop - 14;
    dr(co.company_name || '', bx + 8, iy, 10.5, ink); iy -= 13;
    if (co.reg_number) { dr('登録番号 ' + co.reg_number, bx + 8, iy, 8.5, ink); iy -= 12; }
    if (co.company_addr) { dr(ell(co.company_addr, 8, bW - 70), bx + 8, iy, 8, mut); iy -= 11; }
    if (co.email) { dr(ell(co.email, 8, bW - 70), bx + 8, iy, 8, mut); }
    // 印欄
    if (_slC) { var _sfC = _fit(_slC, 36, 36); page.drawImage(_slC, { x: bx + bW - 44 + (38 - _sfC.w) / 2, y: (bTop - 6) - 38 + (38 - _sfC.h) / 2, width: _sfC.w, height: _sfC.h }); } else { rect(bx + bW - 44, bTop - 6, 38, 38, 0.8); drC('印', bx + bW - 25, bTop - 28, 8, mut); }

    // ご請求金額ボックス（全幅・強調）
    var amtTop = H - 222, amtH = 34;
    rect(M, amtTop, R - M, amtH, 0.8);
    page.drawRectangle({ x: M, y: amtTop - amtH, width: 150, height: amtH, color: grayfill });
    dr(K.amount, M + 10, amtTop - 22, 11, ink);
    drR(yen2(payable), R - 14, amtTop - 24, 18, ink);
    vl(M + 150, amtTop, amtTop - amtH);

    // 明細テーブル（フルグリッド）
    var tTop = amtTop - amtH - 18;
    var cName = M, wQty = 44, wUnit = 38, wPrice = 78, wAmt = 88;
    var xQty = R - wQty - wUnit - wPrice - wAmt, xUnit = xQty + wQty, xPrice = xUnit + wUnit, xAmt = xPrice + wPrice;
    var headH = 22, rowH = 22, nrows = 12;
    // header
    page.drawRectangle({ x: M, y: tTop - headH, width: R - M, height: headH, color: grayfill });
    drC('品目・摘要', (cName + xQty) / 2, tTop - 15, 9.5, ink);
    drC('数量', xQty + wQty / 2, tTop - 15, 9.5, ink); drC('単位', xUnit + wUnit / 2, tTop - 15, 9.5, ink);
    drC('単価', xPrice + wPrice / 2, tTop - 15, 9.5, ink); drC('金額', xAmt + wAmt / 2, tTop - 15, 9.5, ink);
    var yy = tTop - headH, _allc = items || [];
    for (var i = 0; i < nrows; i++) {
      if (i === nrows - 1 && _allc.length > nrows) {
        dr('— ほか ' + (_allc.length - (nrows - 1)) + ' 件 —', cName + 8, yy - 15, 9, mut);
      } else {
        var it = _allc[i];
        if (it) {
          var amt = Math.round((Number(it.qty) || 0) * (Math.round(Number(it.unit_price) || 0)));
          dr(ell(it.name || '', 9.5, xQty - cName - 12), cName + 8, yy - 15, 9.5, ink);
          drC(String(it.qty == null ? '' : it.qty), xQty + wQty / 2, yy - 15, 9.5, ink);
          drC(it.unit || '', xUnit + wUnit / 2, yy - 15, 9.5, ink);
          drR(yen2(it.unit_price), xPrice + wPrice - 6, yy - 15, 9.5, ink);
          drR(yen2(amt), xAmt + wAmt - 6, yy - 15, 9.5, ink);
        }
      }
      yy -= rowH; hl(M, R, yy);
    }
    var tBot = yy;
    // 縦罫
    [cName, xQty, xUnit, xPrice, xAmt, R].forEach(function (x) { vl(x, tTop, tBot); });
    hl(M, R, tTop); hl(M, R, tTop - headH, 0.8);

    // 合計欄（右側・罫線）＋ 備考/振込先（左側）
    var sTop = tBot - 4, sx = xPrice, sRowH = 18;
    var srow = function (label, val, strong) {
      rect(sx, sTop, R - sx, sRowH, 0.8); vl(xAmt, sTop, sTop - sRowH);
      dr(label, sx + 6, sTop - 13, strong ? 10 : 9, ink); drR(yen2(val), R - 6, sTop - 13, strong ? 11 : 9.5, strong ? ac : ink);
      sTop -= sRowH;
    };
    srow('小計', c.subtotal); srow('消費税', c.tax);
    if (K.wh && c.withholding > 0) srow('源泉徴収税', -c.withholding);
    srow(K.total, payable, true);

    // 下部ボックス（左：振込先/備考 または 領収）
    var boxTop = tBot - 4, boxBot = sTop - 6, boxH = boxTop - boxBot; if (boxH < 46) boxH = 46;
    rect(M, boxTop, sx - M - 10, boxH, 0.8);
    if (K.receipt) {
      dr('但し書き', M + 8, boxTop - 15, 9.5, ink);
      dr(doc.notes ? ('但し ' + doc.notes + ' として') : '但し　　　　　　　　　として', M + 8, boxTop - 31, 9, mut);
      dr('上記正に領収いたしました。', M + 8, boxTop - 45, 8.5, mut);
    } else {
      dr(K.bank ? 'お振込先' : '備考', M + 8, boxTop - 15, 9.5, ink);
      if (K.bank && (doc.bank || co.default_bank)) dr(ell(doc.bank || co.default_bank, 9, sx - M - 28), M + 8, boxTop - 31, 9, mut);
      if (doc.notes) dr(ell('備考 : ' + doc.notes, 8.5, sx - M - 28), M + 8, boxTop - (K.bank ? 45 : 31), 8.5, mut);
    }
    // 収入印紙（領収・5万以上）
    if (K.receipt && payable >= 50000) { var ipx = sx - 10 - 60; rect(ipx, tBot - 10, 56, 36, 0.7); drC('収入印紙', ipx + 28, tBot - 31, 8, mut); }

    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, (doc.doc_no || kind || 'document') + '.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  // ---- ミニマル様式（余白広め・罫線少なめ）----
  async function renderMinimal(doc, items, co, kind, theme) {
    await ensureLib();
    var K = kindCfg(kind), c = calc(items || []);
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var W = 595.28, H = 841.89, M = 52, R = W - M;
    var T = themeCols(theme), ink = T.ink, mut = T.mut, ac = T.ac, line = rgb(0.85, 0.85, 0.86);
    var page = pdf.addPage([W, H]);
    var yen2 = function (n) { return '¥' + (Math.round(Number(n) || 0)).toLocaleString('ja-JP'); };
    var tw = function (ss, sz) { return font.widthOfTextAtSize(sani(ss), sz); };
    var dr = function (ss, x, y, sz, col) { page.drawText(sani(ss), { x: x, y: y, size: sz, font: font, color: col || ink }); };
    var drR = function (ss, xr, y, sz, col) { ss = sani(ss); page.drawText(ss, { x: xr - font.widthOfTextAtSize(ss, sz), y: y, size: sz, font: font, color: col || ink }); };
    var ell = function (ss, sz, max) { ss = sani(ss); if (tw(ss, sz) <= max) return ss; while (ss.length > 1 && tw(ss + '…', sz) > max) ss = ss.slice(0, -1); return ss + '…'; };
    var hl = function (x1, x2, y, t, col) { page.drawLine({ start: { x: x1, y: y }, end: { x: x2, y: y }, thickness: t || 0.6, color: col || line }); };
    var payable = K.wh ? c.payable : c.total;
    var _lgM = await _embedImg(pdf, co.logo), _slM = await _embedImg(pdf, co.seal);
    var y = H - 60;
    dr(K.en, M, y + 13, 8.5, ac);
    dr(K.t, M, y - 17, 24, ink);
    page.drawRectangle({ x: M, y: y - 32, width: 46, height: 3, color: ac });
    var _ldx = R;
    if (_lgM) { var _lfM = _fit(_lgM, 120, 28); page.drawImage(_lgM, { x: R - _lfM.w, y: (y + 6) - _lfM.h, width: _lfM.w, height: _lfM.h }); _ldx = R - _lfM.w - 12; }
    drR('発行日　' + (doc.issue_date || ''), _ldx, y - 2, 9, mut);
    drR(K.num + '　' + (doc.doc_no || '—'), _ldx, y - 16, 9, mut);
    if (K.due) drR('支払期限　' + (doc.due_date || '—'), _ldx, y - 30, 9, mut);
    y -= 54;
    var rx = 348, yr = y;
    if (_slM) { var _sfM = _fit(_slM, 40, 40); page.drawImage(_slM, { x: R - _sfM.w, y: yr - 30, width: _sfM.w, height: _sfM.h }); }
    dr(ell((doc.client_name || '') + '　' + (doc.honorific || '御中'), 14, rx - M - 14), M, y, 14, ink);
    var leftBot = y;
    if (doc.client_address) { dr(ell(doc.client_address, 9, rx - M - 14), M, y - 15, 9, mut); leftBot = y - 15; }
    dr(ell(co.company_name || '', 11, R - rx - (_slM ? 46 : 0)), rx, yr, 11, ink); yr -= 13;
    if (co.reg_number) { dr('登録番号 ' + co.reg_number, rx, yr, 8.5, mut); yr -= 12; }
    if (co.company_addr) { dr(ell(co.company_addr, 8, R - rx), rx, yr, 8, mut); yr -= 11; }
    if (co.email) { dr(ell(co.email, 8, R - rx), rx, yr, 8, mut); yr -= 11; }
    y = Math.min(leftBot, yr) - 30;
    dr(K.amount, M, y, 11, mut); drR(yen2(payable), R, y - 6, 23, ac);
    y -= 20; hl(M, R, y, 1.2, ac); y -= 22;
    // 明細（罫線少なめ）
    var cName = M, cQty = 350, cUnit = 392, cPrice = 452, cAmt = R;
    dr('品目・摘要', cName, y, 8.5, mut); drR('数量', cQty + 24, y, 8.5, mut); dr('単位', cUnit, y, 8.5, mut); drR('単価', cPrice + 42, y, 8.5, mut); drR('金額', cAmt, y, 8.5, mut);
    y -= 7; hl(M, R, y, 0.8, ink); y -= 4;
    var _mall = items || [], _mmax = Math.max(1, Math.floor((y - (M + 130)) / 17)), _mdraw = _mall, _movf = 0;
    if (_mall.length > _mmax) { _mdraw = _mall.slice(0, _mmax - 1); _movf = _mall.length - _mdraw.length; }
    _mdraw.forEach(function (it) {
      var amt = Math.round((Number(it.qty) || 0) * (Math.round(Number(it.unit_price) || 0)));
      y -= 17;
      dr(ell(it.name || '', 10, cQty - cName - 12), cName, y + 3, 10, ink);
      drR(String(it.qty == null ? '' : it.qty), cQty + 24, y + 3, 9.5, ink); dr(it.unit || '', cUnit, y + 3, 9.5, ink);
      drR(yen2(it.unit_price), cPrice + 42, y + 3, 9.5, ink); drR(yen2(amt), cAmt, y + 3, 9.5, ink);
      hl(M, R, y - 3, 0.5);
    });
    if (_movf > 0) { y -= 17; dr('— ほか ' + _movf + ' 件 —', cName, y + 3, 9.5, mut); hl(M, R, y - 3, 0.5); }
    y -= 24; var sx = 360;
    var row = function (l, v, col) { dr(l, sx, y, 9.5, col || ink); drR(yen2(v), R, y, 9.5, col || ink); y -= 15; };
    row('小計', c.subtotal); row('消費税', c.tax, mut);
    if (K.wh && c.withholding > 0) row('源泉徴収税', -c.withholding, mut);
    y -= 2; hl(sx, R, y + 6, 1, ac); y -= 8;
    dr(K.total, sx, y, 11, ink); drR(yen2(payable), R, y - 1, 13, ac); y -= 30;
    // 下部
    if (K.receipt) {
      dr('但し書き', M, y, 9.5, ink); dr(doc.notes ? ('但し ' + doc.notes + ' として') : '但し　　　　　　　　　として', M, y - 15, 9, mut);
      dr('上記正に領収いたしました。', M, y - 29, 8.5, mut);
      if (payable >= 50000) { page.drawRectangle({ x: R - 60, y: y - 30, width: 56, height: 38, borderColor: rgb(0.6, 0.6, 0.6), borderWidth: 0.6 }); dr('収入印紙', R - 54, y - 10, 7.5, mut); dr('（貼付）', R - 52, y - 22, 7, mut); }
    } else {
      dr(K.bank ? 'お振込先' : '備考', M, y, 9.5, ink);
      if (K.bank) dr(doc.bank || co.default_bank || '', M, y - 15, 9, mut);
      if (doc.notes) dr('備考 : ' + doc.notes, M, y - (K.bank ? 29 : 15), 8.5, mut);
    }
    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, (doc.doc_no || kind || 'document') + '.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  async function invoiceFromData(doc, items, co, kind, template, theme) { if (template === 'classic') { await renderClassic(doc, items, co, kind, theme); } else if (template === 'minimal') { await renderMinimal(doc, items, co, kind, theme); } else { await render(doc, items, co, kind, theme); } }
  async function logout() { try { await req('/api/auth/logout', 'POST'); } catch (e) {} location.href = '/login'; }

  // ---- 履歴書PDF（写真埋め込み対応・クライアント完結） ----
  function wrapLines(font, size, text, maxW) {
    var out = [];
    String(text == null ? '' : text).split('\n').forEach(function (para) {
      var ln = '';
      for (var i = 0; i < para.length; i++) {
        var t = ln + para[i];
        if (ln && font.widthOfTextAtSize(t, size) > maxW) { out.push(ln); ln = para[i]; } else ln = t;
      }
      out.push(ln);
    });
    return out;
  }
  async function renderResume(data) {
    await ensureLib();
    data = data || {};
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var W = 595.28, H = 841.89, M = 42, R = W - M;
    var ink = rgb(0.12, 0.12, 0.13), mut = rgb(0.4, 0.42, 0.46), line = rgb(0.22, 0.23, 0.25);
    var T = themeCols(data.theme);
    var fmt = (data.format === 'jis') ? 'jis' : 'mhlw';
    var page;
    function mk() { page = pdf.addPage([W, H]); }
    var dr = function (s, x, y, sz, col) { page.drawText(sani(s), { x: x, y: y, size: sz, font: font, color: col || ink }); };
    var tw = function (s, sz) { return font.widthOfTextAtSize(sani(s), sz); };
    var drC = function (s, cx, y, sz, col) { dr(s, cx - tw(s, sz) / 2, y, sz, col); };
    var ell = function (s, sz, max) { s = sani(s); if (tw(s, sz) <= max) return s; while (s.length > 1 && tw(s + '…', sz) > max) s = s.slice(0, -1); return s + '…'; };
    var hline = function (x1, x2, yy, t) { page.drawLine({ start: { x: x1, y: yy }, end: { x: x2, y: yy }, thickness: t || 0.7, color: line }); };
    var vline = function (x, y1, y2, t) { page.drawLine({ start: { x: x, y: y1 }, end: { x: x, y: y2 }, thickness: t || 0.7, color: line }); };
    var box = function (x, yTop, w, h, bw) { page.drawRectangle({ x: x, y: yTop - h, width: w, height: h, borderColor: line, borderWidth: bw || 0.7 }); };
    var dlnH = function (x1, x2, yy) { var t = x1; while (t < x2) { page.drawLine({ start: { x: t, y: yy }, end: { x: Math.min(t + 2.2, x2), y: yy }, thickness: 0.7, color: line }); t += 4.4; } };
    var dlnV = function (x, y1, y2) { var t = y1; while (t > y2) { page.drawLine({ start: { x: x, y: t }, end: { x: x, y: Math.max(t - 2.2, y2) }, thickness: 0.7, color: line }); t -= 4.4; } };
    // vertical-center a text baseline inside a cell whose TOP edge is `top` and height is `h`
    var vmid = function (top, h, sz) { return top - h / 2 - sz * 0.34; };
    var drL = function (s, x, top, h, sz, col) { dr(s, x, vmid(top, h, sz), sz, col); };      // left aligned, v-centered
    var drCv = function (s, cx, top, h, sz, col) { drC(s, cx, vmid(top, h, sz), sz, col); };   // h + v centered

    function table(title, rows, maxRows, top, rowH) {
      var c1 = M + 42, c2 = M + 84, headH = 18;
      page.drawRectangle({ x: M, y: top - headH, width: R - M, height: headH, color: T.band });
      drCv('年', (M + c1) / 2, top, headH, 9); drCv('月', (c1 + c2) / 2, top, headH, 9); drCv(title, (c2 + R) / 2, top, headH, 9.5);
      hline(M, R, top); hline(M, R, top - headH);
      var yy = top - headH;
      for (var i = 0; i < maxRows; i++) {
        var r = (rows && rows[i]) || {};
        drCv(r.y || '', (M + c1) / 2, yy, rowH, 10); drCv(r.m || '', (c1 + c2) / 2, yy, rowH, 10);
        drL(ell(r.text || '', 10, R - (c2 + 8) - 8), c2 + 8, yy, rowH, 10);
        yy -= rowH; hline(M, R, yy);
      }
      vline(M, top, yy); vline(c1, top, yy); vline(c2, top, yy); vline(R, top, yy);
      return yy;
    }
    function textBox(label, text, top, h, innerLines) {
      page.drawRectangle({ x: M, y: top - 16, width: R - M, height: 16, color: T.band });
      dr(label, M + 5, vmid(top, 16, 9), 9, ink); hline(M, R, top); hline(M, R, top - 16);
      var lines = wrapLines(font, 10, text || '', R - M - 20), ly = top - 32;
      lines.forEach(function (l) { if (ly > top - h + 6) { dr(l, M + 8, ly, 10, ink); ly -= 15; } });
      if (innerLines) { for (var gi = 1; gi < innerLines; gi++) { var gy = (top - 16) - (h - 16) * gi / innerLines; hline(M, R, gy); } }
      box(M, top, R - M, h, 0.7);
      return top - h;
    }

    var b = data.birth || {}, age = (data.age != null && data.age !== '') ? data.age : '';
    var dt = data.date || {};

    // ========== PAGE 1 ==========
    mk();
    dr('履 歴 書', M, H - M - 16, 22, ink);
    dr((dt.y || '　　　') + ' 年 ' + (dt.m || '　') + ' 月 ' + (dt.d || '　') + ' 日現在', M + 250, H - M - 14, 10.5, ink);

    // 氏名ボックス + 写真欄（上端を揃える）
    var nbTop = H - M - 34, furiH = 18, nameH = 64, nbH = furiH + nameH, idTop = nbTop - nbH;
    var pbW = 84, pbTop = H - M - 4, pbBot = idTop, pbH = pbTop - pbBot, pbX = R - pbW, nbR = pbX - 8;
    dlnH(pbX, pbX + pbW, pbTop); dlnH(pbX, pbX + pbW, pbBot); dlnV(pbX, pbTop, pbBot); dlnV(pbX + pbW, pbTop, pbBot);
    if (data.photo && data.photo.bytes) {
      try {
        var img = data.photo.type === 'png' ? await pdf.embedPng(data.photo.bytes) : await pdf.embedJpg(data.photo.bytes);
        var pad = 4, bw2 = pbW - pad * 2, bh2 = pbH - pad * 2, sc = Math.min(bw2 / img.width, bh2 / img.height), iw = img.width * sc, ih = img.height * sc;
        page.drawImage(img, { x: pbX + (pbW - iw) / 2, y: pbBot + (pbH - ih) / 2, width: iw, height: ih });
      } catch (e) { drC('写真', pbX + pbW / 2, (pbTop + pbBot) / 2, 9, mut); }
    } else {
      drC('写真を貼る位置', pbX + pbW / 2, pbTop - 15, 7.3, ink);
      dr('写真を貼る必要が', pbX + 6, pbTop - 33, 6.6, mut); dr('ある場合', pbX + 24, pbTop - 43, 6.6, mut);
      dr('1.縦 36〜40mm', pbX + 6, pbTop - 59, 6.6, mut); dr('  横 24〜30mm', pbX + 6, pbTop - 69, 6.6, mut);
      dr('2.本人単身胸から上', pbX + 6, pbTop - 83, 6.6, mut); dr('3.裏面にのりづけ', pbX + 6, pbTop - 95, 6.6, mut);
    }
    // 氏名ボックス
    drL('ふりがな', M + 6, nbTop, furiH, 8, mut);
    drL(ell(data.furi_name || '', 10, nbR - (M + 56) - 6), M + 56, nbTop, furiH, 10, ink);
    dlnH(M, nbR, nbTop - furiH);
    drL('氏　名', M + 6, nbTop - furiH, nameH, 11, mut);
    dr(ell(data.name || '', 20, nbR - (M + 80) - 6), M + 80, vmid(nbTop - furiH, nameH, 20), 20, ink);
    box(M, nbTop, nbR - M, nbH, 0.7);

    // 生年月日 / 性別 行
    var y = idTop, r1H = 28, sexX = R - 108;
    drCv((b.y || '　　　') + ' 年 ' + (b.m || '　') + ' 月 ' + (b.d || '　') + ' 日生　（満 ' + (age || '　') + ' 歳）', (M + sexX) / 2, y, r1H, 11, ink);
    var sexLbl = '性別';
    drL(sexLbl, sexX + 8, y, r1H, 9.5, mut);
    dr(data.gender || '', sexX + 10 + tw(sexLbl, 9.5) + 10, vmid(y, r1H, 10.5), 10.5, ink);
    box(M, y, R - M, r1H, 0.7); vline(sexX, y, y - r1H);
    y -= r1H;

    // 現住所 / 連絡先ブロック
    function addrBlock(label, note, furi, zip, addr, tel, email, top) {
      var cX = R - 168, fH = 16, aH = 36, bH = fH + aH;
      // 左：ふりがな帯
      drL('ふりがな', M + 6, top, fH, 8, mut);
      if (furi) drL(ell(furi, 9.5, cX - (M + 56) - 6), M + 56, top, fH, 9.5, ink);
      dlnH(M, cX, top - fH);
      // 左：住所帯（ラベル＋〒zip、下に住所）
      drL(label, M + 6, top - fH, aH, 9.5, mut);
      dr('〒 ' + (zip || ''), M + 72, top - fH - 13, 9, mut);
      if (addr) dr(ell(addr, 10, cX - (M + 72) - 6), M + 72, top - fH - 27, 10, ink);
      if (note) dr(note, M + 72, top - fH - 29, 7.3, mut);
      // 右：電話（上半分）／E-mail（下半分）
      var telH = bH / 2, emTop = top - bH / 2, emH = bH / 2, emCy = emTop - emH / 2;
      drL('電話', cX + 8, top, telH, 8, mut);
      if (tel) dr(tel, cX + 44, vmid(top, telH, 9.5), 9.5, ink);
      dr('E-mail', cX + 8, emCy + 5, 8, mut);
      if (email) dr(ell(email, 8, R - (cX + 8) - 6), cX + 8, emCy - 7, 8, ink);
      box(M, top, R - M, bH, 0.7); vline(cX, top, top - bH); hline(cX, R, top - bH / 2);
      return top - bH;
    }
    y = addrBlock('現住所', '', data.furi_addr || '', data.zip || '', data.addr || '', data.tel || '', data.email || '', y);
    y = addrBlock('連絡先', data.contact ? '' : '（現住所以外に連絡を希望する場合のみ記入）', '', '', data.contact || '', '', '', y);

    // 学歴・職歴（1ページ目・下まで）
    var footY = M + 2, tTop = y - 14, rowH = 24, avail = tTop - 18 - (M + 22);
    var rows1 = Math.max(8, Math.floor(avail / rowH));
    var hist = (data.histories || []);
    table('学 歴 ・ 職 歴', hist.slice(0, rows1), rows1, tTop, rowH);
    if (fmt === 'mhlw') dr('※「性別」欄の記載は任意です。記載しなくても構いません。', M, footY, 8.5, mut);

    // ========== PAGE 2 ==========
    mk();
    var y2 = H - M;
    y2 = table('学 歴 ・ 職 歴', hist.slice(rows1), 7, y2, 24);
    y2 -= 18;
    y2 = table('免 許 ・ 資 格', data.licenses || [], 6, y2, 24);
    y2 -= 22;
    var motH = data.variant === 'shinsotsu' ? 206 : 168;
    if (fmt === 'jis') motH -= 54;
    var motLabel = data.variant === 'shinsotsu' ? '志望の動機、特技、自己PR、得意科目・ゼミ、趣味 など' : '志望の動機、特技、自己PR、アピールポイントなど';
    y2 = textBox(motLabel, data.motivation || '', y2, motH);
    y2 -= 16;
    var reqH = data.variant === 'arbeit' ? 116 : 84;
    var reqLabel = data.variant === 'arbeit' ? '本人希望記入欄（希望勤務日・時間・勤務地・その他の希望があれば記入）' : '本人希望記入欄（特に給料・職種・勤務時間・勤務地・その他についての希望などがあれば記入）';
    y2 = textBox(reqLabel, data.request || '', y2, reqH);

    // JIS様式：通勤時間・扶養家族・配偶者ブロック
    if (fmt === 'jis') {
      y2 -= 16;
      var jTop = y2, jH = 52, midX = (M + R) / 2, rh = jH / 2;
      drL('通勤時間', M + 8, jTop, rh, 9, mut);
      dr('約 ' + (data.commute_h || '　') + ' 時間 ' + (data.commute_m || '　') + ' 分', M + 74, vmid(jTop, rh, 9.5), 9.5, ink);
      drL('扶養家族数（配偶者を除く）', midX + 8, jTop, rh, 9, mut);
      dr((data.dependents || '　') + ' 人', midX + 158, vmid(jTop, rh, 9.5), 9.5, ink);
      var j2 = jTop - rh;
      drL('配偶者', M + 8, j2, rh, 9, mut);
      dr(data.spouse === '有' ? '有' : (data.spouse === '無' ? '無' : '有　・　無'), M + 74, vmid(j2, rh, 9.5), 9.5, ink);
      drL('配偶者の扶養義務', midX + 8, j2, rh, 9, mut);
      dr(data.spouse_support === '有' ? '有' : (data.spouse_support === '無' ? '無' : '有　・　無'), midX + 158, vmid(j2, rh, 9.5), 9.5, ink);
      box(M, jTop, R - M, jH, 0.7); hline(M, R, jTop - rh); vline(midX, jTop, jTop - jH);
      y2 = jTop - jH;
    }

    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, '履歴書.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  async function resumePdf(data) { await renderResume(data); }

  // ---- 送付状など手紙型PDF ----
  function fmtDate(d) {
    if (!d) return '';
    if (typeof d === 'string') { var p = d.split('-'); return p.length === 3 ? (p[0] + '年' + parseInt(p[1], 10) + '月' + parseInt(p[2], 10) + '日') : d; }
    return (d.y || '') + '年' + (d.m || '') + '月' + (d.d || '') + '日';
  }
  async function renderLetter(data) {
    await ensureLib();
    data = data || {};
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var page = pdf.addPage([595.28, 841.89]);
    var W = 595.28, H = 841.89, M = 56;
    var T = themeCols(data.theme); var ink = T.ink, mut = T.mut, ac = T.ac, line = T.line;
    var dr = function (s, x, y, sz, col) { page.drawText(sani(s), { x: x, y: y, size: sz, font: font, color: col || ink }); };
    var tw = function (s, sz) { return font.widthOfTextAtSize(sani(s), sz); };
    var drR = function (s, xr, y, sz, col) { s = sani(s); page.drawText(s, { x: xr - font.widthOfTextAtSize(s, sz), y: y, size: sz, font: font, color: col || ink }); };
    var drC = function (s, cx, y, sz, col) { dr(s, cx - tw(s, sz) / 2, y, sz, col); };
    var ell = function (s, sz, max) { s = sani(s); if (tw(s, sz) <= max) return s; while (s.length > 1 && tw(s + '…', sz) > max) s = s.slice(0, -1); return s + '…'; };
    var PAT = data.pattern || 'standard';
    var y = H - M - 6;
    drR(fmtDate(data.date), W - M, y, 10.5, mut); y -= 30;
    var headTop = y;
    var hon = data.to_hon || '御中';
    var toLines = [];
    if (data.to_company) toLines.push(data.to_company + (data.to_name ? '' : ('　' + hon)));
    if (data.to_dept) toLines.push(data.to_dept);
    var pl = [data.to_title, data.to_name].filter(Boolean).join('　'); if (data.to_name) pl += ('　' + (data.to_hon || '様'));
    if (pl) toLines.push(pl);
    var ly = headTop; toLines.forEach(function (l, i) { dr(ell(l, i === 0 ? 13 : 12, (W - 2 * M) * 0.52), M, ly, i === 0 ? 13 : 12, ink); ly -= 20; });
    var fromLines = [data.from_company, data.from_dept, data.from_name, data.from_addr, data.from_tel ? ('TEL ' + data.from_tel) : '', data.from_email ? ('Email ' + data.from_email) : ''].filter(Boolean);
    var ry = headTop; fromLines.forEach(function (l) { drR(ell(l, 10, (W - 2 * M) * 0.48), W - M, ry, 10, mut); ry -= 14; });
    y = Math.min(ly, ry) - 20;
    var subj = ell(data.subject || '書類送付のご案内', 15, W - 2 * M - 30);
    if (PAT === 'minimal') { dr(subj, M, y, 15, ink); page.drawLine({ start: { x: M, y: y - 7 }, end: { x: M + tw(subj, 15) + 30, y: y - 7 }, thickness: 1.6, color: ac }); }
    else { drC(subj, W / 2, y, 15, ink); page.drawLine({ start: { x: W / 2 - tw(subj, 15) / 2, y: y - 6 }, end: { x: W / 2 + tw(subj, 15) / 2, y: y - 6 }, thickness: 1, color: ac }); }
    y -= 40;
    var full = '拝啓　' + (data.body || '').trim();
    var blines = wrapLines(font, 11, full, W - 2 * M);
    var docCount = (data.docs || []).filter(function (d) { return d.name; }).length;
    var floorY = M + 44 + docCount * 22 + 64;
    var maxLines = Math.max(3, Math.floor((y - floorY) / 19));
    if (blines.length > maxLines) { blines = blines.slice(0, maxLines); var li = blines.length - 1; blines[li] = blines[li].slice(0, Math.max(1, blines[li].length - 1)) + '…'; }
    blines.forEach(function (l) { dr(l, M, y, 11, ink); y -= 19; });
    y -= 4; drR('敬具', W - M, y, 11, ink); y -= 28;
    drC('記', W / 2, y, 12, ink); y -= 22;
    var kiTop = y + 14;
    (data.docs || []).filter(function (d) { return d.name; }).forEach(function (d) {
      dr('・ ' + d.name, M + 50, y, 11, ink); if (d.qty) drR(d.qty + ' 部', W - M - 50, y, 11, ink);
      if (PAT !== 'frame') page.drawLine({ start: { x: M + 50, y: y - 5 }, end: { x: W - M - 50, y: y - 5 }, thickness: 0.4, color: line });
      y -= 22;
    });
    if (PAT === 'frame') { page.drawRectangle({ x: M + 36, y: y + 8, width: W - 2 * M - 72, height: kiTop - (y + 8), borderColor: line, borderWidth: 0.8 }); }
    y -= 8; drR('以上', W - M, y, 11, ink);
    if (PAT === 'frame') { page.drawRectangle({ x: M - 16, y: 44, width: W - 2 * (M - 16), height: H - 88, borderColor: line, borderWidth: 1 }); }
    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, '送付状.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }
  async function letterPdf(data) { await renderLetter(data); }

  // ---- 職務経歴書PDF（自動ページ送り） ----
  async function renderCareer(data) {
    await ensureLib();
    data = data || {};
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var W = 595.28, H = 841.89, M = 54;
    var T = themeCols(data.theme); var ink = T.ink, mut = T.mut, ac = T.ac, line = T.line;
    var cur, y;
    function np() { cur = pdf.addPage([W, H]); y = H - M; }
    np();
    function dr(s, x, yy, sz, col) { cur.drawText(sani(s), { x: x, y: yy, size: sz, font: font, color: col || ink }); }
    function drR(s, xr, yy, sz, col) { s = sani(s); cur.drawText(s, { x: xr - font.widthOfTextAtSize(s, sz), y: yy, size: sz, font: font, color: col || ink }); }
    function ellc(s, sz, max) { s = sani(s); if (font.widthOfTextAtSize(s, sz) <= max) return s; while (s.length > 1 && font.widthOfTextAtSize(s + '…', sz) > max) s = s.slice(0, -1); return s + '…'; }
    function need(h) { if (y - h < M) np(); }
    function para(text, size, opt) { opt = opt || {}; var indent = opt.indent || 0, lh = opt.lh || (size + 5), col = opt.col || ink; if (!text) return; wrapLines(font, size, text, W - 2 * M - indent).forEach(function (l) { need(lh); dr(l, M + indent, y - size, size, col); y -= lh; }); }
    function gap(h) { y -= h; }
    var PAT = data.pattern || 'bar';
    function section(title) {
      need(32);
      if (PAT === 'band') { cur.drawRectangle({ x: M, y: y - 18, width: W - 2 * M, height: 18, color: T.band }); cur.drawRectangle({ x: M, y: y - 18, width: 3.5, height: 18, color: ac }); dr(title, M + 11, y - 14, 11.5, ink); y -= 34; }
      else if (PAT === 'line') { dr(title, M, y - 14, 12.5, ink); cur.drawLine({ start: { x: M, y: y - 20 }, end: { x: W - M, y: y - 20 }, thickness: 1.2, color: ac }); y -= 38; }
      else { cur.drawRectangle({ x: M, y: y - 16, width: 3.5, height: 14, color: ac }); dr(title, M + 10, y - 14, 12, ink); cur.drawLine({ start: { x: M, y: y - 21 }, end: { x: W - M, y: y - 21 }, thickness: 0.6, color: line }); y -= 38; }
    }

    dr('職務経歴書', (W - font.widthOfTextAtSize('職務経歴書', 20)) / 2, y - 18, 20, ink);
    drR(fmtDate(data.date), W - M, y - 6, 10.5, mut);
    drR((data.name || '') + '　', W - M, y - 22, 11, ink);
    y -= 44;

    if (data.summary) { section('職務要約'); para(data.summary, 10.5, { lh: 16 }); gap(10); }

    section('職務経歴');
    (data.careers || []).filter(function (c) { return c.company || c.detail || c.period; }).forEach(function (c) {
      need(42);
      cur.drawRectangle({ x: M, y: y - 18, width: W - 2 * M, height: 18, color: T.band });
      dr(ellc(c.period || '', 9.5, 138), M + 6, y - 13, 9.5, mut); dr(ellc(c.company || '', 11, W - M - 150 - 6), M + 150, y - 13, 11, ink); y -= 24;
      var meta = [c.business ? ('事業内容：' + c.business) : '', c.employees ? ('従業員数：' + c.employees) : '', c.role ? ('雇用形態・役職：' + c.role) : ''].filter(Boolean).join('　／　');
      if (meta) para(meta, 9, { col: mut, lh: 14 });
      if (c.detail) para(c.detail, 10, { lh: 15 });
      gap(12);
    });

    if (data.skills) { gap(2); section('活かせる経験・知識・スキル'); para(data.skills, 10, { lh: 15 }); gap(8); }
    if (data.quals) { section('保有資格'); para(data.quals, 10, { lh: 15 }); gap(8); }
    if (data.selfpr) { section('自己PR'); para(data.selfpr, 10, { lh: 16 }); gap(8); }

    need(22); drR('以上', W - M, y - 10, 10.5, ink);

    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, '職務経歴書.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }
  async function careerPdf(data) { await renderCareer(data); }


  // ---- 退職届・退職願（縦書き）----
  function kansuji(n) {
    n = parseInt(n, 10); if (isNaN(n)) return '';
    if (n === 0) return '〇';
    var d = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
    if (n < 10) return d[n];
    if (n < 20) return '十' + (n % 10 ? d[n % 10] : '');
    if (n < 100) return d[Math.floor(n / 10)] + '十' + (n % 10 ? d[n % 10] : '');
    // 年など3桁以上はそのまま桁読み
    return String(n).split('').map(function (c) { return d[+c] || '〇'; }).join('');
  }
  function wareki(iso) {
    if (!iso) return { era: '令和', y: '　', m: '　', d: '　' };
    var p = String(iso).split('-'); var yy = +p[0], mm = +p[1], dd = +p[2];
    var era = '令和', ey = yy - 2018;
    if (yy < 2019) { era = '平成'; ey = yy - 1988; }
    return { era: era, y: kansuji(ey) || '元', m: kansuji(mm), d: kansuji(dd) };
  }
  async function renderResign(data) {
    await ensureLib();
    data = data || {};
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var W = 595.28, H = 841.89;
    var page = pdf.addPage([W, H]);
    var ink = rgb(0.1, 0.1, 0.12);
    var T = themeCols(data.theme);
    var dr = function (s, x, y, sz, col) { page.drawText(sani(s), { x: x, y: y, size: sz, font: font, color: col || ink }); };
    var tw = function (s, sz) { return font.widthOfTextAtSize(sani(s), sz); };
    var ellr = function (s, sz, max) { s = sani(s); if (tw(s, sz) <= max) return s; while (s.length > 1 && tw(s + '…', sz) > max) s = s.slice(0, -1); return s + '…'; };
    var cut = function (s, n) { s = String(s == null ? '' : s); return s.length > n ? s.slice(0, n - 1) + '…' : s; };
    // 縦書き: 1文字ずつ下方向。全角中心でxに中央寄せ
    function vcol(str, x, yTop, sz, col) {
      sz = sz || 15; var y = yTop; str = String(str || '');
      for (var i = 0; i < str.length; i++) {
        var ch = str[i], w = tw(ch, sz);
        dr(ch, x - w / 2, y - sz, sz, col);
        y -= sz * 1.52;
      }
      return y;
    }
    var isWish = (data.kind === 'wish');
    var PAT = data.pattern || 'tate';
    var title = isWish ? '退 職 願' : '退 職 届';
    function kanN(n){ n=parseInt(n,10); if(isNaN(n))return ''; var d=['〇','一','二','三','四','五','六','七','八','九']; if(n<10)return d[n]; if(n<20)return '十'+(n%10?d[n%10]:''); if(n<100)return (Math.floor(n/10)>1?d[Math.floor(n/10)]:'')+'十'+(n%10?d[n%10]:''); return String(n).split('').map(function(c){return d[+c]||'〇';}).join(''); }
    // wareki() は漢数字を返す（例: 令和八年十一月十六日）
    function wkK(iso){ if(!iso)return '令和　年　月　日'; var w=wareki(iso); return w.era+w.y+'年'+w.m+'月'+w.d+'日'; }
    function wkA(iso){ if(!iso)return '令和　年　月　日'; var p=String(iso).split('-'), yy=+p[0], ey=yy-2018, era='令和'; if(yy<2019){era='平成';ey=yy-1988;} return era+(ey===1?'元':ey)+'年'+(+p[1])+'月'+(+p[2])+'日'; }
    // 縦書き1文字: 句読点は升目の右上、長音・ダッシュ類は90度回転
    var PUNCT = '、。，．', ROT = 'ー－―‐-～〜…‥（）()「」『』';
    function vch(ch, x, ytop, sz){
      var w = tw(ch, sz);
      if (PUNCT.indexOf(ch) >= 0) { dr(ch, x - w / 2 + sz * 0.55, ytop - sz * 0.42, sz, ink); return; }
      if (ROT.indexOf(ch) >= 0) { page.drawText(sani(ch), { x: x - sz * 0.36, y: ytop - sz * 0.02 - (sz - w) / 2, size: sz, font: font, color: ink, rotate: P.degrees(-90) }); return; }
      dr(ch, x - w / 2, ytop - sz, sz, ink);
    }
    function vc(str, x, yTop, sz, step){ str=String(str||''); step=step||sz*1.6; var y=yTop; for(var i=0;i<str.length;i++){ vch(str[i], x, y, sz); y-=step; } return y; }
    // 列分割（行頭禁則: 句読点・閉じ括弧は前の列にぶら下げ）
    function vsplit(str, n){ var NOHEAD='、。，．」』）)ぁぃぅぇぉっゃゅょァィゥェォッャュョー', out=[], cur=''; for(var i=0;i<str.length;i++){ var ch=str[i]; if(cur.length>=n && NOHEAD.indexOf(ch)<0){ out.push(cur); cur=''; } cur+=ch; } if(cur) out.push(cur); return out; }

    if (PAT === 'yoko' || PAT === 'yoko_frame') {
      var drR2 = function (ss, xr, yy, zs, col) { ss = sani(ss); page.drawText(ss, { x: xr - font.widthOfTextAtSize(ss, zs), y: yy, size: zs, font: font, color: col || ink }); };
      var M = 86;
      if (PAT === 'yoko_frame') { page.drawRectangle({ x: 48, y: 56, width: W - 96, height: H - 112, borderColor: T.line, borderWidth: 1 }); }
      dr(title, (W - tw(title, 26)) / 2, H - 132, 26, ink);
      var y = H - 210;
      drR2(wkA(data.submit_date), W - M, y, 13, ink); y -= 56;
      if (data.to_company) { dr(ellr(data.to_company, 15, W - 2 * M), M, y, 15, ink); y -= 28; }
      var tl = [data.to_title, data.to_name].filter(Boolean).join('　');
      if (tl) { dr(ellr(tl + '　殿', 15, W - 2 * M), M, y, 15, ink); y -= 28; }
      else if (data.to_company) { dr('殿', M, y, 15, ink); y -= 28; }
      y -= 52;
      dr('私儀、', M, y, 14, ink); y -= 34;
      var bodyY = 'このたび' + cut(data.reason || '一身上の都合', 40) + 'により、来る' + wkA(data.retire_date) + 'をもって退職' + (isWish ? 'いたしたく、ここにお願い申し上げます。' : 'いたします。');
      wrapLines(font, 14, bodyY, W - 2 * M - 14).forEach(function (l) { dr(l, M + 14, y, 14, ink); y -= 30; });
      y -= 10; drR2('以上', W - M, y, 14, ink);
      y -= 86;
      // 署名ブロック（所属・氏名を左揃え、右端に押印欄）
      var sigW = Math.max(tw(cut(data.dept || '', 24), 13), tw(cut(data.name || '', 24), 16)) ;
      var sx = W - M - 34 - sigW - 14;
      if (data.dept) { dr(cut(data.dept, 24), sx, y, 13, ink); y -= 30; }
      if (data.name) { dr(cut(data.name, 24), sx, y, 16, ink); page.drawCircle({ x: W - M - 14, y: y + 6, size: 12, borderColor: T.ac, borderWidth: 1 }); dr('印', W - M - 14 - tw('印', 9) / 2, y + 2.5, 9, T.ac); }
    }
    else {
      if (PAT === 'tate_frame') { page.drawRectangle({ x: 48, y: 56, width: W - 96, height: H - 112, borderColor: T.line, borderWidth: 1 }); }
      dr(title, (W - tw(title, 24)) / 2, H - 106, 24, ink);
      var bSz = 16, bStep = bSz * 1.6, colStep = 36;
      var bodyTop = H - 168, colMax = 21;
      var reason = cut(data.reason || '一身上の都合', 30);
      var body = 'このたび' + reason + 'により、来る' + wkK(data.retire_date) + 'をもって退職' + (isWish ? 'いたしたく、ここにお願い申し上げます。' : 'いたします。');
      var cols = vsplit(body, colMax);
      var hasTo = !!(data.to_company || data.to_title || data.to_name);
      // 全列の幅を先に計算し、用紙の左右中央に配置
      var units = 1 + cols.length + 0.5 + 1.15 + (data.dept ? 0.95 : 0) + 1.5 + (data.to_company ? 1 : 0) + (hasTo ? 0 : -1.5);
      var x = Math.min(W - 96, W / 2 + (units * colStep) / 2);
      vc('私事', x, bodyTop, bSz, bStep); x -= colStep;
      cols.forEach(function (col) { vc(col, x, bodyTop, bSz, bStep); x -= colStep; });
      x -= colStep * 0.5;
      var sigTop = bodyTop - bStep * 2.2;
      vc(wkK(data.submit_date), x, sigTop, 14, 14 * 1.6); x -= colStep * 1.15;
      if (data.dept) { vc(cut(data.dept, 15), x, sigTop + bStep * 0.5, 12.5, 12.5 * 1.6); x -= colStep * 0.95; }
      var ny = vc(cut(data.name || '', 14), x, sigTop, 16.5, 16.5 * 1.55);
      if (data.name) { page.drawCircle({ x: x, y: ny - 13, size: 11, borderColor: T.ac, borderWidth: 1 }); dr('印', x - tw('印', 8) / 2, ny - 17, 8, T.ac); }
      x -= colStep * 1.5;
      var toTop = bodyTop;
      if (data.to_company) { vc(cut(data.to_company, 22), x, toTop, 15.5, 15.5 * 1.58); x -= colStep; }
      var toLine = [data.to_title, data.to_name].filter(Boolean).join('　');
      if (toLine) { vc(cut(toLine, 22) + '　殿', x, toTop, 15.5, 15.5 * 1.58); }
      else if (data.to_company) { var cl = cut(data.to_company, 22).length; vc('殿', x, toTop - 15.5 * 1.58 * Math.max(1, cl - 2), 15.5, 15.5 * 1.58); }
    }
    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, (isWish ? '退職願' : '退職届') + '.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }


  // ---- 汎用ドキュメント（見出し＋本文／テーブル／ブロック・自動改ページ）----
  async function renderGeneric(spec) {
    await ensureLib();
    spec = spec || {};
    var P = window.PDFLib, rgb = P.rgb;
    var pdf = await P.PDFDocument.create();
    pdf.registerFontkit(window.fontkit);
    var font = await pdf.embedFont(_fontBytes, { subset: false });
    var land = !!spec.landscape;
    var W = land ? 841.89 : 595.28, H = land ? 595.28 : 841.89, M = 54;
    var T = themeCols(spec.theme); var ink = T.ink, mut = T.mut, ac = T.ac, line = T.line, head = T.head, zeb = T.zebra;
    var cur, y;
    function np() { cur = pdf.addPage([W, H]); y = H - M; }
    np();
    function dr(sx, x, yy, sz, col) { cur.drawText(sani(sx), { x: x, y: yy, size: sz, font: font, color: col || ink }); }
    function drR(sx, xr, yy, sz, col) { sx = sani(sx); cur.drawText(sx, { x: xr - font.widthOfTextAtSize(sx, sz), y: yy, size: sz, font: font, color: col || ink }); }
    function twf(sx, sz) { return font.widthOfTextAtSize(sani(sx), sz); }
    function ell(sx, sz, max) { sx = sani(sx); if (twf(sx, sz) <= max) return sx; while (sx.length > 1 && twf(sx + '…', sz) > max) sx = sx.slice(0, -1); return sx + '…'; }
    function need(h) { if (y - h < M) np(); }
    function para(text, size, opt) { opt = opt || {}; var indent = opt.indent || 0, lh = opt.lh || (size + 5), col = opt.col || ink; if (text == null || text === '') { need(lh); dr('—', M + indent, y - size, size, mut); y -= lh; return; } wrapLines(font, size, text, W - 2 * M - indent).forEach(function (l) { need(lh); dr(l, M + indent, y - size, size, col); y -= lh; }); }
    function gap(h) { y -= h; }
    var PAT = spec.pattern || 'bar';
    function section(title) {
      need(32);
      if (PAT === 'band') { cur.drawRectangle({ x: M, y: y - 18, width: W - 2 * M, height: 18, color: T.band }); cur.drawRectangle({ x: M, y: y - 18, width: 3.5, height: 18, color: ac }); dr(title, M + 11, y - 14, 11.5, ink); y -= 34; }
      else if (PAT === 'line') { dr(title, M, y - 14, 12.5, ink); cur.drawLine({ start: { x: M, y: y - 20 }, end: { x: W - M, y: y - 20 }, thickness: 1.2, color: ac }); y -= 38; }
      else { cur.drawRectangle({ x: M, y: y - 16, width: 3.5, height: 14, color: ac }); dr(title, M + 10, y - 14, 12, ink); cur.drawLine({ start: { x: M, y: y - 21 }, end: { x: W - M, y: y - 21 }, thickness: 0.6, color: line }); y -= 38; }
    }
    function table(cols, rows) {
      var x0 = M, tw = W - 2 * M, sumw = 0; cols.forEach(function (c) { sumw += c.w; });
      var xs = [], cx = x0; cols.forEach(function (c) { xs.push(cx); cx += c.w / sumw * tw; });
      var rowH = 20, headH = 20;
      need(headH + rowH);
      cur.drawRectangle({ x: x0, y: y - headH, width: tw, height: headH, color: head });
      cols.forEach(function (c, i) { var w = c.w / sumw * tw; if (c.align === 'r') drR(c.label, xs[i] + w - 8, y - 14, 9, ink); else dr(c.label, xs[i] + 8, y - 14, 9, ink); });
      y -= headH;
      rows.forEach(function (r, ri) {
        need(rowH);
        if (ri % 2 === 1) cur.drawRectangle({ x: x0, y: y - rowH, width: tw, height: rowH, color: zeb });
        cols.forEach(function (c, i) { var w = c.w / sumw * tw; var v = ell(r[i] == null ? '' : String(r[i]), 9, w - 14); if (c.align === 'r') drR(v, xs[i] + w - 8, y - 14, 9, ink); else dr(v, xs[i] + 8, y - 14, 9, ink); });
        cur.drawLine({ start: { x: x0, y: y - rowH }, end: { x: x0 + tw, y: y - rowH }, thickness: 0.5, color: line });
        y -= rowH;
      });
      // 外枠・縦罫
      // (簡易) 下線のみで十分見やすいので省略
    }
    // タイトル
    dr(spec.title || '書類', (W - font.widthOfTextAtSize(sani(spec.title || '書類'), 20)) / 2, y - 18, 20, ink);
    (spec.headerRight || []).forEach(function (l, i) { drR(ell(l, i === 0 ? 10.5 : 11, (W - 2 * M) * 0.45), W - M, y - 6 - i * 15, i === 0 ? 10.5 : 11, i === 0 ? mut : ink); });
    y -= 44;
    if (spec.lead) { dr(ell(spec.lead, 12, W - 2 * M), M, y - 12, 12, ink); y -= 26; }
    (spec.blocks || []).forEach(function (bk) {
      if (!bk) return;
      if (bk.type === 'table') { section(bk.heading); table(bk.cols, bk.rows || []); gap(12); }
      else if (bk.type === 'items') {
        section(bk.heading);
        (bk.items || []).forEach(function (it) {
          need(40);
          cur.drawRectangle({ x: M, y: y - 18, width: W - 2 * M, height: 18, color: zeb });
          dr(it.left || '', M + 6, y - 13, 9.5, mut); dr(it.right || '', M + 160, y - 13, 11, ink); y -= 24;
          if (it.meta) para(it.meta, 9, { col: mut, lh: 14 });
          if (it.detail) para(it.detail, 10, { lh: 15 });
          gap(10);
        });
      }
      else { section(bk.heading); para(bk.body, bk.size || 10.5, { lh: bk.lh || 16 }); gap(10); }
    });
    if (spec.footerRight) { need(22); drR(spec.footerRight, W - M, y - 10, 10.5, ink); }
    var bytes = await pdf.save();
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    _deliver(url, blob, (spec.filename || 'document') + '.pdf');
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  return { get: function (p) { return req(p); }, post: function (p, b) { return req(p, 'POST', b); }, del: function (p) { return req(p, 'DELETE'); }, yen: yen, esc: esc, calc: calc, KINDS: KINDS, kindCfg: kindCfg, invoicePdf: _guardDl(invoicePdf), invoiceFromData: _guardDl(invoiceFromData), resumePdf: _guardDl(resumePdf), letterPdf: _guardDl(letterPdf), careerPdf: _guardDl(careerPdf), resignPdf: _guardDl(renderResign), docPdf: _guardDl(renderGeneric), logout: logout,
    raw: { invoiceFromData: invoiceFromData, resumePdf: resumePdf, letterPdf: letterPdf, careerPdf: careerPdf, resignPdf: renderResign, docPdf: renderGeneric },
    livePreview: livePreview };
})();

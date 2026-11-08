/* Free BizDoc — 確定申告 ブラウザPDFエンジン
   公式PDF（青色申告決算書4枚＋申告書 第一表・第二表）に、計算済みの数値と
   事業者情報を重ねて出力し、6ページの「確定申告一式」として結合する。
   依存: /vendor/pdf-lib-1.17.1.min.js, /vendor/fontkit-1.1.1.umd.min.js,
         /fonts/noto-jp.ttf, aoiro-calc.js, aoiro-fill.js */
(function(){
  var FORM ='/kakutei/forms/aoiro-ippan-r05.pdf';
  var FORMB='/kakutei/forms/aoiro-shinkoku-b-r05.pdf';
  var MAP ='/kakutei/aoiro-ippan-map.json?v=20261107';
  var MAP2='/kakutei/aoiro-ippan-p2-map.json?v=20261107';
  var MAP3='/kakutei/aoiro-ippan-p3-map.json?v=20261108';
  var MAP4='/kakutei/aoiro-ippan-p4-map.json?v=20261108';
  var MAPS1='/kakutei/aoiro-shinkoku-p1-map.json?v=20261108';
  var MAPS2='/kakutei/aoiro-shinkoku-p2-map.json?v=20261108';
  var FONT='/fonts/noto-jp.ttf';
  var _p, _font, _map, _map2, _map3, _map4, _maps1, _maps2, _form, _formb;
  function loadScript(src){return new Promise(function(res,rej){
    var s=document.createElement('script'); s.src=src; s.onload=res; s.onerror=rej;
    document.head.appendChild(s);
  });}
  function fetchJson(u,set){return fetch(u).then(function(r){return r.json();}).then(set);}
  function fetchBuf(u,set){return fetch(u,{cache:'force-cache'}).then(function(r){return r.arrayBuffer();}).then(set);}
  function ready(){
    if(_p) return _p;
    _p=(async function(){
      if(!window.PDFLib)  await loadScript('/vendor/pdf-lib-1.17.1.min.js');
      if(!window.fontkit) await loadScript('/vendor/fontkit-1.1.1.umd.min.js');
      var jobs=[];
      if(!_font) jobs.push(fetchBuf(FONT,function(b){_font=b;}));
      if(!_map)  jobs.push(fetchJson(MAP, function(j){_map=j;}));
      if(!_map2) jobs.push(fetchJson(MAP2,function(j){_map2=j;}));
      if(!_map3) jobs.push(fetchJson(MAP3,function(j){_map3=j;}));
      if(!_map4) jobs.push(fetchJson(MAP4,function(j){_map4=j;}));
      if(!_maps1)jobs.push(fetchJson(MAPS1,function(j){_maps1=j;}));
      if(!_maps2)jobs.push(fetchJson(MAPS2,function(j){_maps2=j;}));
      if(!_form) jobs.push(fetchBuf(FORM, function(b){_form=b;}));
      if(!_formb)jobs.push(fetchBuf(FORMB,function(b){_formb=b;}));
      await Promise.all(jobs);
    })();
    return _p;
  }
  function yen(n){return Number(n||0).toLocaleString('en-US');}
  async function buildPdf(data){
    await ready();
    var P=window.PDFLib, color=P.rgb(0.09,0.11,0.17);
    // ---- 決算書（4枚） ----
    var doc=await P.PDFDocument.load(_form);
    doc.registerFontkit(window.fontkit);
    var font=await doc.embedFont(_font,{subset:false});
    var r=window.AoiroCalc.calc(data);
    window.AoiroFill.fillPage(doc.getPages()[_map.page], font, _map, r.amounts, r.header, color);
    if(_map2 && data.p2){
      var a2=window.AoiroCalc.calcP2(data.p2);
      window.AoiroFill.fillPage(doc.getPages()[_map2.page], font, _map2, a2, {}, color);
    }
    if(_map3 && data.p3){
      window.AoiroFill.fillPage(doc.getPages()[_map3.page], font, _map3, {}, data.p3, color);
    }
    if(_map4 && data.p4){
      var a4=window.AoiroCalc.calcP4(data.p4, r.amounts.G43);
      window.AoiroFill.fillPage(doc.getPages()[_map4.page], font, _map4, a4, {}, color);
    }
    // ---- 申告書 第一表・第二表（2枚） ----
    var sdoc=await P.PDFDocument.load(_formb);
    sdoc.registerFontkit(window.fontkit);
    var sfont=await sdoc.embedFont(_font,{subset:false});
    var sk=data.shinkoku||{};
    var sin={ jigyo:r.amounts.G45, shunyu:r.amounts.G01,
              shaho:sk.shaho, shokibo:sk.shokibo, seimei_pay:sk.seimei_pay,
              jishin_pay:sk.jishin_pay, haiguu:sk.haiguu, fuyou_n:sk.fuyou_n, genzen:sk.genzen };
    var sr=window.AoiroCalc.calcShinkoku(sin);
    var h=data.header||{};
    var sHead={ year:data.year||'', jusho:h.jusho, furigana:h.furigana, shimei:h.shimei,
                shokugyo:h.gyoshu, yago:h.yago, tel:(h.tel_office||h.tel_home||'') };
    window.AoiroFill.fillPage(sdoc.getPages()[_maps1.page], sfont, _maps1, sr.amounts, sHead, color);
    // 第二表：控除の内訳（整合する支払額を記入）
    var shaho=Number(sk.shaho||0);
    var sHead2={ year:data.year||'', jusho:h.jusho, yago:h.yago, furigana:h.furigana, shimei:h.shimei };
    if(shaho>0){ sHead2.shaho_type='国民健康保険・国民年金等'; sHead2.shaho_amt=yen(shaho); sHead2.shaho_amt2=yen(shaho); }
    if(Number(sk.seimei_pay||0)>0) sHead2.seimei_shin=yen(sk.seimei_pay);
    if(Number(sk.jishin_pay||0)>0) sHead2.jishin_amt=yen(sk.jishin_pay);
    window.AoiroFill.fillPage(sdoc.getPages()[_maps2.page], sfont, _maps2, {}, sHead2, color);
    // ---- 6ページに結合 ----
    var out=await P.PDFDocument.create();
    var dp=await out.copyPages(doc, doc.getPageIndices());
    dp.forEach(function(p){ out.addPage(p); });
    var sp=await out.copyPages(sdoc, sdoc.getPageIndices());
    sp.forEach(function(p){ out.addPage(p); });
    var bytes=await out.save();
    bytes.__sr=sr;
    return bytes;
  }
  async function computeShinkoku(data){
    await ready();
    var r=window.AoiroCalc.calc(data);
    var sk=data.shinkoku||{};
    return window.AoiroCalc.calcShinkoku({ jigyo:r.amounts.G45, shunyu:r.amounts.G01,
      shaho:sk.shaho, shokibo:sk.shokibo, seimei_pay:sk.seimei_pay, jishin_pay:sk.jishin_pay,
      haiguu:sk.haiguu, fuyou_n:sk.fuyou_n, genzen:sk.genzen });
  }
  window.AOIRO={
    buildPdf: buildPdf,
    compute:  function(d){ return window.AoiroCalc.calc(d); },
    computeShinkoku: computeShinkoku,
    ready:    ready
  };
})();

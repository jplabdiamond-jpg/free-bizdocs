/* Free BizDoc — 確定申告 ブラウザPDFエンジン
   公式PDF（青色申告決算書4枚＋申告書 第一表・第二表）に、計算済みの数値と
   事業者情報を重ねて出力し、6ページの「確定申告一式」として結合する。
   依存: /vendor/pdf-lib-1.17.1.min.js, /vendor/fontkit-1.1.1.umd.min.js,
         /fonts/noto-jp.ttf, aoiro-calc.js, aoiro-fill.js */
(function(){
  var FORM ='/kakutei/forms/aoiro-ippan-r05.pdf';
  var FORMB='/kakutei/forms/aoiro-shinkoku-b-r05.pdf';
  var FORMC='/kakutei/forms/shushi-ippan-r05.pdf';
  var MAP ='/kakutei/aoiro-ippan-map.json?v=20261107';
  var MAP2='/kakutei/aoiro-ippan-p2-map.json?v=20261107';
  var MAP3='/kakutei/aoiro-ippan-p3-map.json?v=20261108';
  var MAP4='/kakutei/aoiro-ippan-p4-map.json?v=20261108';
  var MAPS1='/kakutei/aoiro-shinkoku-p1-map.json?v=20261109d';
  var MAPS2='/kakutei/aoiro-shinkoku-p2-map.json?v=20261108';
  var MAPC1='/kakutei/shushi-ippan-p1-map.json?v=20261108';
  var MAPC2='/kakutei/shushi-ippan-p2-map.json?v=20261109d';
  var FORMD='/kakutei/forms/aoiro-shinkoku-c-r05.pdf';
  var MAPD='/kakutei/aoiro-shinkoku-c-map.json?v=20261109';
  var FONT='/fonts/noto-jp.ttf';
  var _p, _font, _map, _map2, _map3, _map4, _maps1, _maps2, _mapc1, _mapc2, _mapd, _form, _formb, _formc, _formd;
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
      if(!_mapc1)jobs.push(fetchJson(MAPC1,function(j){_mapc1=j;}));
      if(!_mapc2)jobs.push(fetchJson(MAPC2,function(j){_mapc2=j;}));
      if(!_mapd) jobs.push(fetchJson(MAPD, function(j){_mapd=j;}));
      if(!_form) jobs.push(fetchBuf(FORM, function(b){_form=b;}));
      if(!_formb)jobs.push(fetchBuf(FORMB,function(b){_formb=b;}));
      if(!_formc)jobs.push(fetchBuf(FORMC,function(b){_formc=b;}));
      if(!_formd)jobs.push(fetchBuf(FORMD,function(b){_formd=b;}));
      await Promise.all(jobs);
    })();
    return _p;
  }
  function yen(n){return Number(n||0).toLocaleString('en-US');}
  // 申告書 第一表・第二表（2枚）を作成して返す
  async function buildShinkoku(P,color,data,jigyo,shunyu){
    var sdoc=await P.PDFDocument.load(_formb);
    sdoc.registerFontkit(window.fontkit);
    var sfont=await sdoc.embedFont(_font,{subset:false});
    var sk=data.shinkoku||{}, h=data.header||{};
    var sr=window.AoiroCalc.calcShinkoku(Object.assign({}, sk, { jigyo:jigyo, shunyu:shunyu }));
    var sHead={ year:data.year||'', jusho:h.jusho, furigana:h.furigana, shimei:h.shimei,
                shokugyo:h.gyoshu, yago:h.yago, tel:(h.tel_office||h.tel_home||'') };
    window.AoiroFill.fillPage(sdoc.getPages()[_maps1.page], sfont, _maps1, sr.amounts, sHead, color);
    var shaho=Number(sk.shaho||0);
    var sHead2={ year:data.year||'', jusho:h.jusho, yago:h.yago, furigana:h.furigana, shimei:h.shimei };
    if(shaho>0){ sHead2.shaho_type='国民健康保険・国民年金等'; sHead2.shaho_amt=yen(shaho); sHead2.shaho_amt2=yen(shaho); }
    if(Number(sk.seimei_pay||0)>0) sHead2.seimei_shin=yen(sk.seimei_pay);
    if(Number(sk.jishin_pay||0)>0) sHead2.jishin_amt=yen(sk.jishin_pay);
    window.AoiroFill.fillPage(sdoc.getPages()[_maps2.page], sfont, _maps2, {}, sHead2, color);
    // 第三表（分離課税）：該当があれば作成
    var ddoc=null;
    if(sr.dai3 && sr.dai3.has){
      ddoc=await P.PDFDocument.load(_formd);
      ddoc.registerFontkit(window.fontkit);
      var dfont=await ddoc.embedFont(_font,{subset:false});
      var dHead={ year:data.year||'', jusho:h.jusho, yago:h.yago, furigana:h.furigana, shimei:h.shimei };
      window.AoiroFill.fillPage(ddoc.getPages()[_mapd.page], dfont, _mapd, sr.dai3.amounts, dHead, color);
    }
    return {doc:sdoc, sr:sr, dai3doc:ddoc};
  }
  async function buildPdf(data){
    await ready();
    var P=window.PDFLib, color=P.rgb(0.09,0.11,0.17);
    var out=await P.PDFDocument.create();
    var sr;
    if((data.mode||'青色')==='白色'){
      // ---- 白色：収支内訳書（1枚目） ----
      var cdoc=await P.PDFDocument.load(_formc);
      cdoc.registerFontkit(window.fontkit);
      var cfont=await cdoc.embedFont(_font,{subset:false});
      var h=data.header||{};
      var cr=window.AoiroCalc.calcShushi({ uriage:data.uriage, kaji:data.kaji, sonota:data.sonota,
        kisho:data.kisho, shiire:data.shiire, kimatsu:data.kimatsu, exp:data.exp, senju:data.senju,
        header:{ year:data.year||'', jusho:h.jusho, jigyosho:h.jigyosho, gyoshu:h.gyoshu, yago:h.yago,
                 furigana:h.furigana, shimei:h.shimei, tel_home:(h.tel_home||h.tel_office||''), kanyu:h.kanyu } });
      window.AoiroFill.fillPage(cdoc.getPages()[_mapc1.page], cfont, _mapc1, cr.amounts, cr.header, color);
      // ---- 収支内訳書2枚目（氏名・減価償却・利子割引料/地代家賃の内訳） ----
      var p2h={ shimei:h.shimei };
      var p3=data.p3||{};
      Object.keys(p3).forEach(function(k){ if(k.charAt(0)==='d') p2h[k]=p3[k]; });
      // 本年分の償却費合計＝普通償却費（特別償却なし）として複製
      for(var i=0;i<6;i++){ if(p3['d'+i+'_shokyaku']) p2h['d'+i+'_goukei']=p3['d'+i+'_shokyaku']; }
      var s2=data.shushi2||{};
      Object.keys(s2).forEach(function(k){ p2h[k]=s2[k]; });
      window.AoiroFill.fillPage(cdoc.getPages()[_mapc2.page], cfont, _mapc2, {}, p2h, color);
      // ---- 申告書（事業所得＝収支内訳書 G39、収入＝G05） ----
      var sb=await buildShinkoku(P,color,data,cr.amounts.G39,cr.amounts.G05); sr=sb.sr;
      (await out.copyPages(cdoc, [0,1])).forEach(function(p){ out.addPage(p); });
      (await out.copyPages(sb.doc, sb.doc.getPageIndices())).forEach(function(p){ out.addPage(p); });
      if(sb.dai3doc){ (await out.copyPages(sb.dai3doc, [0])).forEach(function(p){ out.addPage(p); }); }
    } else {
      // ---- 青色：決算書（4枚） ----
      var doc=await P.PDFDocument.load(_form);
      doc.registerFontkit(window.fontkit);
      var font=await doc.embedFont(_font,{subset:false});
      var r=window.AoiroCalc.calc(data);
      window.AoiroFill.fillPage(doc.getPages()[_map.page], font, _map, r.amounts, r.header, color);
      if(_map2 && data.p2){
        window.AoiroFill.fillPage(doc.getPages()[_map2.page], font, _map2, window.AoiroCalc.calcP2(data.p2), {}, color);
      }
      if(_map3 && data.p3){
        window.AoiroFill.fillPage(doc.getPages()[_map3.page], font, _map3, {}, data.p3, color);
      }
      if(_map4 && data.p4){
        window.AoiroFill.fillPage(doc.getPages()[_map4.page], font, _map4, window.AoiroCalc.calcP4(data.p4, r.amounts.G43), {}, color);
      }
      // ---- 申告書（事業所得＝決算書 G45、収入＝G01） ----
      var sb2=await buildShinkoku(P,color,data,r.amounts.G45,r.amounts.G01); sr=sb2.sr;
      (await out.copyPages(doc, doc.getPageIndices())).forEach(function(p){ out.addPage(p); });
      (await out.copyPages(sb2.doc, sb2.doc.getPageIndices())).forEach(function(p){ out.addPage(p); });
      if(sb2.dai3doc){ (await out.copyPages(sb2.dai3doc, [0])).forEach(function(p){ out.addPage(p); }); }
    }
    var bytes=await out.save();
    bytes.__sr=sr;
    return bytes;
  }
  async function computeShinkoku(data){
    await ready();
    var r=window.AoiroCalc.calc(data);
    var sk=data.shinkoku||{};
    return window.AoiroCalc.calcShinkoku(Object.assign({}, sk, { jigyo:r.amounts.G45, shunyu:r.amounts.G01 }));
  }
  window.AOIRO={
    buildPdf: buildPdf,
    compute:  function(d){ return window.AoiroCalc.calc(d); },
    computeShinkoku: computeShinkoku,
    ready:    ready
  };
})();

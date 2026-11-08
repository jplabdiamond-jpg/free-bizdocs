/* Free BizDoc — 青色申告決算書(一般用) ブラウザPDFエンジン
   公式の損益計算書PDFに、計算済みの数値と事業者情報を重ねて出力する。
   依存: /vendor/pdf-lib-1.17.1.min.js, /vendor/fontkit-1.1.1.umd.min.js,
         /fonts/noto-jp.ttf, aoiro-calc.js, aoiro-fill.js */
(function(){
  var FORM='/kakutei/forms/aoiro-ippan-r05.pdf';
  var MAP ='/kakutei/aoiro-ippan-map.json?v=20261107';
  var MAP2='/kakutei/aoiro-ippan-p2-map.json?v=20261107';
  var MAP3='/kakutei/aoiro-ippan-p3-map.json?v=20261108';
  var FONT='/fonts/noto-jp.ttf';
  var _p, _font, _map, _map2, _map3, _form;
  function loadScript(src){return new Promise(function(res,rej){
    var s=document.createElement('script'); s.src=src; s.onload=res; s.onerror=rej;
    document.head.appendChild(s);
  });}
  function ready(){
    if(_p) return _p;
    _p=(async function(){
      if(!window.PDFLib)  await loadScript('/vendor/pdf-lib-1.17.1.min.js');
      if(!window.fontkit) await loadScript('/vendor/fontkit-1.1.1.umd.min.js');
      var jobs=[];
      if(!_font) jobs.push(fetch(FONT,{cache:'force-cache'}).then(function(r){return r.arrayBuffer();}).then(function(b){_font=b;}));
      if(!_map)  jobs.push(fetch(MAP).then(function(r){return r.json();}).then(function(j){_map=j;}));
      if(!_map2) jobs.push(fetch(MAP2).then(function(r){return r.json();}).then(function(j){_map2=j;}));
      if(!_map3) jobs.push(fetch(MAP3).then(function(r){return r.json();}).then(function(j){_map3=j;}));
      if(!_form) jobs.push(fetch(FORM).then(function(r){return r.arrayBuffer();}).then(function(b){_form=b;}));
      await Promise.all(jobs);
    })();
    return _p;
  }
  async function buildPdf(data){
    await ready();
    var P=window.PDFLib;
    var doc=await P.PDFDocument.load(_form);
    doc.registerFontkit(window.fontkit);
    var font=await doc.embedFont(_font,{subset:false});
    var page=doc.getPages()[_map.page];
    var color=P.rgb(0.09,0.11,0.17);
    var r=window.AoiroCalc.calc(data);
    window.AoiroFill.fillPage(page, font, _map, r.amounts, r.header, color);
    // 2枚目：月別の売上・仕入
    if(_map2 && data.p2){
      var a2=window.AoiroCalc.calcP2(data.p2);
      window.AoiroFill.fillPage(doc.getPages()[_map2.page], font, _map2, a2, {}, color);
    }
    // 3枚目：減価償却費の計算（データはフォーマット済み文字列）
    if(_map3 && data.p3){
      window.AoiroFill.fillPage(doc.getPages()[_map3.page], font, _map3, {}, data.p3, color);
    }
    return await doc.save();
  }
  window.AOIRO={
    buildPdf: buildPdf,
    compute:  function(d){ return window.AoiroCalc.calc(d); },
    ready:    ready
  };
})();

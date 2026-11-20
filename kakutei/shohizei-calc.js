/* Free BizDoc — 消費税（個人事業者・インボイス）納付税額の概算ロジック（UMD: ブラウザ/Node共用）
   割戻し計算による目安。国税7.8%/6.24%＋地方消費税(譲渡割=国税×22/78)。端数は申告書に準じ切捨て。 */
(function(root,factory){
  if(typeof module==='object'&&module.exports){module.exports=factory();}
  else{root.ShohiCalc=factory();}
}(typeof self!=='undefined'?self:this,function(){
  function N(v){ v=parseInt(String(v==null?0:v).replace(/[^0-9]/g,''),10); return isNaN(v)?0:v; }
  function floor1000(n){ return Math.floor(n/1000)*1000; }
  function floor100(n){ return Math.floor(n/100)*100; }

  // 税込→税抜（割戻し）。税抜入力ならそのまま
  function nuki(amount, rate, basis){ amount=N(amount);
    return basis==='incl' ? Math.floor(amount/(1+rate)) : amount; }

  // 売上側：税抜課税売上・課税標準額・売上の消費税額（国税）
  function uriage(g){
    var nStd=nuki(g.std, 0.10, g.basis);     // 税抜（標準10%分）
    var nRed=nuki(g.red, 0.08, g.basis);     // 税抜（軽減8%分）
    var nukiTotal=nStd+nRed;
    var csStd=floor1000(nStd), csRed=floor1000(nRed);
    var kazeiHyojun=floor1000(nukiTotal);    // 第二表①（概算）
    // 売上の消費税額（国税）：標準7.8%・軽減6.24%
    var uriTax=Math.floor(csStd*0.078)+Math.floor(csRed*0.0624);
    return {nStd:nStd, nRed:nRed, nukiTotal:nukiTotal, kazeiHyojun:kazeiHyojun, uriTax:uriTax};
  }

  // 仕入側（本則）：課税仕入の消費税額（国税）
  function shiireTax(g){
    var nStd=nuki(g.kaStd, 0.10, g.basis), nRed=nuki(g.kaRed, 0.08, g.basis);
    return Math.floor(floor1000(nStd)*0.078)+Math.floor(floor1000(nRed)*0.0624);
  }

  // 1方式の計算
  function calcMethod(g, method){
    var u=uriage(g);
    var uriTax=u.uriTax, kojo=0, kanpu=false;
    if(method==='nitwari'){ kojo=Math.floor(uriTax*0.8); }          // 2割特例：控除＝売上税額の80%
    else if(method==='kani'){ var r=g.minashi||0.7; kojo=Math.floor(uriTax*r); }
    else { kojo=shiireTax(g); }                                      // 本則
    var sashihiki=uriTax-kojo;                                       // 差引（国税）
    if(sashihiki<0){ kanpu=true; }
    // 2割特例・簡易課税は控除が売上税額を超えない前提（還付なし）
    if(method!=='honsoku') sashihiki=Math.max(0, sashihiki);
    var kokuzei=floor100(Math.max(0,sashihiki));                     // 国税（百円未満切捨て）
    var chihou=floor100(kokuzei*22/78);                             // 地方消費税（譲渡割）
    return {
      nukiTotal:u.nukiTotal, kazeiHyojun:u.kazeiHyojun, uriTax:uriTax,
      kojo:kojo, kokuzei:kokuzei, chihou:chihou, total:kokuzei+chihou, kanpu:(method==='honsoku'&&kanpu)
    };
  }

  function calc(g){ g=g||{}; return calcMethod(g, g.method||'nitwari'); }

  // 3方式の納付合計を比較（還付＝0として比較表示）
  function compareAll(g){
    return {
      nitwari: calcMethod(g,'nitwari').total,
      kani: calcMethod(g,'kani').total,
      honsoku: Math.max(0, calcMethod(g,'honsoku').total)
    };
  }

  return {calc:calc, calcMethod:calcMethod, compareAll:compareAll, uriage:uriage, shiireTax:shiireTax};
}));

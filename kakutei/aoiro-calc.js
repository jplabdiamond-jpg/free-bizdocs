/* Free BizDoc — 青色申告決算書(一般用) 損益計算書の計算ロジック（UMD: ブラウザ/Node共用） */
(function(root,factory){
  if(typeof module==='object'&&module.exports){module.exports=factory();}
  else{root.AoiroCalc=factory();}
}(typeof self!=='undefined'?self:this,function(){
  // 損益計算書の経費科目（印字コード -> 名称）
  var EXPENSES=[
    ['G08','租税公課'],['G09','荷造運賃'],['G10','水道光熱費'],['G11','旅費交通費'],
    ['G12','通信費'],['G13','広告宣伝費'],['G14','接待交際費'],['G15','損害保険料'],
    ['G16','修繕費'],['G17','消耗品費'],['G18','減価償却費'],['G19','福利厚生費'],
    ['G20','給料賃金'],['G21','外注工賃'],['G22','利子割引料'],['G23','地代家賃'],
    ['G24','貸倒金'],['G31','雑費']
  ];
  function N(v){v=Number(v); return isFinite(v)?Math.round(v):0;}
  function calc(d){
    d=d||{}; var a={};
    var uriage=N(d.uriage), kisho=N(d.kisho), shiire=N(d.shiire), kimatsu=N(d.kimatsu);
    a.G01=uriage; a.G02=kisho; a.G03=shiire;
    var shokei=kisho+shiire; a.G04=shokei;                 // 小計(2+3)
    a.G05=kimatsu;
    var genka=shokei-kimatsu; a.G06=genka;                 // 差引原価(4-5)
    var uriageSoneki=uriage-genka; a.G07=uriageSoneki;      // 差引金額(1-6)
    var exp=d.exp||{}, keihi=0;
    EXPENSES.forEach(function(e){ var v=N(exp[e[0]]); a[e[0]]=v; keihi+=v; });
    a.G32=keihi;                                           // 経費 計
    var sashihiki=uriageSoneki-keihi; a.G33=sashihiki;      // 差引金額(7-32)
    var km=d.kurimodoshi||{}, kn=d.kurinyu||{};
    a.G34=N(km.G34); a.G35=N(km.G35); a.G36=N(km.G36);
    var modoshi=a.G34+a.G35+a.G36; a.G37=modoshi;           // 繰戻額等 計
    a.G38=N(kn.G38); a.G39=N(kn.G39); a.G40=N(kn.G40); a.G41=N(kn.G41);
    var nyu=a.G38+a.G39+a.G40+a.G41; a.G42=nyu;             // 繰入額等 計
    var shotokuMae=sashihiki+modoshi-nyu; a.G43=shotokuMae; // 青色申告特別控除前の所得金額
    var kojoReq=N(d.kojo!=null?d.kojo:100000);
    var kojo=Math.max(0, Math.min(kojoReq, Math.max(0,shotokuMae)));
    a.G44=kojo;                                            // 青色申告特別控除額
    a.G45=shotokuMae-kojo;                                 // 所得金額(43-44)
    return {amounts:a, header:(d.header||{})};
  }
  return {calc:calc, EXPENSES:EXPENSES};
}));

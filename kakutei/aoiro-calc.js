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
  // 2枚目：月別の売上（収入）金額及び仕入金額
  function calcP2(p2){
    p2=p2||{}; var a={};
    var uri=p2.uri||[], shi=p2.shi||[], su=0, ss=0, i;
    for(i=0;i<12;i++){ var u=N(uri[i]); a['G'+('0'+(i+1)).slice(-2)]=u; su+=u; }      // G01..G12 月別売上
    for(i=0;i<12;i++){ var s=N(shi[i]); a['G'+(17+i)]=s; ss+=s; }                     // G17..G28 月別仕入
    a.G13=N(p2.kaji);                                                                  // 家事消費等
    a.G14=N(p2.zatsu);                                                                 // 雑収入
    a.G15=su+a.G13+a.G14;                                                              // 売上(収入)計
    a.G16=N(p2.keigenUri);                                                             // うち軽減税率対象(売上)
    a.G29=ss;                                                                          // 仕入 計
    a.G30=N(p2.keigenShi);                                                             // うち軽減税率対象(仕入)
    return a;
  }
  // 4枚目：貸借対照表（資産負債調）。p4={code:値}、g43=青色申告特別控除前の所得金額
  var P4={
    assetFirst:['G01','G02','G03','G04','G05','G06','G07','G08','G09','G10','G11','G12','G13','G14','G15','G16'],
    assetLast :['G25','G26','G27','G28','G29','G30','G31','G32','G33','G34','G35','G36','G37','G38','G39','G40'],
    liabFirst :['G50','G51','G52','G53','G54','G55','G63'],
    liabLast  :['G73','G74','G75','G76','G77','G78','G86']
  };
  function calcP4(p4, g43){
    p4=p4||{}; var a={};
    var all=P4.assetFirst.concat(P4.assetLast,P4.liabFirst,P4.liabLast,['G48','G71','G94','G95']);
    all.forEach(function(c){ a[c]=N(p4[c]); });
    a.G96=N(g43);                                   // 青色申告特別控除前の所得金額（期末）
    function sum(arr){var t=0;arr.forEach(function(c){t+=a[c]||0;});return t;}
    a.G24=sum(P4.assetFirst);                        // 資産 期首合計
    a.G49=sum(P4.assetLast)+a.G48;                   // 資産 期末合計（＋事業主貸）
    a.G72=sum(P4.liabFirst)+a.G71;                   // 負債・資本 期首合計（＋元入金）
    a.G97=sum(P4.liabLast)+a.G94+a.G95+a.G96;        // 負債・資本 期末合計（＋事業主借＋元入金＋所得）
    return a;
  }
  // 申告書 第一表：事業所得・主要所得控除から課税所得と税額目安を計算（令和5年分 総合課税）
  function incomeTax(a){ // a=課税される所得金額（1000円未満切捨て済み）
    var t;
    if(a< 1950000) t=a*0.05;
    else if(a< 3300000) t=a*0.10-97500;
    else if(a< 6950000) t=a*0.20-427500;
    else if(a< 9000000) t=a*0.23-636000;
    else if(a<18000000) t=a*0.33-1536000;
    else if(a<40000000) t=a*0.40-2796000;
    else t=a*0.45-4796000;
    return Math.floor(Math.max(0,t));
  }
  function kisoKojo(gokei){ // 基礎控除（合計所得金額ベース）
    if(gokei<=24000000) return 480000;
    if(gokei<=24500000) return 320000;
    if(gokei<=25000000) return 160000;
    return 0;
  }
  function seimeiKojo(pay){ // 生命保険料控除（新制度・一般、1区分, 上限4万）
    pay=N(pay); if(pay<=0) return 0;
    if(pay<=20000) return pay;
    if(pay<=40000) return Math.floor(pay*0.5+10000);
    if(pay<=80000) return Math.floor(pay*0.25+20000);
    return 40000;
  }
  function jishinKojo(pay){ pay=N(pay); return Math.min(pay,50000); } // 地震保険料控除（上限5万）
  function calcShinkoku(d){
    d=d||{}; var a={};
    var jigyo=N(d.jigyo);                       // 事業所得（決算書 G45）
    var shunyu=N(d.shunyu);                      // 売上（収入）金額（決算書 G01）
    var gokei=jigyo;                             // 総所得金額（コア版：事業所得のみ）
    a.G09=shunyu;                                // 収入 事業・営業等
    a.G39=jigyo;                                 // 所得 事業・営業等（①）
    a.G50=gokei;                                 // 合計（⑫）
    var shaho=N(d.shaho), shokibo=N(d.shokibo);
    var seimei=seimeiKojo(d.seimei_pay);
    var jishin=jishinKojo(d.jishin_pay);
    var haiguu=(d.haiguu && gokei<=9000000) ? 380000 : 0;  // 配偶者控除（本人合計所得900万以下・一般）
    var fuyou=N(d.fuyou_n)*380000;               // 扶養控除（一般・1人38万）
    var kiso=kisoKojo(gokei);
    a.G51=shaho; a.G52=shokibo; a.G53=seimei; a.G54=jishin;
    a.G57=haiguu; a.G58=fuyou; a.G59=kiso;
    var kojoKei=shaho+shokibo+seimei+jishin+haiguu+fuyou+kiso;
    a.G60=kojoKei;                               // ⑬〜㉔の計（㉕）
    a.G64=kojoKei;                               // 合計（㉙）
    var kazei=Math.max(0, gokei-kojoKei);
    kazei=Math.floor(kazei/1000)*1000;           // 課税所得（1000円未満切捨て）
    a.G65=kazei;                                 // 課税される所得金額（㉚）
    var zei=incomeTax(kazei);
    a.G66=zei;                                   // 上の㉚に対する税額（㉛）
    a.G72=zei;                                   // 差引所得税額（㊶）配当控除・住宅控除なし
    a.G74=zei;                                   // 再差引所得税額（基準所得税額）（㊸）
    var fukko=Math.floor(zei*0.021);
    a.G75=fukko;                                 // 復興特別所得税額（㊹）
    var goukei=zei+fukko;
    a.G76=goukei;                                // 所得税及び復興特別所得税の額（㊺）
    var genzen=N(d.genzen);
    a.G78=genzen;                                // 源泉徴収税額（㊽）
    var nouzei=goukei-genzen;                    // 申告納税額（㊾）
    a.G79=Math.abs(nouzei);                      // セルには絶対値（符号は注記で案内）
    var dai3=(nouzei>0)?Math.floor(nouzei/100)*100:0;
    a.G81=dai3;                                  // 第3期分の税額 納める税金（㊿）
    return {amounts:a, kanpu:(nouzei<0?-nouzei:0), nouzei:nouzei, kazei:kazei, kojoKei:kojoKei, gokei:gokei};
  }
  return {calc:calc, calcP2:calcP2, calcP4:calcP4, calcShinkoku:calcShinkoku, EXPENSES:EXPENSES};
}));

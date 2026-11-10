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
  // 配偶者控除・配偶者特別控除（令和5年分）。honIncome=本人の合計所得、haiIncome=配偶者の合計所得
  function haiguuKojo(opt, honIncome){
    if(!opt || !opt.has) return 0;
    if(honIncome>10000000) return 0;             // 本人合計所得1000万超は対象外
    // 本人所得の段階（0:≤900万, 1:900-950万, 2:950-1000万）
    var tier=(honIncome<=9000000)?0:(honIncome<=9500000?1:2);
    var hi=N(opt.income);                         // 配偶者の合計所得
    var old=!!opt.old;                            // 老人配偶者（70歳以上）
    if(hi<=480000){                               // 配偶者控除
      return old ? [480000,320000,160000][tier] : [380000,260000,130000][tier];
    }
    // 配偶者特別控除（48万超133万以下）
    var tbl=[ // [上限(円), [≤900,900-950,950-1000]]
      [950000,[380000,260000,130000]],[1000000,[360000,240000,120000]],
      [1050000,[310000,210000,110000]],[1100000,[260000,180000,90000]],
      [1150000,[210000,140000,70000]],[1200000,[160000,110000,60000]],
      [1250000,[110000,80000,40000]],[1300000,[60000,40000,20000]],
      [1330000,[30000,20000,10000]]
    ];
    for(var i=0;i<tbl.length;i++){ if(hi<=tbl[i][0]) return tbl[i][1][tier]; }
    return 0;                                     // 133万超
  }
  function fuyouKojo(opt){                         // 扶養控除（区分別）
    opt=opt||{};
    return N(opt.ippan)*380000 + N(opt.tokutei)*630000 + N(opt.rojin)*480000 + N(opt.doukyo)*580000;
  }
  // 譲渡の内訳（土地建物）→ 短期/長期の所得・差引合計・特別控除合計
  function joutoSum(bunri){
    var t=N(bunri.tanki), c=N(bunri.chouki), sabikiKei=0, tokubetsuKei=0, jo=bunri.jouto||[], used=false;
    if(jo.length){
      t=0; c=0;
      for(var k=0;k<jo.length;k++){
        var j=jo[k], shu=N(j.shunyu), kh=N(j.keihi), tk=N(j.tokubetsu);
        if(!(shu||kh||tk)) continue;
        used=true;
        var sabiki=Math.max(0,shu-kh), sho=Math.max(0,sabiki-tk);
        sabikiKei+=sabiki; tokubetsuKei+=tk;
        if(j.kubun==='長期') c+=sho; else t+=sho;
      }
    }
    return {tanki:t, chouki:c, sabiki:sabikiKei, tokubetsu:tokubetsuKei, used:used};
  }
  // 山林所得：収入−必要経費−特別控除（最高50万）＝所得金額
  function sanrinCalc(s){ s=s||{}; var shu=N(s.shunyu), kh=N(s.keihi);
    var sabiki=Math.max(0, shu-kh);
    var tok=Math.min(500000, sabiki);            // 山林所得の特別控除（最高50万円）
    return {shunyu:shu, keihi:kh, tokubetsu:tok, shotoku:Math.max(0, sabiki-tok)}; }
  // 退職所得：退職所得控除を差し引き、原則1/2課税（役員等で勤続5年以下は1/2なし）
  function taishokuCalc(t){ t=t||{}; var shu=N(t.shunyu), yrsRaw=N(t.years);
    if(shu<=0) return {shunyu:0, years:0, kojo:0, shotoku:0, half:true};
    var y=Math.max(1, Math.ceil(yrsRaw));        // 勤続年数（1年未満は切上げ）
    var kojo = (y<=20) ? 400000*y : 8000000+700000*(y-20);
    kojo=Math.max(800000, kojo);                 // 最低80万円
    var base=Math.max(0, shu-kojo);
    var half = !(t.yakuin5);                      // 役員等かつ勤続5年以下は1/2なし
    var sho = half ? Math.floor(base/2) : base;
    return {shunyu:shu, years:y, kojo:kojo, shotoku:sho, half:half}; }
  // 申告書第三表（分離課税用）：主要な分離所得の税額を計算し、第一表㉛へ合算
  // soogoAll=総合課税の合計(第一表⑫/G50)、kojoKei=所得控除(第一表㉙/G64)
  function calcDai3(bunri, soogoAll, kojoKei){
    bunri=bunri||{}; var a={};
    var js=joutoSum(bunri), tanki=js.tanki, chouki=js.chouki, jouto=bunri.jouto||[];
    if(js.used){ a.G65=js.sabiki; a.G66=js.tokubetsu; }  // 差引金額・特別控除額の合計
    var ippanKabu=N(bunri.ippan_kabu), jojoKabu=N(bunri.jojo_kabu);
    var haito=N(bunri.haito), sakimono=N(bunri.sakimono);
    var kabuAll=ippanKabu+jojoKabu;
    var sr=sanrinCalc(bunri.sanrin), tx=taishokuCalc(bunri.taishoku);
    // 収入金額
    a.G28=sr.shunyu; a.G29=tx.shunyu;             // ㉘山林・㉙退職の収入金額
    // 所得金額
    a.G30=tanki; a.G32=chouki; a.G35=ippanKabu; a.G36=jojoKabu; a.G37=haito; a.G38=sakimono;
    a.G39=sr.shotoku; a.G40=tx.shotoku;           // ㊵山林・㊶退職の所得金額
    a.G41=soogoAll; a.G42=kojoKei;                // ⑫総合合計・㉙所得控除
    function fl(n){return Math.floor(Math.max(0,n)/1000)*1000;}
    var rem=Math.max(0, kojoKei-soogoAll);        // 総合で使い切れなかった所得控除を分離へ充当
    function ap(inc){ var k=Math.max(0,inc-rem); rem=Math.max(0,rem-inc); return k; }
    a.G43=fl(Math.max(0, soogoAll-kojoKei));      // 総合課税分の課税所得（第一表㉚と同じ）
    a.G44=fl(ap(tanki));                          // 短期譲渡
    a.G45=fl(ap(chouki));                         // 長期譲渡
    a.G46=fl(ap(kabuAll));                        // 株式等譲渡
    a.G47=fl(ap(haito));                          // 上場配当
    a.G48=fl(ap(sakimono));                       // 先物取引
    a.G49=fl(ap(sr.shotoku));                     // 課税山林所得
    a.G50=fl(ap(tx.shotoku));                     // 課税退職所得
    a.G51=incomeTax(a.G43);                       // 総合分の税額
    a.G52=Math.floor(a.G44*0.30);                 // 短期譲渡30%
    a.G53=Math.floor(a.G45*0.15);                 // 長期譲渡15%
    a.G54=Math.floor(a.G46*0.15);                 // 株式等15%
    a.G55=Math.floor(a.G47*0.15);                 // 上場配当15%
    a.G56=Math.floor(a.G48*0.15);                 // 先物15%
    a.G57=incomeTax(Math.floor(a.G49/5))*5;       // 山林（5分5乗）
    a.G58=incomeTax(a.G50);                        // 退職（1/2後の課税退職所得に通常税率）
    a.G59=a.G51+a.G52+a.G53+a.G54+a.G55+a.G56+a.G57+a.G58;  // 93＝第一表㉛へ転記
    a.G67=N(bunri.jojo_genzen);                   // 上場株式等の源泉徴収税額
    var has=(tanki+chouki+kabuAll+haito+sakimono+sr.shotoku+tx.shotoku)>0;
    return {amounts:a, total:a.G59, genzen:a.G67, has:has, jouto:jouto,
      sanrin:sr, taishoku:tx};
  }
  // 個人住民税の概算（所得割10%＋均等割＋分離課税分）。住民税は所得税と控除額が異なる
  function seimeiJuminKojo(pay){ pay=N(pay); if(pay<=0)return 0;
    if(pay<=12000)return pay; if(pay<=32000)return Math.floor(pay*0.5+6000);
    if(pay<=56000)return Math.floor(pay*0.25+14000); return 28000; }
  function kisoJumin(gokei){ if(gokei<=24000000)return 430000; if(gokei<=24500000)return 290000; if(gokei<=25000000)return 150000; return 0; }
  function haiguuJumin(opt, hon){ if(!opt||!opt.has)return 0; if(hon>10000000)return 0;
    var t=(hon<=9000000)?0:(hon<=9500000?1:2), hi=N(opt.income), old=!!opt.old;
    if(hi<=480000) return old?[380000,260000,130000][t]:[330000,220000,110000][t];
    var tb=[[950000,[330000,220000,110000]],[1000000,[330000,220000,110000]],[1050000,[310000,210000,110000]],[1100000,[260000,180000,90000]],[1150000,[210000,140000,70000]],[1200000,[160000,110000,60000]],[1250000,[110000,80000,40000]],[1300000,[60000,40000,20000]],[1330000,[30000,20000,10000]]];
    for(var i=0;i<tb.length;i++) if(hi<=tb[i][0]) return tb[i][1][t]; return 0; }
  function fuyouJumin(o){ o=o||{}; return N(o.ippan)*330000+N(o.tokutei)*450000+N(o.rojin)*380000+N(o.doukyo)*450000; }
  function calcJuminzei(d, gokei){
    d=d||{};
    var kojo=N(d.shaho)+N(d.shokibo)+seimeiJuminKojo(d.seimei_pay)+Math.min(N(d.jishin_pay),25000)
      +haiguuJumin({has:d.haiguu,income:d.haiguu_income,old:d.haiguu_old},gokei)
      +fuyouJumin({ippan:d.fuyou_ippan,tokutei:d.fuyou_tokutei,rojin:d.fuyou_rojin,doukyo:d.fuyou_doukyo})
      +kisoJumin(gokei)+N(d.zatsuson);
    var kazei=Math.max(0,gokei-kojo); kazei=Math.floor(kazei/1000)*1000;
    var wari=Math.floor(kazei*0.10);
    // 調整控除（人的控除差）
    var jinteki=((gokei<=25000000)?50000:0)
      +((d.haiguu&&gokei<=10000000&&N(d.haiguu_income)<=480000)?50000:0)
      +N(d.fuyou_ippan)*50000+N(d.fuyou_tokutei)*180000+N(d.fuyou_rojin)*100000+N(d.fuyou_doukyo)*130000;
    var chousei=(kazei<=2000000)?Math.floor(Math.min(jinteki,kazei)*0.05):Math.floor(Math.max(jinteki-(kazei-2000000),50000)*0.05);
    wari=Math.max(0,wari-chousei);
    var b=d.bunri||{}, js=joutoSum(b), sanr=sanrinCalc(b.sanrin);
    // 山林所得は住民税も5分5乗だが税率一律10%のため課税山林×10%で同値（退職は原則特別徴収済みのため概算に含めない）
    var bunri=Math.floor(N(b.jojo_kabu)*0.05)+Math.floor(N(b.haito)*0.05)+Math.floor(N(b.ippan_kabu)*0.05)
      +Math.floor(N(b.sakimono)*0.05)+Math.floor(js.chouki*0.05)+Math.floor(js.tanki*0.09)
      +Math.floor(sanr.shotoku*0.10);
    var kintou=5000;
    return {total:wari+bunri+kintou, shotokuwari:wari, bunriWari:bunri, kintou:kintou, kazei:kazei};
  }
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
    var haiguu=haiguuKojo({has:d.haiguu, income:d.haiguu_income, old:d.haiguu_old}, gokei);
    var fuyou=fuyouKojo({ippan:d.fuyou_ippan, tokutei:d.fuyou_tokutei, rojin:d.fuyou_rojin, doukyo:d.fuyou_doukyo});
    var kiso=kisoKojo(gokei);
    a.G51=shaho; a.G52=shokibo; a.G53=seimei; a.G54=jishin;
    a.G57=haiguu; a.G58=fuyou; a.G59=kiso;
    var kojoKei=shaho+shokibo+seimei+jishin+haiguu+fuyou+kiso;
    a.G60=kojoKei;                               // ⑬〜㉔の計（㉕）
    var zatsuson=N(d.zatsuson);                  // 雑損控除（㉖）
    a.G61=zatsuson;
    kojoKei=kojoKei+zatsuson;                     // 所得控除の合計に雑損を加える
    a.G64=kojoKei;                               // 合計（㉙）
    var kazei=Math.max(0, gokei-kojoKei);
    kazei=Math.floor(kazei/1000)*1000;           // 課税所得（1000円未満切捨て）
    a.G65=kazei;                                 // 課税される所得金額（㉚）
    // 分離課税（第三表）：該当があれば㉛税額を第三表93に差し替え
    var d3=calcDai3(d.bunri, gokei, kojoKei);
    var zei = d3.has ? d3.total : incomeTax(kazei);
    a.G66=zei;                                   // 上の㉚に対する税額 又は第三表の93（㉛）
    var haitou=N(d.haitou_kojo), jutaku=N(d.jutaku_kojo); // 配当控除㉜・住宅借入金等特別控除㉞
    a.G67=haitou; a.G69=jutaku;
    var zei2=Math.max(0, zei-haitou-jutaku);
    a.G72=zei2;                                  // 差引所得税額（㊶）＝㉛−配当控除−住宅控除
    a.G74=zei2;                                  // 再差引所得税額（基準所得税額）（㊸）
    zei=zei2;
    var fukko=Math.floor(zei*0.021);
    a.G75=fukko;                                 // 復興特別所得税額（㊹）
    var goukei=zei+fukko;
    a.G76=goukei;                                // 所得税及び復興特別所得税の額（㊺）
    var genzen=N(d.genzen)+d3.genzen;            // 源泉徴収税額（㊽）＝給与等＋上場株式等の源泉
    a.G78=genzen;
    var nouzei=goukei-genzen;                    // 申告納税額（㊾）
    a.G79=Math.abs(nouzei);                      // セルには絶対値（符号は注記で案内）
    var dai3=(nouzei>0)?Math.floor(nouzei/100)*100:0;
    a.G81=dai3;                                  // 第3期分の税額 納める税金（㊿）
    return {amounts:a, kanpu:(nouzei<0?-nouzei:0), nouzei:nouzei, kazei:kazei, kojoKei:kojoKei, gokei:gokei, dai3:d3};
  }
  // 白色申告 収支内訳書(一般用) 1枚目：収入・売上原価・経費・専従者控除→所得金額
  // 決算書の経費コード → 収支内訳書の経費コード（同じ科目名で対応づけ）
  var SHUSHI_EXP={
    G08:'G18', G09:'G19', G10:'G20', G11:'G21', G12:'G22', G13:'G23', G14:'G24',
    G15:'G25', G16:'G26', G17:'G27', G18:'G14', G19:'G28', G20:'G12', G21:'G13',
    G22:'G17', G23:'G16', G24:'G15', G31:'G34'
  };
  function calcShushi(d){
    d=d||{}; var a={};
    var uriage=N(d.uriage), kaji=N(d.kaji), sonota=N(d.sonota);
    a.G02=uriage; a.G03=kaji; a.G04=sonota;
    a.G05=uriage+kaji+sonota;                               // 収入金額 計
    var kisho=N(d.kisho), shiire=N(d.shiire), kimatsu=N(d.kimatsu);
    a.G06=kisho; a.G07=shiire; a.G08=kisho+shiire;          // 小計
    a.G09=kimatsu; a.G10=a.G08-kimatsu;                     // 差引原価
    a.G11=a.G05-a.G10;                                      // 差引金額(④−⑨)
    var exp=d.exp||{};
    Object.keys(SHUSHI_EXP).forEach(function(k){ a[SHUSHI_EXP[k]]=N(exp[k]); });
    // その他経費小計（イ〜レ＝G18〜G34）
    var other=0; ['G18','G19','G20','G21','G22','G23','G24','G25','G26','G27','G28','G29','G30','G31','G32','G33','G34'].forEach(function(c){ other+=a[c]||0; });
    a.G35=other;                                            // 小計(イ〜レ)
    a.G36=a.G12+a.G13+a.G14+a.G15+a.G16+a.G17+a.G35;        // 経費計
    a.G37=a.G11-a.G36;                                      // 専従者控除前の所得金額
    // 専従者控除：人数指定があれば上限を自動判定、なければ手入力額
    var sHai=!!d.senju_haiguu, sOther=N(d.senju_other), sn=(sHai?1:0)+sOther;
    if(sn>0){
      var cap=Math.floor(Math.max(0,a.G37)/(sn+1));         // 所得÷(専従者数+1)
      a.G38=(sHai?Math.min(860000,cap):0)+sOther*Math.min(500000,cap);
    } else {
      a.G38=N(d.senju);
    }
    a.G39=a.G37-a.G38;                                      // 所得金額
    return {amounts:a, header:(d.header||{}), senjuCap:(sn>0?Math.floor(Math.max(0,a.G37)/(sn+1)):0)};
  }
  return {calc:calc, calcP2:calcP2, calcP4:calcP4, calcShinkoku:calcShinkoku, calcShushi:calcShushi, calcDai3:calcDai3, calcJuminzei:calcJuminzei, EXPENSES:EXPENSES};
}));

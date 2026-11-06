/* Free BizDoc — 経費の勘定科目 自動振り分けエンジン（UMD: ブラウザ/Node共用）
   CSV解析＋キーワード辞書＋業種プロファイル＋学習（手修正の記憶）。 */
(function(root,factory){
  if(typeof module==='object'&&module.exports){module.exports=factory();}
  else{root.ExpenseCats=factory();}
}(typeof self!=='undefined'?self:this,function(){

  // 損益計算書の経費科目（コード -> 名称）
  var LABELS={G08:'租税公課',G09:'荷造運賃',G10:'水道光熱費',G11:'旅費交通費',G12:'通信費',
    G13:'広告宣伝費',G14:'接待交際費',G15:'損害保険料',G16:'修繕費',G17:'消耗品費',G18:'減価償却費',
    G19:'福利厚生費',G20:'給料賃金',G21:'外注工賃',G22:'利子割引料',G23:'地代家賃',G24:'貸倒金',G31:'雑費'};

  // 基本辞書（キーワード -> コード）。摘要/店名に含まれれば分類。
  var BASE=[
    // 水道光熱費
    ['電力','G10'],['電気料','G10'],['東京電力','G10'],['関西電力','G10'],['中部電力','G10'],['東北電力','G10'],['九州電力','G10'],['東電','G10'],['でんき','G10'],['ガス','G10'],['東京ガス','G10'],['大阪ガス','G10'],['水道','G10'],['上下水道','G10'],
    // 通信費
    ['ドコモ','G12'],['docomo','G12'],['au','G12'],['kddi','G12'],['softbank','G12'],['ソフトバンク','G12'],['楽天モバイル','G12'],['携帯','G12'],['通信','G12'],['インターネット','G12'],['プロバイダ','G12'],['ntt','G12'],['ocn','G12'],['nuro','G12'],['さくらインターネット','G12'],['xserver','G12'],['エックスサーバ','G12'],['お名前.com','G12'],['ムームー','G12'],['cloudflare','G12'],['aws','G12'],['google cloud','G12'],['切手','G12'],['郵便','G12'],['はがき','G12'],
    // 旅費交通費
    ['jr','G11'],['新幹線','G11'],['地下鉄','G11'],['メトロ','G11'],['都営','G11'],['私鉄','G11'],['バス','G11'],['タクシー','G11'],['日本交通','G11'],['etc','G11'],['高速','G11'],['nexco','G11'],['航空','G11'],['ana','G11'],['jal','G11'],['航空券','G11'],['suica','G11'],['pasmo','G11'],['icoca','G11'],['駐車','G11'],['タイムズ','G11'],['ガソリン','G11'],['eneos','G11'],['出光','G11'],['コスモ石油','G11'],['宿泊','G11'],['ホテル','G11'],
    // 荷造運賃
    ['ヤマト','G09'],['宅急便','G09'],['クロネコ','G09'],['佐川','G09'],['ゆうパック','G09'],['送料','G09'],['配送','G09'],['レターパック','G09'],['梱包','G09'],
    // 消耗品費
    ['amazon','G17'],['アマゾン','G17'],['楽天','G17'],['ヨドバシ','G17'],['ビックカメラ','G17'],['ヤマダ電機','G17'],['カインズ','G17'],['ニトリ','G17'],['無印','G17'],['ダイソー','G17'],['セリア','G17'],['アスクル','G17'],['askul','G17'],['モノタロウ','G17'],['kaunet','G17'],['コクヨ','G17'],['文具','G17'],['事務用品','G17'],['消耗品','G17'],
    // 広告宣伝費
    ['広告','G13'],['google ads','G13'],['google広告','G13'],['facebook','G13'],['meta','G13'],['instagram','G13'],['チラシ','G13'],['ラクスル','G13'],['indeed','G13'],['求人','G13'],['リスティング','G13'],['名刺','G13'],
    // 外注工賃
    ['外注','G21'],['業務委託','G21'],['ランサーズ','G21'],['lancers','G21'],['クラウドワークス','G21'],['crowdworks','G21'],['ココナラ','G21'],['委託','G21'],
    // 租税公課
    ['収入印紙','G08'],['印紙','G08'],['自動車税','G08'],['固定資産税','G08'],['事業税','G08'],['不動産取得税','G08'],['登録免許税','G08'],['印鑑証明','G08'],
    // 損害保険料
    ['保険','G15'],['損保','G15'],['東京海上','G15'],['三井住友海上','G15'],['損保ジャパン','G15'],['あいおい','G15'],['火災保険','G15'],
    // 地代家賃
    ['家賃','G23'],['賃料','G23'],['地代','G23'],['テナント','G23'],['レンタルオフィス','G23'],['wework','G23'],['regus','G23'],['コワーキング','G23'],['月極','G23'],
    // 利子割引料
    ['利息','G22'],['利子','G22'],
    // 給料賃金
    ['給与','G20'],['給料','G20'],['賃金','G20'],['アルバイト代','G20'],
    // 修繕費
    ['修理','G16'],['修繕','G16'],['メンテナンス','G16'],['車検','G16'],
    // 福利厚生費
    ['健康診断','G19'],['人間ドック','G19'],
    // 雑費（手数料など）
    ['振込手数料','G31'],['手数料','G31'],['atm','G31'],['年会費','G31'],['会費','G31']
  ];

  // 業種プロファイル（業種特有の上書き・追加。基本辞書より優先）
  var PROFILES={
    general:[],
    it:[['サーバ','G12'],['ドメイン','G12'],['github','G12'],['adobe','G17'],['jetbrains','G17'],['notion','G12'],['slack','G12'],['zoom','G12'],['figma','G17'],['chatgpt','G12'],['openai','G12'],['vercel','G12'],['netlify','G12']],
    design:[['adobe','G17'],['figma','G17'],['canva','G17'],['photo','G17'],['素材','G17'],['フォント','G17'],['pixta','G13'],['shutterstock','G13']],
    construction:[['工具','G17'],['資材','G17'],['建材','G17'],['ホームセンター','G17'],['作業着','G17'],['ワークマン','G17'],['軽油','G11'],['重機','G11']],
    beauty:[['美容材料','G17'],['シャンプー','G17'],['カラー剤','G17'],['タオル','G17'],['サロン','G23']],
    retail:[['仕入','G17'],['包装','G09'],['ショッピングカート','G13'],['base','G13'],['shopify','G13'],['stores','G13']],
    writer:[['書籍','G17'],['取材','G11'],['資料','G17'],['adobe','G17']],
    consult:[['書籍','G17'],['セミナー','G13'],['研修','G19']]
  };

  function norm(s){return String(s||'').toLowerCase().replace(/\s+/g,'');}

  // desc を分類。opts: {industry, learned:{keyword:code}}。戻り: {code,label,by} or {code:null}
  function categorize(desc, opts){
    opts=opts||{}; var d=norm(desc);
    if(!d) return {code:null};
    // 1) 学習（手修正の記憶）を最優先
    var learned=opts.learned||{};
    var lk=Object.keys(learned).sort(function(a,b){return b.length-a.length;});
    for(var i=0;i<lk.length;i++){ if(lk[i] && d.indexOf(norm(lk[i]))>=0){ var c=learned[lk[i]]; return {code:c,label:LABELS[c]||'',by:'learned'}; } }
    // 2) 業種プロファイル -> 基本辞書（長いキーワード優先）
    var prof=PROFILES[opts.industry]||[];
    var all=prof.concat(BASE).slice().sort(function(a,b){return b[0].length-a[0].length;});
    for(var j=0;j<all.length;j++){ if(d.indexOf(norm(all[j][0]))>=0){ return {code:all[j][1],label:LABELS[all[j][1]],by:'dict',keyword:all[j][0]}; } }
    return {code:null};
  }

  // 金額文字列 -> 整数（¥,円,カンマ,空白を除去し絶対値）
  function parseAmount(s){
    if(s==null) return 0;
    var t=String(s).replace(/[^0-9.\-]/g,'');
    var n=parseFloat(t); if(!isFinite(n)) return 0;
    return Math.round(Math.abs(n));
  }

  // 簡易CSVパーサ（カンマ区切り・ダブルクオート対応）。戻り: 行の配列（各行は文字列配列）
  function parseCSV(text){
    var rows=[], row=[], field='', i=0, inq=false, c;
    text=String(text).replace(/\r\n/g,'\n').replace(/\r/g,'\n');
    for(i=0;i<text.length;i++){
      c=text[i];
      if(inq){
        if(c==='"'){ if(text[i+1]==='"'){field+='"';i++;} else {inq=false;} }
        else field+=c;
      }else{
        if(c==='"') inq=true;
        else if(c===',') { row.push(field); field=''; }
        else if(c==='\n'){ row.push(field); rows.push(row); row=[]; field=''; }
        else field+=c;
      }
    }
    if(field!==''||row.length){ row.push(field); rows.push(row); }
    return rows.filter(function(r){return r.some(function(x){return String(x).trim()!=='';});});
  }

  // ヘッダ行から 日付/摘要/金額 列を推測。戻り: {date,desc,amount} index（不明は-1）
  function guessColumns(header){
    var H=(header||[]).map(function(x){return norm(x);});
    function find(keys){ for(var k=0;k<keys.length;k++){ for(var i=0;i<H.length;i++){ if(H[i].indexOf(keys[k])>=0) return i; } } return -1; }
    return {
      date: find(['日付','取引日','利用日','ご利用日','date','年月日']),
      desc: find(['摘要','内容','利用先','ご利用先','店名','利用店名','description','memo','詳細','取引内容']),
      amount: find(['出金','利用金額','ご利用金額','支払金額','金額','amount','お支払金額','引き落とし'])
    };
  }

  return { LABELS:LABELS, BASE:BASE, PROFILES:PROFILES, categorize:categorize,
           parseAmount:parseAmount, parseCSV:parseCSV, guessColumns:guessColumns };
}));

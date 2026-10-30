// 公開オンライン請求書ページ /i/<token>（認証不要）。
// HTMLシェルを返し、クライアントで /api/i/<token> を取得して描画。PDFは window.API で生成。
export async function onRequestGet() {
  return new Response(PAGE, {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' },
  });
}

const PAGE = `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>請求書 | Free BizDoc</title>
<link rel="icon" href="/favicon.ico">
<style>
:root{--bg:#eef3fb;--card:#fff;--ink:#0f2744;--mut:#64748b;--line:#e4ebf5;--brand:#1766e6;--brand-d:#0f4fc4;--good:#0a8f5b;--good-s:#e6f6ef;--warn:#b26a00;--warn-s:#fdf3e2;--bad:#d64545;--bad-s:#fdeaea}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Kaku Gothic ProN",Meiryo,Roboto,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:720px;margin:0 auto;padding:22px 16px 64px}
.topbar{display:flex;align-items:center;gap:10px;margin-bottom:18px}
.topbar img{height:28px;width:auto;display:block}
.lang{margin-left:auto;font-size:12.5px}
.lang a{color:var(--mut);text-decoration:none;padding:3px 7px;border-radius:7px}
.lang a.on{background:#fff;color:var(--brand);font-weight:700;box-shadow:0 1px 3px rgba(15,39,68,.08)}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:0 10px 30px rgba(15,39,68,.07);overflow:hidden}
.hd{padding:24px 26px 18px;border-bottom:1px solid var(--line);display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap}
.hd h1{margin:0;font-size:22px;letter-spacing:.04em}
.badge{font-size:12px;font-weight:800;padding:5px 11px;border-radius:999px;white-space:nowrap}
.b-pend{background:var(--warn-s);color:var(--warn)}.b-part{background:#eaf1fe;color:var(--brand-d)}.b-paid{background:var(--good-s);color:var(--good)}.b-over{background:var(--bad-s);color:var(--bad)}
.bd{padding:22px 26px}
.parties{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:6px}
@media(max-width:560px){.parties{grid-template-columns:1fr}.hd,.bd{padding-left:18px;padding-right:18px}}
.lbl{font-size:11px;font-weight:700;color:var(--mut);letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px}
.pty .nm{font-size:16px;font-weight:700}
.pty .sub{font-size:12.5px;color:var(--mut);white-space:pre-wrap}
.meta{display:flex;gap:22px;flex-wrap:wrap;margin:16px 0 6px;font-size:13px;color:var(--mut)}
.meta b{color:var(--ink);font-weight:700}
table.items{width:100%;border-collapse:collapse;margin:12px 0}
table.items th{font-size:11px;color:var(--mut);text-align:left;font-weight:700;padding:8px 8px;border-bottom:2px solid var(--line)}
table.items td{padding:10px 8px;border-bottom:1px solid var(--line);font-size:13.5px;vertical-align:top}
table.items td.r,table.items th.r{text-align:right;white-space:nowrap}
.tot{margin-left:auto;width:min(320px,100%);margin-top:10px}
.tot .row{display:flex;justify-content:space-between;padding:5px 0;font-size:13.5px;color:var(--mut)}
.tot .row b{color:var(--ink);font-weight:600}
.tot .grand{border-top:2px solid var(--line);margin-top:6px;padding-top:12px;font-size:20px;font-weight:800;color:var(--ink)}
.tot .grand span:last-child{color:var(--brand-d)}
.pay{margin:22px 0 4px;padding:18px;background:#f6f9ff;border:1px solid #dbe6fb;border-radius:14px}
.pay .amt{font-size:13px;color:var(--mut);margin-bottom:10px}
.pay .amt b{font-size:19px;color:var(--ink)}
.btns{display:flex;gap:10px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:7px;border:none;cursor:pointer;font-size:14px;font-weight:700;border-radius:11px;padding:12px 20px;text-decoration:none;transition:transform .05s,box-shadow .15s}
.btn:active{transform:translateY(1px)}
.btn.pri{background:var(--brand);color:#fff;box-shadow:0 6px 16px rgba(23,102,230,.3)}
.btn.pri:hover{background:var(--brand-d)}
.btn.sec{background:#fff;color:var(--brand);border:1.5px solid #cfe0fb}
.btn.ghost{background:#fff;color:var(--mut);border:1.5px solid var(--line)}
.bank{margin-top:14px;font-size:13px;color:var(--mut);white-space:pre-wrap;padding:12px 14px;background:#fafcff;border:1px solid var(--line);border-radius:11px}
.notes{margin-top:14px;font-size:12.5px;color:var(--mut);white-space:pre-wrap}
.ft{text-align:center;margin-top:22px;font-size:11.5px;color:#9aa7b4}
.ft a{color:var(--brand)}
.msg{margin-top:12px;font-size:13px;padding:11px 14px;border-radius:10px;display:none}
.msg.ok{display:block;background:var(--good-s);color:var(--good)}
.msg.err{display:block;background:var(--bad-s);color:var(--bad)}
.skel{padding:60px 20px;text-align:center;color:var(--mut);font-size:14px}
.spin{width:22px;height:22px;border:3px solid #dce6f5;border-top-color:var(--brand);border-radius:50%;display:inline-block;animation:sp 1s linear infinite;vertical-align:-5px;margin-right:8px}
@keyframes sp{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <img src="/logo.png?v=20261030" alt="Free BizDoc">
    <span class="lang"><a href="?lang=ja" id="l-ja">日本語</a><a href="?lang=en" id="l-en">EN</a></span>
  </div>
  <div id="root"><div class="card"><div class="skel"><span class="spin"></span><span id="loadmsg">読み込み中…</span></div></div></div>
</div>
<script src="/api.js?v=20261030a"></script>
<script>
(function(){
  var qs=new URLSearchParams(location.search);
  var LANG=(qs.get('lang')==='en')?'en':'ja';
  document.documentElement.lang=LANG;
  var L={ja:document.getElementById('l-ja'),en:document.getElementById('l-en')};
  (LANG==='en'?L.en:L.ja).classList.add('on');
  var TOKEN=(location.pathname.split('/').filter(Boolean).pop()||'');
  var DATA=null;
  function t(ja,en){return LANG==='en'?en:ja;}
  document.getElementById('loadmsg').textContent=t('読み込み中…','Loading…');
  function yen(n){var v=Math.round(Number(n)||0);return '¥'+v.toLocaleString(LANG==='en'?'en-US':'ja-JP');}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
  function fdate(s){return s?esc(s):'';}

  fetch('/api/i/'+encodeURIComponent(TOKEN)).then(function(r){return r.json();}).then(function(j){
    if(!j||!j.ok){ document.getElementById('root').innerHTML='<div class="card"><div class="skel">'+t('この請求書は見つかりませんでした。リンクが正しいかご確認ください。','This invoice could not be found. Please check the link.')+'</div></div>'; return; }
    DATA=j; render(j);
  }).catch(function(){ document.getElementById('root').innerHTML='<div class="card"><div class="skel">'+t('読み込みに失敗しました。','Could not load.')+'</div></div>'; });

  function statusBadge(st,overdue){
    if(st==='paid')return '<span class="badge b-paid">'+t('支払い済み','Paid')+'</span>';
    if(st==='partial')return '<span class="badge b-part">'+t('一部入金','Partial')+'</span>';
    if(overdue)return '<span class="badge b-over">'+t('期限超過','Overdue')+'</span>';
    return '<span class="badge b-pend">'+t('未払い','Unpaid')+'</span>';
  }
  function render(j){
    var d=j.doc, items=j.items||[], co=j.company||{};
    var today=new Date().toISOString().slice(0,10);
    var overdue=(d.status==='pending'||d.status==='partial')&&d.due_date&&d.due_date<today;
    var rows=items.map(function(it){
      var amt=Math.round((Number(it.qty)||0)*(Math.round(Number(it.unit_price)||0)));
      var q=(Number(it.qty)||0);
      return '<tr><td>'+esc(it.name||'')+'</td>'
        +'<td class="r">'+q+(it.unit?(' '+esc(it.unit)):'')+'</td>'
        +'<td class="r">'+yen(it.unit_price)+'</td>'
        +'<td class="r">'+yen(amt)+'</td></tr>';
    }).join('');
    var totRows='';
    totRows+='<div class="row"><span>'+t('小計','Subtotal')+'</span><b>'+yen(d.subtotal)+'</b></div>';
    if(d.tax)totRows+='<div class="row"><span>'+t('消費税','Tax')+'</span><b>'+yen(d.tax)+'</b></div>';
    if(d.withholding)totRows+='<div class="row"><span>'+t('源泉徴収','Withholding')+'</span><b>-'+yen(d.withholding)+'</b></div>';
    totRows+='<div class="row grand"><span>'+t('ご請求額','Total due')+'</span><span>'+yen(d.payable)+'</span></div>';
    if(d.paid_total)totRows+='<div class="row"><span>'+t('入金済み','Paid')+'</span><b>'+yen(d.paid_total)+'</b></div>';

    var remaining=j.remaining;
    var payBtn=j.paylink?('<a class="btn pri" href="'+esc(j.paylink)+'" target="_blank" rel="noopener">'+payIcon()+t('今すぐお支払い','Pay now')+'</a>'):'';
    var paidReportBtn=(d.status!=='paid')?('<button class="btn sec" id="paidbtn">'+t('支払いました','I\\'ve paid')+'</button>'):'';
    var payBox=(d.status==='paid')
      ? '<div class="pay"><div class="amt">'+t('この請求書はお支払い済みです。ありがとうございました。','This invoice has been paid. Thank you.')+'</div><div class="btns"><button class="btn ghost" id="pdfbtn">'+t('PDFをダウンロード','Download PDF')+'</button></div></div>'
      : '<div class="pay"><div class="amt">'+t('お支払い残額','Amount due')+' <b>'+yen(remaining)+'</b></div><div class="btns">'+payBtn+'<button class="btn ghost" id="pdfbtn">'+t('PDFをダウンロード','Download PDF')+'</button>'+paidReportBtn+'</div><div class="msg" id="msg"></div></div>';

    var bank=(d.bank||co.default_bank||'');
    var html='<div class="card">'
      +'<div class="hd"><h1>'+t('請求書','INVOICE')+'</h1>'+statusBadge(d.status,overdue)
      +'<span style="margin-left:auto;text-align:right"><div class="lbl">'+t('請求書番号','Invoice No.')+'</div><div style="font-weight:700;font-size:14px">'+esc(d.doc_no||'—')+'</div></span></div>'
      +'<div class="bd">'
      +'<div class="parties">'
      +'<div class="pty"><div class="lbl">'+t('請求元','From')+'</div><div class="nm">'+esc(co.company_name||'')+'</div><div class="sub">'+esc(co.company_addr||'')+(co.reg_number?('\\n'+t('登録番号','Reg. No.')+': '+esc(co.reg_number)):'')+'</div></div>'
      +'<div class="pty"><div class="lbl">'+t('請求先','Bill to')+'</div><div class="nm">'+esc(d.client_name||'')+(d.honorific?(' '+esc(d.honorific)):'')+'</div><div class="sub">'+esc(d.client_address||'')+'</div></div>'
      +'</div>'
      +'<div class="meta"><span>'+t('発行日','Issued')+': <b>'+fdate(d.issue_date)+'</b></span>'+(d.due_date?('<span>'+t('支払期限','Due')+': <b>'+fdate(d.due_date)+'</b></span>'):'')+'</div>'
      +'<table class="items"><thead><tr><th>'+t('品目','Item')+'</th><th class="r">'+t('数量','Qty')+'</th><th class="r">'+t('単価','Unit price')+'</th><th class="r">'+t('金額','Amount')+'</th></tr></thead><tbody>'+rows+'</tbody></table>'
      +'<div class="tot">'+totRows+'</div>'
      +payBox
      +(bank?('<div class="bank"><b>'+t('お振込先','Bank transfer')+'</b>\\n'+esc(bank)+'</div>'):'')
      +(d.notes?('<div class="notes">'+esc(d.notes)+'</div>'):'')
      +'</div></div>'
      +'<div class="ft">'+t('このページは ','Powered by ')+'<a href="https://free-bizdocs.com/'+(LANG==='en'?'en/':'')+'?utm_source=online_invoice&utm_medium=footer" target="_blank" rel="noopener">Free BizDoc</a>'+t(' で発行されました','')+'</div>';
    document.getElementById('root').innerHTML=html;

    var pdfb=document.getElementById('pdfbtn');
    if(pdfb)pdfb.addEventListener('click',function(){ downloadPdf(pdfb); });
    var pb=document.getElementById('paidbtn');
    if(pb)pb.addEventListener('click',function(){ reportPaid(pb); });
  }
  function payIcon(){return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></svg>';}

  async function downloadPdf(btn){
    if(!window.API){ alert(t('PDFを生成できませんでした。','Could not generate PDF.')); return; }
    var old=btn.textContent; btn.textContent=t('生成中…','Generating…'); btn.disabled=true;
    try{ await API.invoiceFromData(DATA.doc, DATA.items||[], DATA.company||{}, DATA.kind||'invoice'); }
    catch(e){ alert(t('PDFを生成できませんでした。','Could not generate PDF.')); }
    btn.textContent=old; btn.disabled=false;
  }
  async function reportPaid(btn){
    var msg=document.getElementById('msg');
    btn.disabled=true; btn.textContent=t('送信中…','Sending…');
    try{
      var r=await fetch('/api/i/'+encodeURIComponent(TOKEN),{method:'POST',headers:{'content-type':'application/json'},body:'{}'});
      var j=await r.json();
      if(j&&j.ok){ msg.className='msg ok'; msg.textContent=t('お支払いの報告を送信しました。発行者が確認します。ありがとうございました。','Your payment report has been sent. The sender will confirm it. Thank you.'); btn.style.display='none'; }
      else { throw new Error(); }
    }catch(e){ msg.className='msg err'; msg.textContent=t('送信に失敗しました。時間をおいてお試しください。','Could not send. Please try again later.'); btn.disabled=false; btn.textContent=t('支払いました','I\\'ve paid'); }
  }
})();
</script>
</body>
</html>`;

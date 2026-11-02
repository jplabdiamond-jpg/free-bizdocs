// 公開 取引先ポータル /c/<token>（認証不要）。その取引先宛の請求書・見積書を一覧表示。
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
<title>書類一覧 | Free BizDoc</title>
<link rel="icon" href="/favicon.ico">
<style>
:root{--bg:#eef3fb;--card:#fff;--ink:#0f2744;--mut:#64748b;--line:#e4ebf5;--brand:#1766e6;--brand-d:#0f4fc4;--good:#0a8f5b;--good-s:#e6f6ef;--warn:#b26a00;--warn-s:#fdf3e2;--bad:#d64545;--bad-s:#fdeaea}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Kaku Gothic ProN",Meiryo,Roboto,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding:22px 16px 64px}
.topbar{display:flex;align-items:center;gap:10px;margin-bottom:18px}
.topbar img{height:26px;width:auto;display:block}
.lang{margin-left:auto;font-size:12.5px}
.lang a{color:var(--mut);text-decoration:none;padding:3px 7px;border-radius:7px}
.lang a.on{background:#fff;color:var(--brand);font-weight:700;box-shadow:0 1px 3px rgba(15,39,68,.08)}
.head{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 22px;margin-bottom:16px;box-shadow:0 8px 24px rgba(15,39,68,.06)}
.head .snd{font-size:13px;color:var(--mut)}
.head h1{margin:4px 0 0;font-size:20px}
.sec{margin:20px 0 8px;font-size:13px;font-weight:800;color:var(--mut);letter-spacing:.04em}
.doc{display:flex;align-items:center;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:13px;padding:14px 16px;margin-bottom:10px;text-decoration:none;color:inherit;transition:box-shadow .15s,transform .05s}
.doc:hover{box-shadow:0 8px 22px rgba(15,39,68,.1)}
.doc:active{transform:translateY(1px)}
.doc .meta{min-width:0;flex:1}
.doc .no{font-weight:700;font-size:14.5px}
.doc .sub{font-size:12px;color:var(--mut)}
.doc .amt{font-weight:800;font-size:15px;white-space:nowrap}
.badge{font-size:11px;font-weight:800;padding:4px 9px;border-radius:999px;white-space:nowrap}
.b-pend{background:var(--warn-s);color:var(--warn)}.b-part{background:#eaf1fe;color:var(--brand-d)}.b-paid{background:var(--good-s);color:var(--good)}.b-over{background:var(--bad-s);color:var(--bad)}
.arrow{color:var(--mut);flex:none}
.empty,.skel{padding:48px 20px;text-align:center;color:var(--mut)}
.ft{text-align:center;margin-top:26px;font-size:11.5px;color:#9aa7b4}.ft a{color:var(--brand)}
.spin{width:22px;height:22px;border:3px solid #dce6f5;border-top-color:var(--brand);border-radius:50%;display:inline-block;animation:sp 1s linear infinite;vertical-align:-5px;margin-right:8px}
@keyframes sp{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar"><img src="/logo.png?v=20261030" alt="Free BizDoc">
    <span class="lang"><a href="?lang=ja" id="l-ja">日本語</a><a href="?lang=en" id="l-en">EN</a></span>
  </div>
  <div id="root"><div class="head"><div class="skel"><span class="spin"></span><span id="loadmsg">読み込み中…</span></div></div></div>
</div>
<script>
(function(){
  var qs=new URLSearchParams(location.search);
  var LANG=(qs.get('lang')==='en')?'en':'ja';
  document.documentElement.lang=LANG;
  (LANG==='en'?document.getElementById('l-en'):document.getElementById('l-ja')).classList.add('on');
  var TOKEN=(location.pathname.split('/').filter(Boolean).pop()||'');
  function t(ja,en){return LANG==='en'?en:ja;}
  document.getElementById('loadmsg').textContent=t('読み込み中…','Loading…');
  function yen(n){var v=Math.round(Number(n)||0);return '¥'+v.toLocaleString(LANG==='en'?'en-US':'ja-JP');}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}

  fetch('/api/c/'+encodeURIComponent(TOKEN)).then(function(r){return r.json();}).then(function(j){
    if(!j||!j.ok){ document.getElementById('root').innerHTML='<div class="head"><div class="empty">'+t('ページが見つかりませんでした。','This page could not be found.')+'</div></div>'; return; }
    render(j);
  }).catch(function(){ document.getElementById('root').innerHTML='<div class="head"><div class="empty">'+t('読み込みに失敗しました。','Could not load.')+'</div></div>'; });

  function badge(dc){
    var today=new Date().toISOString().slice(0,10);
    if(dc.type==='quote')return dc.accepted?'<span class="badge b-paid">'+t('承認済み','Accepted')+'</span>':'<span class="badge b-pend">'+t('未承認','Pending')+'</span>';
    if(dc.status==='paid')return '<span class="badge b-paid">'+t('支払い済み','Paid')+'</span>';
    if(dc.status==='partial')return '<span class="badge b-part">'+t('一部入金','Partial')+'</span>';
    if(dc.due_date&&dc.due_date<today)return '<span class="badge b-over">'+t('期限超過','Overdue')+'</span>';
    return '<span class="badge b-pend">'+t('未払い','Unpaid')+'</span>';
  }
  function docRow(dc){
    var kind=dc.type==='quote'?t('見積書','Estimate'):t('請求書','Invoice');
    return '<a class="doc" href="'+esc(dc.link)+'">'
      +'<div class="meta"><div class="no">'+esc(dc.doc_no||'—')+'</div><div class="sub">'+kind+' ・ '+esc(dc.issue_date||'')+(dc.due_date?(' ・ '+t('期限','due')+' '+esc(dc.due_date)):'')+'</div></div>'
      +'<div class="amt">'+yen(dc.amount)+'</div>'+badge(dc)
      +'<svg class="arrow" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg></a>';
  }
  function render(j){
    var invoices=j.docs.filter(function(d){return d.type==='invoice';});
    var quotes=j.docs.filter(function(d){return d.type==='quote';});
    var unpaid=invoices.filter(function(d){return d.status!=='paid';});
    var html='<div class="head"><div class="snd">'+esc(j.sender_name||'')+'</div><h1>'+esc(j.client_name||'')+' '+esc(j.honorific||'')+'</h1>'
      +'<div class="snd" style="margin-top:6px">'+t('お客様宛の書類一覧です。各書類を開いて内容確認・お支払い・承認ができます。','Documents addressed to you. Open any to review, pay, or accept.')+'</div></div>';
    if(!j.docs.length){ html+='<div class="head"><div class="empty">'+t('まだ書類はありません。','No documents yet.')+'</div></div>'; }
    if(unpaid.length){ html+='<div class="sec">'+t('お支払い待ちの請求書','Invoices awaiting payment')+'</div>'+unpaid.map(docRow).join(''); }
    var paid=invoices.filter(function(d){return d.status==='paid';});
    if(paid.length){ html+='<div class="sec">'+t('お支払い済みの請求書','Paid invoices')+'</div>'+paid.map(docRow).join(''); }
    if(quotes.length){ html+='<div class="sec">'+t('見積書','Estimates')+'</div>'+quotes.map(docRow).join(''); }
    html+='<div class="ft">'+t('このページは ','Powered by ')+'<a href="https://free-bizdocs.com/'+(LANG==='en'?'en/':'')+'?utm_source=portal&utm_medium=footer" target="_blank" rel="noopener">Free BizDoc</a>'+t(' で提供されています','')+'</div>';
    document.getElementById('root').innerHTML=html;
  }
})();
</script>
</body>
</html>`;

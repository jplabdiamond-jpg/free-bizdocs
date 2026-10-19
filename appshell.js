/* アプリ画面共通: PRO限定ゲート＋アップセル／モバイルのハンバーガー／テーブル崩れ修正 */
(function(){
  var GATED={'/recurring':1,'/payments':1,'/reports':1}; // 無料は不可（PRO限定）
  var path=location.pathname.replace(/\.html$/,'');

  // ---- CSS ----
  var css=''
  +'.fb-burger{display:none}'
  +'.fb-lock{margin-left:auto;font-size:10px;font-weight:800;color:#9c6b15;background:#f6ecd2;border-radius:999px;padding:1px 7px}'
  +'.fb-ov{position:absolute;inset:0;background:rgba(246,246,242,.72);backdrop-filter:blur(2px);display:flex;align-items:flex-start;justify-content:center;padding:60px 20px;z-index:50}'
  +'.fb-modal{position:fixed;inset:0;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px}'
  +'.fb-card{background:#fff;border-radius:18px;max-width:430px;width:100%;padding:26px 26px 22px;box-shadow:0 30px 80px -20px rgba(15,23,42,.5);text-align:center;font-family:"Zen Kaku Gothic New",system-ui,sans-serif}'
  +'.fb-card .bd{display:inline-block;font-size:12px;font-weight:800;color:#9c6b15;background:#f6ecd2;border-radius:999px;padding:5px 13px;margin-bottom:12px}'
  +'.fb-card h3{font-size:20px;font-weight:900;margin:0 0 8px;color:#171a21}'
  +'.fb-card p{font-size:14px;color:#51606f;line-height:1.8;margin:0 0 14px}'
  +'.fb-card ul{list-style:none;padding:0;margin:0 0 18px;text-align:left;display:inline-block}'
  +'.fb-card li{font-size:13.5px;color:#243;padding:5px 0 5px 24px;position:relative}'
  +'.fb-card li::before{content:"\\2713";position:absolute;left:0;color:#1766e6;font-weight:900}'
  +'.fb-card .cta{display:block;background:linear-gradient(120deg,#1766e6,#2f9bf0);color:#fff;text-decoration:none;font-weight:800;font-size:15.5px;padding:14px;border-radius:12px;box-shadow:0 10px 24px -8px rgba(23,102,230,.5)}'
  +'.fb-card .later{margin-top:12px;background:none;border:none;color:#8294a8;font-size:13px;font-family:inherit;cursor:pointer;text-decoration:underline}'
  +'@media(max-width:860px){'
  +'.app>.side{position:fixed;top:0;left:0;bottom:0;width:250px;z-index:1000;transform:translateX(-100%);transition:transform .25s ease;box-shadow:0 0 50px rgba(0,0,0,.25);overflow-y:auto}'
  +'.app.side-open>.side{transform:translateX(0)}'
  +'.fb-scrim{position:fixed;inset:0;background:rgba(0,0,0,.42);z-index:999;display:none}'
  +'.app.side-open .fb-scrim{display:block}'
  +'.fb-burger{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border:1px solid #e2e5ea;border-radius:9px;background:#fff;cursor:pointer;flex:none;padding:0}'
  +'.app .top{position:relative}'
  +'.app .card,.app .panel{overflow-x:auto!important}'
  +'.app table{min-width:540px}'
  +'.app table th,.app table td{white-space:nowrap}'
  +'}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  // ---- モバイル: ハンバーガー＋スクリム ----
  function burgerSvg(){ return '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#45607a" stroke-width="2.4"><path d="M3 6h18M3 12h18M3 18h18"/></svg>'; }
  function setupMobile(){
    var app=document.querySelector('.app'); if(!app) return;
    var top=app.querySelector('.top');
    if(top){ var b=document.createElement('button'); b.className='fb-burger'; b.setAttribute('aria-label','メニュー'); b.innerHTML=burgerSvg();
      b.addEventListener('click',function(e){ e.stopPropagation(); app.classList.toggle('side-open'); });
      top.insertBefore(b, top.firstChild); }
    var sc=document.createElement('div'); sc.className='fb-scrim'; sc.addEventListener('click',function(){ app.classList.remove('side-open'); });
    app.appendChild(sc);
    var side=app.querySelector('.side'); if(side) side.addEventListener('click',function(e){ if(e.target.closest('a')) app.classList.remove('side-open'); });
  }

  // ---- アップセル・モーダル ----
  function buildModal(){
    var m=document.createElement('div'); m.className='fb-modal'; m.id='fbModal';
    m.innerHTML='<div class="fb-card"><div class="bd">🔒 PRO プラン限定の機能</div>'
      +'<h3 id="fbModalТtl">この機能はPROプランでご利用いただけます</h3>'
      +'<p>定期請求・入金管理・レポートは、発行から回収までを効率化するPROの機能です。アップグレードすると今すぐ使えます。</p>'
      +'<ul><li>定期請求の自動作成</li><li>入金管理・消込（売掛の見える化）</li><li>売上レポート・取引先別集計</li><li>書類の保存が無制限</li></ul>'
      +'<a class="cta" href="/pricing">PROにアップグレード（期間限定 月¥2,000）→</a>'
      +'<button class="later" type="button" data-close>あとで</button></div>';
    m.addEventListener('click',function(e){ if(e.target.id==='fbModal'||(e.target.dataset&&e.target.dataset.close!=null)) m.style.display='none'; });
    document.body.appendChild(m);
  }
  function showModal(){ var m=document.getElementById('fbModal'); if(m) m.style.display='flex'; }
  window.fbShowModal=showModal;

  // ---- PRO限定ナビの横取り＆オーバーレイ ----
  function markGated(){
    var links=document.querySelectorAll('.nav a');
    Array.prototype.forEach.call(links,function(a){
      var href=(a.getAttribute('href')||'').replace(/\.html$/,'');
      if(GATED[href]){
        if(!a.querySelector('.fb-lock')){ var s=document.createElement('span'); s.className='fb-lock'; s.textContent='PRO'; a.appendChild(s); }
        a.addEventListener('click',function(e){ e.preventDefault(); var app=document.querySelector('.app'); if(app)app.classList.remove('side-open'); showModal(); });
      }
    });
  }
  function showOverlay(){
    var main=document.querySelector('.app .main')||document.querySelector('.main'); if(!main) return;
    var ov=document.createElement('div'); ov.className='fb-ov';
    ov.innerHTML='<div class="fb-card"><div class="bd">🔒 PRO プラン限定の機能</div>'
      +'<h3>この画面はPROプランの機能です</h3>'
      +'<p>定期請求・入金管理・レポートは、PROプランでご利用いただけます。無料プランでは書類の作成・保存（5件まで）がお使いいただけます。</p>'
      +'<ul><li>定期請求の自動作成</li><li>入金管理・消込</li><li>売上レポート・取引先別集計</li></ul>'
      +'<a class="cta" href="/pricing">PROにアップグレード（期間限定 月¥2,000）→</a>'
      +'<button class="later" type="button" onclick="location.href=\'/dashboard\'">ダッシュボードへ戻る</button></div>';
    main.style.position='relative';
    // コンテンツ（モックの数値など）を隠す
    Array.prototype.forEach.call(main.children,function(c){ if(c!==ov) c.style.filter='blur(3px)'; });
    main.appendChild(ov);
  }

  // ---- サイドバー動的化（保存済みタイプのみ項目追加） ----
  function buildDynamicNav(dt){
    var EXTRA=[['delivery','納品書'],['po','発注書'],['receipt','領収書'],['rirekisho','履歴書'],['shokumu','職務経歴書'],['soufu','送付状'],['inkan','電子印鑑'],['taishoku','退職届'],['shiboudouki','志望動機書'],['entrysheet','エントリーシート'],['skillsheet','スキルシート']];
    var nav=document.querySelector('.nav'); if(!nav) return;
    var after=nav.querySelector('a[href="/quotes"]') || nav.querySelector('a[href="/invoice-list"]');
    var curType=null; try{ if(path==='/doclist') curType=new URLSearchParams(location.search).get('type'); }catch(e){}
    EXTRA.forEach(function(x){
      if(!dt[x[0]]) return;
      if(nav.querySelector('a[data-dt="'+x[0]+'"]')) return;
      var a=document.createElement('a'); a.setAttribute('href','/doclist?type='+x[0]); a.setAttribute('data-dt',x[0]);
      a.innerHTML='<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6"/></svg>'+x[1];
      if(curType===x[0]) a.className='on';
      if(after&&after.parentNode){ after.parentNode.insertBefore(a, after.nextSibling); after=a; }
      else nav.appendChild(a);
    });
  }
  function init(){
    setupMobile(); buildModal();
    fetch('/api/auth/me',{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(me){
      if(me&&me.authed) buildDynamicNav(me.doc_types||{});
      var pro=me&&me.authed&&me.plan==='pro';
      if(pro) return;
      markGated();
      if(GATED[path]) showOverlay();
    }).catch(function(){});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

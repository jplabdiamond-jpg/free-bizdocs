/* 全公開ページ共通のヘッダー＋フッター認証導線（ログイン状態で出し分け） */
(function(){
  // ---- CSS（自己完結）----
  var css=''
  +'.fb-hdr{position:sticky;top:0;z-index:600;background:#fff;border-bottom:1px solid #e6e8ec}'
  +'.fb-hdr .in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:14px;padding:10px 20px}'
  +'.fb-hdr .brand{display:flex;align-items:center;text-decoration:none;flex:none}'
  +'.fb-hdr .brand img{height:28px;width:auto;display:block}'
  +'.fb-hdr .nav{display:flex;gap:2px;margin-left:6px}'
  +'.fb-hdr .nav a{font-size:13.5px;font-weight:600;color:#45607a;text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}'
  +'.fb-hdr .nav a:hover{background:#f1f5fb;color:#1766e6}'
  +'.fb-hdr .sp{flex:1}'
  +'.fb-hdr .auth{display:flex;align-items:center;gap:8px}'
  +'.fb-hdr .auth a,.fb-hdr .auth button{font-family:inherit;font-size:13.5px;font-weight:700;text-decoration:none;border-radius:9px;padding:8px 14px;cursor:pointer;white-space:nowrap;line-height:1}'
  +'.fb-hdr .lgn{color:#1766e6;background:#eaf1fe;border:1px solid #d4e3fb}'
  +'.fb-hdr .lgn:hover{background:#dbe9fd}'
  +'.fb-hdr .sgn{color:#fff;background:#1766e6;border:1px solid #1766e6}'
  +'.fb-hdr .sgn:hover{background:#1257ca}'
  +'.fb-hdr .em{font-size:12.5px;color:#6c6f78;max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
  +'.fb-ft-auth{display:flex;gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;padding:16px 20px 2px;font-size:13px}'
  +'.fb-ft-auth .ttl{color:#8097ad;font-weight:700}'
  +'.fb-ft-auth a,.fb-ft-auth button{color:#dbe7f5;font-weight:700;text-decoration:none;font-family:inherit;font-size:13px;background:none;border:none;cursor:pointer;padding:0}'
  +'.fb-ft-auth a:hover,.fb-ft-auth button:hover{text-decoration:underline}'
  +'.fb-hdr .lang-sw{font-size:12.5px;font-weight:700;color:#45607a;text-decoration:none;border:1px solid #dce5f0;border-radius:999px;padding:6px 12px;white-space:nowrap;margin-right:2px}'
  +'.fb-hdr .lang-sw:hover{background:#f1f5fb;color:#1766e6;border-color:#c7d6e8}'
  +'@media(max-width:640px){.fb-hdr .nav{display:none}.fb-hdr .em{display:none}.fb-hdr .auth a,.fb-hdr .auth button{padding:8px 12px}.fb-hdr .lang-sw{padding:6px 10px}}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  // ---- ヘッダー ----
  var hdr=document.createElement('header'); hdr.className='fb-hdr';
  hdr.innerHTML='<div class="in">'
    +'<a class="brand" href="/"><img src="/logo.png" alt="Free BizDoc"></a>'
    +'<nav class="nav"><a href="/invoice">書類を作成</a><a href="/blog">お役立ち</a><a href="/pricing">料金・PRO</a></nav>'
    +'<span class="sp"></span>'
    +'<a class="lang-sw" href="/en/?lang=en" lang="en" title="English version">English</a>'
    +'<div class="auth" id="fbAuth">'
    +'<a class="lgn" href="/login">ログイン</a><a class="sgn" href="/login?mode=signup">新規登録（無料）</a>'
    +'</div></div>';

  function mountHeader(){
    var old=document.querySelector('header.hdr');
    if(old){ old.parentNode.replaceChild(hdr, old); }
    else { document.body.insertBefore(hdr, document.body.firstChild); }
  }
  function mountFooter(){
    var ft=document.querySelector('footer.ft .in') || document.querySelector('footer.ft');
    if(!ft) return;
    var box=document.createElement('div'); box.className='fb-ft-auth'; box.id='fbFtAuth';
    box.innerHTML='<span class="ttl">アカウント</span><a href="/login">サインイン（ログイン）</a><a href="/login?mode=signup">サインアップ（無料で新規登録）</a>';
    ft.insertBefore(box, ft.firstChild);
  }

  function doLogout(){ fetch('/api/auth/logout',{method:'POST',credentials:'same-origin'}).then(function(){location.href='/';},function(){location.href='/';}); }

  function refreshAuth(){
    fetch('/api/auth/me',{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(me){
      if(!(me&&me.authed)) return;
      var a=document.getElementById('fbAuth');
      if(a){ a.innerHTML='<span class="em" title="'+(me.email||'')+'">'+(me.email||'')+'</span>'
        +'<a class="lgn" href="/dashboard">ダッシュボード</a><button class="sgn" id="fbLogout" type="button">ログアウト</button>';
        var lo=document.getElementById('fbLogout'); if(lo) lo.addEventListener('click',doLogout); }
      var f=document.getElementById('fbFtAuth');
      if(f){ f.innerHTML='<span class="ttl">アカウント</span><a href="/dashboard">ダッシュボード</a><button type="button" id="fbFtLogout">ログアウト</button>';
        var lo2=document.getElementById('fbFtLogout'); if(lo2) lo2.addEventListener('click',doLogout); }
    }).catch(function(){});
  }

  function mount(){ mountHeader(); mountFooter(); refreshAuth(); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

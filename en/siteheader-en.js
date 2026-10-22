/* English site: shared header + footer auth row (mirrors JA siteheader.js, in English). */
(function(){
  // ---- CSS (self-contained; same look as the Japanese site) ----
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
  +'.fb-hdr .sgn{position:relative;overflow:visible;color:#fff;background:#1766e6;border:1px solid #1766e6}'
  +'.fb-hdr .sgn:hover{background:#1257ca}'
  +'.fb-hdr .sgn-ex{position:absolute;top:-9px;right:-10px;transform:rotate(14deg);background:#e11d48;color:#fff;font-size:10px;font-weight:900;letter-spacing:.03em;line-height:1;padding:3px 7px;border-radius:5px;box-shadow:0 3px 9px -2px rgba(225,29,72,.6);pointer-events:none}'
  +'.fb-hdr .em{font-size:12.5px;color:#6c6f78;max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
  +'.fb-ft-auth{display:flex;gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;padding:16px 20px 2px;font-size:13px}'
  +'.fb-ft-auth .ttl{color:#8097ad;font-weight:700}'
  +'.fb-ft-auth a,.fb-ft-auth button{color:#dbe7f5;font-weight:700;text-decoration:none;font-family:inherit;font-size:13px;background:none;border:none;cursor:pointer;padding:0}'
  +'.fb-ft-auth a:hover,.fb-ft-auth button:hover{text-decoration:underline}'
  +'.fb-hdr .lang-sw{font-size:12.5px;font-weight:700;color:#45607a;text-decoration:none;border:1px solid #dce5f0;border-radius:999px;padding:6px 12px;white-space:nowrap;margin-right:2px}'
  +'.fb-hdr .lang-sw:hover{background:#f1f5fb;color:#1766e6;border-color:#c7d6e8}'
  +'@media(max-width:640px){.fb-hdr .nav{display:none}.fb-hdr .em{display:none}.fb-hdr .in{gap:8px;padding:10px 14px}.fb-hdr .auth{gap:6px}.fb-hdr .auth a,.fb-hdr .auth button{padding:10px 12px}.fb-hdr .lang-sw{padding:8px 10px}}'
  +'@media(max-width:430px){.fb-hdr .lang-sw{display:none}.fb-hdr .in{gap:8px;padding:10px 12px}.fb-hdr .auth a,.fb-hdr .auth button{padding:10px 11px;font-size:13px}.fb-hdr .sgn-ex{right:-7px;top:-8px}.fb-hdr .brand img{height:26px}}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  // ---- Header ----
  var hdr=document.createElement('header'); hdr.className='fb-hdr';
  hdr.innerHTML='<div class="in">'
    +'<a class="brand" href="/en/"><img src="/logo.png?v=20261021" alt="Free BizDoc"></a>'
    +'<nav class="nav"><a href="/en/invoice">Create document</a><a href="/en/blog">Blog</a><a href="/en/pricing">Pricing &amp; PRO</a></nav>'
    +'<span class="sp"></span>'
    +'<a class="lang-sw" href="/?lang=ja" lang="ja" title="Japanese version">日本語</a>'
    +'<div class="auth" id="fbAuth">'
    +'<a class="lgn" href="/en/login">Log in</a><a class="sgn" href="/en/login?mode=signup">Sign up<span class="sgn-ex">Free</span></a>'
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
    box.innerHTML='<span class="ttl">Account</span><a href="/en/login">Sign in</a><a href="/en/login?mode=signup">Create account (free)</a>';
    ft.insertBefore(box, ft.firstChild);
  }

  function doLogout(){ fetch('/api/auth/logout',{method:'POST',credentials:'same-origin'}).then(function(){location.href='/en/';},function(){location.href='/en/';}); }

  function refreshAuth(){
    fetch('/api/auth/me',{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(me){
      if(!(me&&me.authed)) return;
      var a=document.getElementById('fbAuth');
      if(a){ a.innerHTML='<span class="em" title="'+(me.email||'')+'">'+(me.email||'')+'</span>'
        +'<a class="lgn" href="/en/account">Account</a><button class="sgn" id="fbLogout" type="button">Log out</button>';
        var lo=document.getElementById('fbLogout'); if(lo) lo.addEventListener('click',doLogout); }
      var f=document.getElementById('fbFtAuth');
      if(f){ f.innerHTML='<span class="ttl">Account</span><a href="/en/account">Account</a><button type="button" id="fbFtLogout">Log out</button>';
        var lo2=document.getElementById('fbFtLogout'); if(lo2) lo2.addEventListener('click',doLogout); }
    }).catch(function(){});
  }

  function mount(){ mountHeader(); mountFooter(); refreshAuth(); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

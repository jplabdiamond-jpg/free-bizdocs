/* 非明細ツール共通: ログイン時にアカウント保存＋復元
   - 保存: フォーム + free_* localStorage + 写真(履歴書) のスナップショット
   - 復元: localStorageを戻してから1回だけ再読込 → ツールが学歴/職歴などの行まで再構築
   - 編集中(?saved=ID)は「上書き保存」、別途「新規として保存」も可能 */
(function(){
  var GEN={rirekisho:1,soufu:1,inkan:1,shokumu:1,taishoku:1,shiboudouki:1,entrysheet:1,skillsheet:1};
  var LABELJP={rirekisho:'履歴書',soufu:'送付状',inkan:'電子印鑑',shokumu:'職務経歴書',taishoku:'退職届',shiboudouki:'志望動機書',entrysheet:'エントリーシート',skillsheet:'スキルシート'};
  var type=location.pathname.replace(/^\//,'').replace(/\.html$/,'');
  if(!GEN[type]) return;

  function b64enc(bytes){ var bin=''; var CH=0x8000; for(var i=0;i<bytes.length;i+=CH){ bin+=String.fromCharCode.apply(null, bytes.subarray(i,i+CH)); } return btoa(bin); }
  function b64dec(s){ var bin=atob(s); var a=new Uint8Array(bin.length); for(var i=0;i<bin.length;i++) a[i]=bin.charCodeAt(i); return a; }

  function snapshot(){
    var fields={};
    Array.prototype.forEach.call(document.querySelectorAll('input[id],select[id],textarea[id]'),function(el){
      if(el.type==='file') return;
      if(el.type==='checkbox'||el.type==='radio') fields[el.id]={c:el.checked};
      else fields[el.id]=el.value;
    });
    var ls={};
    try{ for(var i=0;i<localStorage.length;i++){ var k=localStorage.key(i); if(k&&k.indexOf('free_')===0) ls[k]=localStorage.getItem(k); } }catch(e){}
    var photo=null;
    try{ if(window.photo && window.photo.bytes && window.photo.bytes.length){ var b=b64enc(window.photo.bytes); if(b.length<1800000){ photo={b64:b, type:(window.photo.type==='png'?'png':'jpg')}; } } }catch(e){}
    return {fields:fields, ls:ls, photo:photo};
  }
  function deriveLabel(){
    var best='';
    var ins=document.querySelectorAll('input[type=text],input:not([type])');
    for(var i=0;i<ins.length;i++){ var v=(ins[i].value||'').trim(); if(v){ best=v; break; } }
    return (best?best+'｜':'')+LABELJP[type]+' '+new Date().toISOString().slice(0,10);
  }
  function restorePhoto(data){
    if(!(data&&data.photo&&data.photo.b64)) return;
    try{
      var type2=data.photo.type==='png'?'png':'jpg';
      window.photo={bytes:b64dec(data.photo.b64), type:type2};
      var url='data:image/'+(type2==='png'?'png':'jpeg')+';base64,'+data.photo.b64;
      var pb=document.getElementById('photo-box'); if(pb) pb.innerHTML='<img src="'+url+'">';
      var rp=document.getElementById('rv-photo'); if(rp) rp.innerHTML='<img src="'+url+'">';
    }catch(e){}
  }
  function applyData(data){
    try{
      if(data.fields){ Object.keys(data.fields).forEach(function(id){
        var el=document.getElementById(id); if(!el)return; var v=data.fields[id];
        if(v&&typeof v==='object'&&'c' in v){ el.checked=!!v.c; }
        else if(v!=null){ el.value=v; }
        el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));
      }); }
      restorePhoto(data);
    }catch(e){}
  }
  function toast(m){ var t=document.getElementById('__asToast'); if(!t){t=document.createElement('div');t.id='__asToast';t.style.cssText='position:fixed;left:50%;bottom:84px;transform:translateX(-50%);background:#13263b;color:#fff;font-size:13.5px;font-weight:700;padding:11px 18px;border-radius:12px;box-shadow:0 12px 30px -10px rgba(19,38,59,.6);z-index:100000;opacity:0;transition:.25s;max-width:90vw;text-align:center';document.body.appendChild(t);} t.textContent=m; requestAnimationFrame(function(){t.style.opacity='1';}); clearTimeout(t._h); t._h=setTimeout(function(){t.style.opacity='0';},2600); }

  async function doSave(btn, mode, editingId){
    btn.disabled=true; var old=btn.textContent; btn.textContent='保存中…';
    try{
      var payload={type:type,label:deriveLabel(),data:snapshot()};
      var url='/api/saved', method='POST';
      if(mode==='overwrite' && editingId){ url='/api/saved/'+editingId; method='PUT'; }
      var r=await fetch(url,{method:method,headers:{'content-type':'application/json'},credentials:'same-origin',body:JSON.stringify(payload)});
      var j=await r.json().catch(function(){return{};});
      if(r.ok){
        if(mode==='overwrite'){ toast('上書き保存しました'); }
        else {
          toast('アカウントに保存しました');
          if(j.id){ var u=new URL(location.href); u.searchParams.set('saved', j.id); history.replaceState(null,'',u.toString());
            var w=document.getElementById('__acctWrap'); if(w){ w.parentNode.removeChild(w); addButton(String(j.id)); } }
        }
      }
      else if(r.status===403&&j.upsell){ if(confirm('無料プランで保存できる書類は5件までです。\nPROプラン（期間限定 月¥2,000）にアップグレードしますか？')) location.href='/pricing'; }
      else { toast('保存に失敗しました: '+(j.error||('HTTP '+r.status))); }
    }catch(e){ toast('通信エラーが発生しました'); }
    btn.disabled=false; btn.textContent=old;
  }
  function addButton(editingId){
    if(document.getElementById('__acctWrap')) return;
    var wrap=document.createElement('div'); wrap.id='__acctWrap';
    wrap.style.cssText='position:fixed;right:18px;bottom:18px;z-index:99998;display:flex;flex-direction:column;gap:8px;align-items:flex-end';
    var main=document.createElement('button'); main.type='button'; main.id='__acctSave';
    main.textContent=editingId?'💾 上書き保存':'💾 アカウントに保存';
    main.style.cssText='background:#0f7a43;color:#fff;border:none;border-radius:12px;padding:13px 18px;font-size:14px;font-weight:800;font-family:inherit;box-shadow:0 10px 24px -8px rgba(15,122,67,.55);cursor:pointer';
    main.addEventListener('click',function(){ doSave(main, editingId?'overwrite':'new', editingId); });
    wrap.appendChild(main);
    if(editingId){
      var alt=document.createElement('button'); alt.type='button'; alt.textContent='＋ 新規として保存';
      alt.style.cssText='background:#fff;color:#0f7a43;border:1.5px solid #0f7a43;border-radius:10px;padding:8px 14px;font-size:12.5px;font-weight:800;font-family:inherit;cursor:pointer;box-shadow:0 6px 16px -8px rgba(15,122,67,.4)';
      alt.addEventListener('click',function(){ doSave(alt,'new',null); });
      wrap.appendChild(alt);
    }
    document.body.appendChild(wrap);
  }
  function init(){
    fetch('/api/auth/me',{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(me){
      if(!(me&&me.authed)) return;
      var editingId=new URLSearchParams(location.search).get('saved');
      addButton(editingId);
      if(!editingId) return;
      var tag=type+':'+editingId;
      if(sessionStorage.getItem('__fbR')===tag){
        sessionStorage.removeItem('__fbR');
        var cached=sessionStorage.getItem('__fbD'); sessionStorage.removeItem('__fbD');
        if(cached){ try{ var data=JSON.parse(cached); setTimeout(function(){ applyData(data); toast('保存した内容を読み込みました（編集できます）'); },300); }catch(e){} }
        return;
      }
      fetch('/api/saved/'+editingId,{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(d){
        if(!(d&&d.data)) return;
        try{ if(d.data.ls){ Object.keys(d.data.ls).forEach(function(k){ try{localStorage.setItem(k,d.data.ls[k]);}catch(e){} }); } }catch(e){}
        try{ sessionStorage.setItem('__fbR',tag); sessionStorage.setItem('__fbD',JSON.stringify(d.data)); }catch(e){}
        location.reload();
      }).catch(function(){});
    }).catch(function(){});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();

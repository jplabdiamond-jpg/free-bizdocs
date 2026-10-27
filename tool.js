/* 共通 明細型ツール（請求書/見積書/納品書/発注書/領収書）。
   ページ側に #toolwrap[data-kind] と各入力DOM、api.js が存在する前提。 */
(function(){
var toolRoot=document.getElementById('toolwrap');
var kind=(toolRoot&&toolRoot.getAttribute('data-kind'))||'invoice';
var rowsEl=document.getElementById('rows');
var editDocId=null; try{ editDocId=new URLSearchParams(location.search).get('doc')||null; }catch(e){}
var CO=['co-name','co-reg','co-email','co-addr','co-bank'];
function loadCo(){ try{ var s=JSON.parse(localStorage.getItem('free_company')||'{}'); CO.forEach(function(id){ if(s[id]!=null) document.getElementById(id).value=s[id]; }); var d=document.getElementById('co-details'); if(d){ d.open=!s['co-name']; } }catch(e){} }
function saveCo(){ try{ var o={}; CO.forEach(function(id){o[id]=document.getElementById(id).value;}); localStorage.setItem('free_company',JSON.stringify(o)); }catch(e){} }

function rowHtml(it){ it=it||{}; return '<div class="rw">'
  +'<input class="i-name" value="'+API.esc(it.name||'')+'" placeholder="品目を入力">'
  +'<input class="i-qty n" value="'+(it.qty!=null?it.qty:1)+'">'
  +'<input class="i-unit" value="'+API.esc(it.unit||'式')+'">'
  +'<input class="i-price n" value="'+(it.unit_price!=null?it.unit_price:0)+'">'
  +'<select class="i-rate"><option value="10">10%</option><option value="8">8%</option><option value="0">非課税</option></select>'
  +'<span class="gen"><input type="checkbox" class="i-wh" style="width:15px;height:15px;accent-color:var(--ac)"></span>'
  +'<button class="del" type="button" aria-label="行を削除">×</button></div>'; }
function addRow(it){ rowsEl.insertAdjacentHTML('beforeend', rowHtml(it)); recompute(); }
function collect(){ return Array.prototype.slice.call(rowsEl.querySelectorAll('.rw')).map(function(rw){ return {
  name:rw.querySelector('.i-name').value, qty:parseFloat(rw.querySelector('.i-qty').value)||0,
  unit:rw.querySelector('.i-unit').value, unit_price:parseInt(String(rw.querySelector('.i-price').value).replace(/[^0-9.-]/g,''),10)||0,
  tax_rate:parseInt(rw.querySelector('.i-rate').value,10), withholding:rw.querySelector('.i-wh').checked?1:0 }; }); }
// ---- 下書き自動保存（取引先・明細を localStorage に保持）----
function draftKey(){ return 'free_draft_'+kind; }
var _dsT=null;
function saveDraft(){ try{ clearTimeout(_dsT); _dsT=setTimeout(function(){ try{ var o={ cl:document.getElementById('cl-name').value, hon:document.getElementById('cl-hon').value, due:document.getElementById('due').value, notes:document.getElementById('notes').value, items:collect() }; localStorage.setItem(draftKey(), JSON.stringify(o)); }catch(e){} },400); }catch(e){} }
function loadDraft(){ try{ var o=JSON.parse(localStorage.getItem(draftKey())||'null'); if(!o) return false; if(o.cl!=null)document.getElementById('cl-name').value=o.cl; if(o.hon)document.getElementById('cl-hon').value=o.hon; if(o.due)document.getElementById('due').value=o.due; if(o.notes!=null)document.getElementById('notes').value=o.notes; if(o.items&&o.items.length){ rowsEl.innerHTML=''; o.items.forEach(function(it){ rowsEl.insertAdjacentHTML('beforeend', rowHtml(it)); }); var rws=rowsEl.querySelectorAll('.rw'); o.items.forEach(function(it,i){ var rw=rws[i]; if(!rw)return; if(it.tax_rate!=null){ var rs=rw.querySelector('.i-rate'); if(rs)rs.value=String(it.tax_rate); } if(it.withholding){ var wc=rw.querySelector('.i-wh'); if(wc)wc.checked=true; } }); } return true; }catch(e){ return false; } }
function clearDraft(){ try{ localStorage.removeItem(draftKey()); }catch(e){} }
window.__colog=''; window.__coseal='';
function _loadImgLS(){ try{ window.__colog=localStorage.getItem('free_logo')||''; window.__coseal=localStorage.getItem('free_seal')||''; }catch(e){} }
function _downscale(durl,maxDim,cb){ var im=new Image(); im.onload=function(){ var w=im.width,h=im.height,sc=Math.min(1,maxDim/Math.max(w,h)); var cw=Math.max(1,Math.round(w*sc)),ch=Math.max(1,Math.round(h*sc)); var c=document.createElement('canvas'); c.width=cw;c.height=ch; c.getContext('2d').drawImage(im,0,0,cw,ch); try{cb(c.toDataURL('image/png'));}catch(e){cb('');} }; im.onerror=function(){cb('');}; im.src=durl; }
function _handleImg(id,key){ var el=document.getElementById(id); if(!el)return; el.addEventListener('change',function(){ var fl=el.files&&el.files[0]; if(!fl)return; var r=new FileReader(); r.onload=function(){ _downscale(r.result,440,function(d){ if(!d)return; if(key==='logo')window.__colog=d; else window.__coseal=d; try{localStorage.setItem(key==='logo'?'free_logo':'free_seal',d);}catch(e){} renderImgRow(); recompute(); }); }; r.readAsDataURL(fl); }); }
function renderImgRow(){ var row=document.getElementById('imgrow'); if(!row)return; var h=''; if(window.__colog) h+='<span style="display:inline-flex;align-items:center;gap:5px;font-size:11.5px;color:#5a6b7d"><img src="'+window.__colog+'" style="max-height:30px;max-width:90px;border:1px solid #e2eaf4;border-radius:4px">ロゴ<button type="button" data-k="logo" class="imgdel" style="border:none;background:none;color:#c0392b;cursor:pointer;font-size:16px;line-height:1">×</button></span>'; if(window.__coseal) h+='<span style="display:inline-flex;align-items:center;gap:5px;font-size:11.5px;color:#5a6b7d"><img src="'+window.__coseal+'" style="max-height:34px;max-width:34px;border:1px solid #e2eaf4;border-radius:4px">印影<button type="button" data-k="seal" class="imgdel" style="border:none;background:none;color:#c0392b;cursor:pointer;font-size:16px;line-height:1">×</button></span>'; row.innerHTML=h; }
function companyObj(){ return { company_name:document.getElementById('co-name').value, reg_number:document.getElementById('co-reg').value, company_addr:document.getElementById('co-addr').value, email:document.getElementById('co-email').value, default_bank:document.getElementById('co-bank').value, logo:window.__colog||'', seal:window.__coseal||'' }; }
function docObj(){ return { doc_no:(document.getElementById('doc-no')?document.getElementById('doc-no').value:''), issue_date:document.getElementById('issue').value, due_date:document.getElementById('due').value, client_name:document.getElementById('cl-name').value, honorific:document.getElementById('cl-hon').value, bank:document.getElementById('co-bank').value, notes:document.getElementById('notes').value }; }

var _lastTotal=0;
function animateTotal(to){
  var el=document.getElementById('pv-total');
  if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches){el.textContent=API.yen(to);_lastTotal=to;return;}
  var from=_lastTotal||0;if(from===to){el.textContent=API.yen(to);return;}
  var start=null,dur=420;
  function step(ts){if(!start)start=ts;var pr=Math.min((ts-start)/dur,1);var e=1-Math.pow(1-pr,3);var v=Math.round(from+(to-from)*e);el.textContent=API.yen(v);if(pr<1)requestAnimationFrame(step);else{el.textContent=API.yen(to);_lastTotal=to;}}
  requestAnimationFrame(step);
}
function pad4(n){return ('000'+n).slice(-4);}
function nextDocNo(){ try{ var y=new Date().getFullYear(); var seq=parseInt(localStorage.getItem('free_docseq')||'0',10)||0; return y+'-'+pad4(seq+1); }catch(e){ return new Date().getFullYear()+'-0001'; } }
function bumpDocNo(){ try{ var seq=parseInt(localStorage.getItem('free_docseq')||'0',10)||0; localStorage.setItem('free_docseq',String(seq+1)); }catch(e){} }
function recompute(){
  var items=collect(), c=API.calc(items), K=API.kindCfg(kind), payable=K.wh?c.payable:c.total;
  animateTotal(payable);
  document.getElementById('pv-to').textContent=(document.getElementById('cl-name').value||'取引先')+'　'+(document.getElementById('cl-hon').value||'御中');
  var ta=document.getElementById('pv-toaddr'); if(ta) ta.textContent='';
  document.getElementById('pv-issue').textContent=document.getElementById('issue').value||'';
  var _dn=document.getElementById('doc-no'); var _pn=document.getElementById('pv-num'); if(_pn) _pn.textContent=API.kindCfg(kind).num+' : '+((_dn&&_dn.value)||'—');
  document.getElementById('pv-due').textContent=document.getElementById('due').value||'—';
  document.getElementById('pv-conm').textContent=document.getElementById('co-name').value||'';
  var reg=document.getElementById('co-reg').value;
  document.getElementById('pv-coreg').textContent=reg?('登録番号 : '+reg):'';
  var ca=document.getElementById('pv-coaddr'); if(ca) ca.textContent=document.getElementById('co-addr').value||'';
  document.getElementById('pv-coemail').textContent=document.getElementById('co-email').value||'';
  var _pl=document.getElementById('pv-logo'); if(_pl){ if(window.__colog){_pl.src=window.__colog;_pl.style.display='';}else{_pl.style.display='none';} }
  var _ps=document.getElementById('pv-seal'); if(_ps){ if(window.__coseal){_ps.src=window.__coseal;_ps.style.display='';}else{_ps.style.display='none';} }
  var _rowsHtml=items.map(function(it){ var amt=Math.round((it.qty||0)*(it.unit_price||0)); return '<tr><td>'+API.esc(it.name||'')+'</td><td class="n">'+it.qty+'</td><td>'+API.esc(it.unit||'')+'</td><td class="n">'+API.yen(it.unit_price)+'</td><td class="n">'+API.yen(amt)+'</td></tr>'; }).join('');
  if((window.__tpl||'standard')==='classic'){ var _need=Math.max(0, 8-items.length); for(var _ei=0;_ei<_need;_ei++){ _rowsHtml+='<tr class="empty"><td>\u00a0</td><td></td><td></td><td></td><td></td></tr>'; } }
  document.getElementById('pv-rows').innerHTML=_rowsHtml;
  var s='';
  if(c.sub10>0){ s+='<div class="sr"><span>10%対象 小計</span><span>'+API.yen(c.sub10)+'</span></div>'; s+='<div class="sr mut"><span>消費税（10%）</span><span>'+API.yen(c.tax10)+'</span></div>'; }
  if(c.sub8>0){ s+='<div class="sr"><span>8%対象 小計（軽減）</span><span>'+API.yen(c.sub8)+'</span></div>'; s+='<div class="sr mut"><span>消費税（8%）</span><span>'+API.yen(c.tax8)+'</span></div>'; }
  if(K.wh&&c.withholding>0) s+='<div class="sr wh"><span>源泉徴収税（10.21%）</span><span>− '+API.yen(c.withholding)+'</span></div>';
  s+='<div class="tot"><span>'+K.total+'</span><span class="v">'+API.yen(payable)+'</span></div>';
  document.getElementById('pv-sum').innerHTML=s;
  var bx=document.getElementById('pv-bottom');
  if(bx){ var bh='';
    if(K.receipt){
      var nt=document.getElementById('notes').value;
      bh='<div class="bl">但し書き</div><div class="mut">'+(nt?('但し '+API.esc(nt)+' として'):'但し　　　　　　　　　として')+'</div><div class="mut">上記金額を正に領収いたしました。</div>';
      if(payable>=50000) bh+='<div class="stamp">収入印紙<em>（貼付）</em></div>';
    } else {
      bh='<div class="bl">'+(K.bank?'お振込先':'備考')+'</div>';
      if(K.bank) bh+='<div class="mut">'+API.esc(document.getElementById('co-bank').value||'')+'</div>';
      var n2=document.getElementById('notes').value;
      if(n2) bh+='<div class="mut">備考 : '+API.esc(n2)+'</div>';
    }
    bx.innerHTML=bh;
  }
}
rowsEl.addEventListener('input',recompute); rowsEl.addEventListener('change',recompute);
rowsEl.addEventListener('input',saveDraft); rowsEl.addEventListener('change',saveDraft);
rowsEl.addEventListener('click',function(e){ var d=e.target.closest('.del'); if(d){ d.closest('.rw').remove(); recompute(); saveDraft(); } });
document.getElementById('addrow').addEventListener('click',function(){ addRow({unit:'式',unit_price:0}); saveDraft(); });
['cl-name','cl-hon','issue','due','notes','doc-no'].concat(CO).forEach(function(id){ var el=document.getElementById(id); el.addEventListener('input',function(){ recompute(); if(CO.indexOf(id)>=0) saveCo(); else saveDraft(); }); el.addEventListener('change',function(){ recompute(); if(CO.indexOf(id)>=0) saveCo(); else saveDraft(); }); });

function applyKind(k){
  kind=k; var K=API.kindCfg(kind);
  var t=document.getElementById('pv-title'); if(t) t.textContent=K.t;
  var en=document.getElementById('pv-en'); if(en) en.textContent=K.en;
  var nm=document.getElementById('pv-num'); if(nm){ var _d=document.getElementById('doc-no'); nm.textContent=K.num+' : '+((_d&&_d.value)||'—'); }
  var bl=document.getElementById('pv-bnlabel'); if(bl) bl.textContent=K.amount;
  var dw=document.getElementById('due-wrap'); if(dw) dw.style.display=K.due?'':'none';
  var pdw=document.getElementById('pv-duewrap'); if(pdw) pdw.style.display=K.due?'':'none';
  var rc=document.getElementById('pv-receiptline'); if(rc) rc.style.display=K.receipt?'':'none';
  recompute();
}
var seg=document.getElementById('seg');
if(seg){ seg.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
  Array.prototype.forEach.call(this.children,function(x){x.classList.remove('on');}); b.classList.add('on');
  applyKind(b.getAttribute('data-kind'));
}); }

async function refreshRemain(){ try{ var r=await API.get('/api/free/check'); var el=document.getElementById('remain'); if(el) el.innerHTML='この1時間であと <b>'+r.remaining+'</b> 枚まで無料で作成できます'; }catch(e){} }
document.getElementById('make').addEventListener('click',async function(){
  var items=collect().filter(function(it){return it.name||it.unit_price;});
  var m=document.getElementById('msg'); m.className='msg';
  if(!items.length){ m.textContent='明細を1行以上入力してください'; m.className='msg err'; return; }
  if(!document.getElementById('cl-name').value){ m.textContent='取引先名を入力してください'; m.className='msg err'; return; }
  var btn=this; btn.disabled=true; btn.textContent='作成中…';
  try{
    var chk=await fetch('/api/free/check',{method:'POST'}); var cj=await chk.json();
    if(chk.status===429 || !cj.ok){
      var lb=document.getElementById('limitbox');
      lb.style.display='block';
      lb.innerHTML='無料ツールは1時間に2枚までです。あと約 <b>'+(cj.retry_min||60)+'分</b> で再び作成できます。<br>無制限で使うなら <a href="/pricing">PRO（月額¥3,000）</a> がおすすめです。';
      btn.disabled=false; btn.textContent='PDFを作成（無料）'; return;
    }
    await API.invoiceFromData(docObj(), items, companyObj(), kind, window.__tpl || 'standard', window.__theme || 'mono');
    bumpDocNo(); var _dnx=document.getElementById('doc-no'); if(_dnx) _dnx.value=nextDocNo(); recompute();
    var rem=document.getElementById('remain'); if(rem) rem.innerHTML='この1時間であと <b>'+cj.remaining+'</b> 枚まで無料で作成できます';
    if(cj.remaining<=0){ var lb2=document.getElementById('limitbox'); lb2.style.display='block'; lb2.innerHTML='今回で今の時間枠は終了です。無制限で使うなら <a href="/pricing">PRO（月額¥3,000）</a> がおすすめです。'; }
  }catch(e){ m.textContent='PDF作成に失敗しました: '+e.message; m.className='msg err'; }
  btn.disabled=false; btn.textContent='PDFを作成（無料）';
});

(function(){
  try{ var __SHARE=parseShare(); if(__SHARE){ enterShareView(__SHARE); return; } }catch(e){}
  document.getElementById('issue').value=new Date().toISOString().slice(0,10);
  var _dnEl=document.getElementById('doc-no'); if(_dnEl && !_dnEl.value) _dnEl.value=nextDocNo();
  document.getElementById('due').value=new Date(Date.now()+1000*60*60*24*30).toISOString().slice(0,10);
  _loadImgLS(); _handleImg('co-logo','logo'); _handleImg('co-seal','seal'); renderImgRow();
  var _ir=document.getElementById('imgrow'); if(_ir) _ir.addEventListener('click',function(e){ var d=e.target.closest('.imgdel'); if(!d)return; var k=d.getAttribute('data-k'); if(k==='logo'){window.__colog='';try{localStorage.removeItem('free_logo');}catch(e){}} else {window.__coseal='';try{localStorage.removeItem('free_seal');}catch(e){}} var fi=document.getElementById(k==='logo'?'co-logo':'co-seal'); if(fi)fi.value=''; renderImgRow(); recompute(); });
  loadCo();
  // 初期タイプ: ?type 優先、無ければ data-kind
  var initKind=kind; try{ var qt=new URLSearchParams(location.search).get('type'); if(qt) initKind=qt; }catch(e){}
  if(seg){ var qb=document.querySelector('#seg button[data-kind="'+initKind+'"]');
    if(qb){ Array.prototype.forEach.call(seg.children,function(x){x.classList.remove('on');}); qb.classList.add('on'); } }
  applyKind(initKind);
  // 外部ツール（計算サテライト等）からの事前入力: #p=<base64url JSON {it:[[name,qty,unit,price,rate,wh]],cn,no}>
  var __PRE=null; try{ var pm=(location.hash||'').match(/[#&]p=([^&]+)/); if(pm){ var po=JSON.parse(_b64d(decodeURIComponent(pm[1]))); if(po&&po.it&&po.it.length) __PRE=po; } }catch(e){}
  if(editDocId){ loadDocForEdit(editDocId); }
  else if(__PRE){
    rowsEl.innerHTML='';
    __PRE.it.slice(0,20).forEach(function(r){ rowsEl.insertAdjacentHTML('beforeend', rowHtml({name:String(r[0]||''),qty:(r[1]!=null?r[1]:1),unit:String(r[2]||'式'),unit_price:parseInt(r[3],10)||0})); var rw=rowsEl.lastElementChild; var rs=rw.querySelector('.i-rate'); if(rs&&r[4]!=null) rs.value=String(r[4]); var wc=rw.querySelector('.i-wh'); if(wc&&r[5]) wc.checked=true; });
    if(__PRE.cn){ var ce=document.getElementById('cl-name'); if(ce&&!ce.value) ce.value=String(__PRE.cn); }
    if(__PRE.no){ var ne=document.getElementById('notes'); if(ne&&!ne.value) ne.value=String(__PRE.no); }
    try{ history.replaceState(null,'',location.pathname+location.search); }catch(e){}
    setTimeout(function(){ toast('計算結果を明細に反映しました'); },400);
  }
  else if(!loadDraft()){ addRow({name:'',unit:'式',unit_price:0}); }
  recompute();
  // 入力内容クリアリンク
  var _mk=document.getElementById('make');
  if(_mk && _mk.parentNode){ var _cl=document.createElement('button'); _cl.type='button'; _cl.textContent='入力内容をクリア'; _cl.style.cssText='display:block;margin:10px auto 0;background:none;border:none;color:#8294a8;font-size:12.5px;cursor:pointer;text-decoration:underline'; _cl.addEventListener('click',function(){ if(!confirm('取引先・明細をクリアして新しい書類を作成しますか？\\n（会社情報・ロゴ・印影は保持されます）'))return; clearDraft(); document.getElementById('cl-name').value=''; document.getElementById('cl-hon').value='御中'; document.getElementById('notes').value=''; var dd=document.getElementById('due'); if(dd)dd.value=new Date(Date.now()+1000*60*60*24*30).toISOString().slice(0,10); rowsEl.innerHTML=''; addRow({name:'',unit:'式',unit_price:0}); var _dn2=document.getElementById('doc-no'); if(_dn2)_dn2.value=nextDocNo(); editDocId=null; try{ var u=new URL(location.href); u.searchParams.delete('doc'); history.replaceState(null,'',u.toString()); }catch(e){} rebuildSaveButtons(); recompute(); }); _mk.parentNode.appendChild(_cl); }
  // テンプレート切替
  window.__tpl='standard';
  var tplseg=document.getElementById('tplseg');
  if(tplseg){ tplseg.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
    Array.prototype.forEach.call(this.querySelectorAll('button'),function(x){x.classList.remove('on');}); b.classList.add('on');
    window.__tpl=b.getAttribute('data-tpl');
    var pv=document.querySelector('.pv'); if(pv){ pv.classList.remove('classic','minimal'); if(window.__tpl==='classic'||window.__tpl==='minimal') pv.classList.add(window.__tpl); }
    recompute();
  }); }
  injectToolCSS();
  try{ var _pb=document.querySelector('.card.right .pvbody'); var _cta=_pb?_pb.querySelector('.cta'):null; if(_pb&&_cta){ var _cv=buildConvertBar(); if(_cv)_pb.insertBefore(_cv,_cta); _cta.appendChild(buildShareUI()); } }catch(e){}
  setupSave();
  refreshRemain();
})();

/* ===== 無料ツール拡張: 書類変換 & Web共有リンク + 入金導線 ===== */
function _b64e(str){ return btoa(unescape(encodeURIComponent(str))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); }
function _b64d(s){ s=String(s).replace(/-/g,'+').replace(/_/g,'/'); while(s.length%4)s+='='; return decodeURIComponent(escape(atob(s))); }
function buildPayload(){
  var items=collect().filter(function(it){return it.name||it.unit_price;});
  var dn=document.getElementById('doc-no');
  return { k:kind, p:(window.__tpl||'standard'),
    dn:(dn?dn.value:''), id:document.getElementById('issue').value, dd:document.getElementById('due').value,
    cn:document.getElementById('cl-name').value, ch:document.getElementById('cl-hon').value, no:document.getElementById('notes').value,
    co:document.getElementById('co-name').value, cr:document.getElementById('co-reg').value, ca:document.getElementById('co-addr').value, ce:document.getElementById('co-email').value, cb:document.getElementById('co-bank').value,
    it:items.map(function(it){return [it.name,it.qty,it.unit,it.unit_price,it.tax_rate,it.withholding];}) };
}
function parseShare(){ try{ var m=(location.hash||'').match(/[#&]s=([^&]+)/); if(!m)return null; var o=JSON.parse(_b64d(decodeURIComponent(m[1]))); return (o&&o.it)?o:null; }catch(e){ return null; } }
function toast(msg){ var t=document.getElementById('__toast'); if(!t){ t=document.createElement('div'); t.id='__toast'; t.style.cssText='position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(20px);background:#13263b;color:#fff;font-size:13.5px;font-weight:700;padding:11px 18px;border-radius:12px;box-shadow:0 12px 30px -10px rgba(19,38,59,.6);z-index:9999;opacity:0;transition:.25s;max-width:90vw;text-align:center'; document.body.appendChild(t);} t.textContent=msg; requestAnimationFrame(function(){ t.style.opacity='1'; t.style.transform='translateX(-50%) translateY(0)'; }); clearTimeout(t.__h); t.__h=setTimeout(function(){ t.style.opacity='0'; t.style.transform='translateX(-50%) translateY(20px)'; },2600); }

function convertTo(k){
  if(seg){ Array.prototype.forEach.call(seg.children,function(x){x.classList.remove('on');}); var sb=seg.querySelector('[data-kind="'+k+'"]'); if(sb)sb.classList.add('on'); }
  applyKind(k);
  var dn=document.getElementById('doc-no'); if(dn) dn.value=nextDocNo();
  var is=document.getElementById('issue'); if(is) is.value=new Date().toISOString().slice(0,10);
  var K=API.kindCfg(k);
  if(K.due){ var du=document.getElementById('due'); if(du&&!du.value) du.value=new Date(Date.now()+1000*60*60*24*30).toISOString().slice(0,10); }
  recompute(); saveDraft();
  toast('同じ内容で「'+K.t+'」を作成しました');
  try{ document.querySelector('.card.right').scrollIntoView({behavior:'smooth',block:'start'}); }catch(e){}
}
function buildConvertBar(){
  if(!seg) return null;
  var kinds=Array.prototype.map.call(seg.children,function(b){return {k:b.getAttribute('data-kind'),t:b.textContent};});
  var wrap=document.createElement('div'); wrap.id='convbar'; wrap.className='convbar';
  function render(){ var cur=kind;
    var btns=kinds.filter(function(x){return x.k!==cur;}).map(function(x){ return '<button type="button" data-to="'+x.k+'">'+x.t+'</button>'; }).join('');
    wrap.innerHTML='<div class="cv-lb">✓ 入力はそのまま、<b>別の書類も無料で作成</b>（見積→請求→納品→領収）</div><div class="cv-bs">'+btns+'</div>'; }
  render();
  wrap.addEventListener('click',function(e){ var b=e.target.closest('button[data-to]'); if(!b)return; convertTo(b.getAttribute('data-to')); render(); });
  if(seg) seg.addEventListener('click',function(){ setTimeout(render,0); });
  return wrap;
}
function buildShareUI(){
  var box=document.createElement('div'); box.id='sharebox'; box.className='sharebox';
  box.innerHTML='<button type="button" id="sharebtn" class="sharebtn"><svg viewBox="0 0 24 24" aria-hidden="true" style="display:inline-block;vertical-align:-0.18em;width:1.1em;height:1.1em;fill:none;stroke:#1f6fe5;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 1px #4cc5ff) drop-shadow(0 0 4px rgba(37,111,229,.75))"><path d="M9.5 14.5l5-5"/><path d="M11 7l1.2-1.2a4 4 0 0 1 5.9 5.9L17 13"/><path d="M13 17l-1.2 1.2a4 4 0 0 1-5.9-5.9L7 11"/></svg> 共有リンクを作成（PDF添付せずURLで送る）</button>'
    +'<div id="shareout" class="shareout" style="display:none">'
    +'<div class="so-lb">このリンクを送るだけ。相手はブラウザで内容を確認し、PDFもダウンロードできます。</div>'
    +'<div class="so-row"><input id="shareurl" readonly><button type="button" id="sharecopy">コピー</button></div>'
    +'<div class="so-note">※ ロゴ・印影はリンクに含まれません。内容はリンク内だけに保持され、サーバーには保存されません。</div>'
    +'</div>';
  box.addEventListener('click',function(e){
    if(e.target.id==='sharebtn'){
      var items=collect().filter(function(it){return it.name||it.unit_price;});
      if(!items.length){ toast('明細を入力してから共有リンクを作成してください'); return; }
      if(!document.getElementById('cl-name').value){ toast('取引先名を入力してください'); return; }
      var url=location.origin+location.pathname+'#s='+_b64e(JSON.stringify(buildPayload()));
      var out=document.getElementById('shareout'); out.style.display='block';
      var inp=document.getElementById('shareurl'); inp.value=url; inp.focus(); inp.select();
    } else if(e.target.id==='sharecopy'){
      var inp=document.getElementById('shareurl'); inp.select(); var ok=false; try{ ok=document.execCommand('copy'); }catch(e){}
      if(navigator.clipboard){ navigator.clipboard.writeText(inp.value).then(function(){toast('共有リンクをコピーしました');},function(){ toast(ok?'共有リンクをコピーしました':'手動でコピーしてください'); }); }
      else { toast(ok?'共有リンクをコピーしました':'手動でコピーしてください'); }
    }
  });
  return box;
}

function injectToolCSS(){
  var s=document.createElement('style'); s.textContent=
   '.convbar{margin:14px 0 2px;padding:12px 14px;border:1px dashed var(--ac,#1766e6);border-radius:12px;background:var(--surf2,#f3f8ff)}'
  +'.convbar .cv-lb{font-size:12.5px;color:var(--mut,#45607a);margin-bottom:8px}'
  +'.convbar .cv-lb b{color:var(--ac,#1766e6)}'
  +'.convbar .cv-bs{display:flex;flex-wrap:wrap;gap:7px}'
  +'.convbar .cv-bs button{font-family:inherit;font-size:12.5px;font-weight:700;border:1px solid var(--ac,#1766e6);color:var(--ac,#1766e6);background:#fff;border-radius:999px;padding:7px 13px;cursor:pointer}'
  +'.convbar .cv-bs button:hover{background:var(--ac,#1766e6);color:#fff}'
  +'.sharebox{margin-top:10px}'
  +'.sharebtn{width:100%;font-family:inherit;font-size:13.5px;font-weight:800;border:1.5px solid var(--ac,#1766e6);color:var(--ac,#1766e6);background:#fff;border-radius:11px;padding:11px;cursor:pointer}'
  +'.sharebtn:hover{background:var(--ac-s,#eaf1fe)}'
  +'.shareout{margin-top:10px;background:var(--surf2,#f3f8ff);border:1px solid var(--bd,#e2eaf4);border-radius:11px;padding:11px 12px}'
  +'.shareout .so-lb{font-size:12px;color:var(--mut,#45607a);margin-bottom:7px}'
  +'.shareout .so-row{display:flex;gap:6px}'
  +'.shareout .so-row input{flex:1;min-width:0;font-family:inherit;font-size:12px;padding:8px 9px;border:1px solid var(--bd,#cfe0f2);border-radius:8px;background:#fff;color:#333}'
  +'.shareout .so-row button{font-family:inherit;font-size:12.5px;font-weight:800;border:none;border-radius:8px;padding:8px 14px;background:var(--ac,#1766e6);color:#fff;cursor:pointer}'
  +'.shareout .so-note{font-size:11px;color:var(--faint,#8aa0b6);margin-top:7px;line-height:1.5}';
  document.head.appendChild(s);
}
function injectShareCSS(){
  var s=document.createElement('style'); s.textContent=
   'body.shared-view .promo,body.shared-view #docnav,body.shared-view .hero,body.shared-view .art,body.shared-view .sell,body.shared-view .faqwrap,body.shared-view .hdr .pro,body.shared-view .card.pad,body.shared-view .pvhd,body.shared-view #convbar,body.shared-view #sharebox{display:none!important}'
  +'body.shared-view .wrap{grid-template-columns:1fr!important;max-width:720px;margin-left:auto;margin-right:auto}'
  +'body.shared-view .cta .btn,body.shared-view .remain,body.shared-view .limitbox,body.shared-view .msg{display:none}'
  +'.paybar{background:linear-gradient(120deg,#0f2f7a,#1766e6);color:#fff;border-radius:16px;padding:18px 20px;margin:0 0 14px;box-shadow:0 16px 40px -20px rgba(23,102,230,.5)}'
  +'.paybar .pb-from{font-size:12.5px;opacity:.9}'
  +'.paybar .pb-amt{font-size:30px;font-weight:900;letter-spacing:-.02em;margin:2px 0 6px}'
  +'.paybar .pb-row{font-size:13px;margin:3px 0;opacity:.96}'
  +'.paybar .pb-bank{background:rgba(255,255,255,.15);border-radius:10px;padding:9px 12px;margin-top:9px;font-size:13.5px;font-weight:700;word-break:break-all}'
  +'.sv-dl{display:flex;flex-direction:column;gap:9px;margin-top:12px}'
  +'.sv-dl .dlbtn{display:inline-flex;align-items:center;justify-content:center;gap:7px;background:var(--ac,#1766e6);color:#fff;border:none;border-radius:11px;padding:13px;font-size:15px;font-weight:800;cursor:pointer;font-family:inherit}'
  +'.sv-dl .mk{text-align:center;font-size:12.5px;color:var(--mut,#5a6b7b)}'
  +'.sv-dl .mk a{color:var(--ac,#1766e6);font-weight:700}'
  +'.sv-cta{margin-top:4px;border:1px solid var(--bd,#e2eaf4);background:var(--surf2,#f6faff);border-radius:13px;padding:15px 16px;text-align:center}'
  +'.sv-cta .sct-h{font-size:14px;font-weight:800;color:var(--ink,#16202b)}'
  +'.sv-cta .sct-h b{color:var(--ac,#1766e6)}'
  +'.sv-cta .sct-p{font-size:12px;color:var(--mut,#5a6b7b);margin:5px 0 12px;line-height:1.6}'
  +'.sv-cta .sct-btn{display:inline-flex;align-items:center;gap:6px;background:var(--ac,#1766e6);color:#fff;text-decoration:none;font-weight:800;font-size:13.5px;padding:10px 18px;border-radius:10px}'
  +'.sv-cta .sct-btn:hover{background:#1257ca}';
  document.head.appendChild(s);
}

function enterShareView(P){
  window.__colog=''; window.__coseal='';
  function set(id,v){ var el=document.getElementById(id); if(el!=null&&v!=null) el.value=v; }
  set('co-name',P.co); set('co-reg',P.cr); set('co-addr',P.ca); set('co-email',P.ce); set('co-bank',P.cb);
  set('cl-name',P.cn); set('cl-hon',P.ch||'御中'); set('notes',P.no);
  set('doc-no',P.dn); set('issue',P.id); set('due',P.dd);
  rowsEl.innerHTML='';
  (P.it||[]).forEach(function(a){ rowsEl.insertAdjacentHTML('beforeend', rowHtml({name:a[0],qty:a[1],unit:a[2],unit_price:a[3]})); });
  var rws=rowsEl.querySelectorAll('.rw');
  (P.it||[]).forEach(function(a,i){ var rw=rws[i]; if(!rw)return; var rs=rw.querySelector('.i-rate'); if(rs&&a[4]!=null)rs.value=String(a[4]); var wc=rw.querySelector('.i-wh'); if(wc&&a[5])wc.checked=true; });
  var k=P.k||'invoice';
  window.__tpl=P.p||'standard';
  var pv=document.querySelector('.pv'); if(pv){ pv.classList.remove('classic','minimal'); if(window.__tpl!=='standard')pv.classList.add(window.__tpl); }
  if(seg){ Array.prototype.forEach.call(seg.children,function(x){x.classList.remove('on');}); var sb=seg.querySelector('[data-kind="'+k+'"]'); if(sb)sb.classList.add('on'); }
  applyKind(k);
  document.body.classList.add('shared-view');
  injectShareCSS();
  var items=collect(); var c=API.calc(items); var K=API.kindCfg(k); var pay=K.wh?c.payable:c.total;
  var pb=document.createElement('div'); pb.className='paybar';
  var h='<div class="pb-from">'+API.esc(P.co||'発行者')+' からの'+API.esc(K.t)+'</div><div class="pb-amt">'+API.yen(pay)+'</div>';
  if(K.due&&P.dd) h+='<div class="pb-row">お支払期限 : '+API.esc(P.dd)+'</div>';
  if(P.cb) h+='<div class="pb-bank">お振込先 : '+API.esc(P.cb)+'</div>';
  pb.innerHTML=h;
  var dl=document.createElement('div'); dl.className='sv-dl';
  dl.innerHTML='<button type="button" class="dlbtn" id="svdl">この'+API.esc(K.t)+'をPDFでダウンロード</button>'
    +'<div class="sv-cta"><div class="sct-h">あなたも <b>無料</b> で書類を作れます</div>'
    +'<div class="sct-p">請求書・見積書・納品書・領収書を、登録不要・インボイス対応で。日本語PDFをその場でダウンロードできます。</div>'
    +'<a class="sct-btn" href="/invoice?utm_source=shared_view&utm_medium=referral&utm_campaign=share_cta">無料で書類を作ってみる →</a></div>';
  var right=document.querySelector('.card.right'); var pvbody=right?right.querySelector('.pvbody'):null;
  if(pvbody){ pvbody.insertBefore(pb, pvbody.firstChild); }
  var cta=right?right.querySelector('.cta'):null; if(cta){ cta.appendChild(dl); }
  var svdl=document.getElementById('svdl');
  if(svdl) svdl.addEventListener('click',async function(){ var btn=this; btn.disabled=true; var old=btn.textContent; btn.textContent='作成中…';
    try{ await API.invoiceFromData(docObj(), collect().filter(function(it){return it.name||it.unit_price;}), companyObj(), kind, window.__tpl||'standard', window.__theme||'mono'); }
    catch(e){ toast('PDF作成に失敗しました'); }
    btn.disabled=false; btn.textContent=old; });
  try{ document.title=(P.co?P.co+' ':'')+K.t; }catch(e){}
}

/* ===== ログイン時: アカウントに保存 ===== */
function buildSavePayload(){
  var items=collect().filter(function(it){return it.name||it.unit_price;});
  return { type:kind, status:'pending',
    client_name:document.getElementById('cl-name').value, honorific:document.getElementById('cl-hon').value,
    issue_date:document.getElementById('issue').value, due_date:document.getElementById('due').value||null,
    bank:document.getElementById('co-bank').value, notes:document.getElementById('notes').value,
    company:{company_name:document.getElementById('co-name').value, company_addr:document.getElementById('co-addr').value, reg_number:document.getElementById('co-reg').value, default_bank:document.getElementById('co-bank').value},
    items:items };
}
// ライブプレビュー用（実際のPDF生成と同じ関数・同じ値で描画）
window.__pdfGen=function(){ return API.raw.invoiceFromData(docObj(), collect().filter(function(it){return it.name||it.unit_price;}), companyObj(), kind, window.__tpl||'standard', window.__theme||'mono'); };
var _isAuthed=false;
async function loadDocForEdit(id){
  try{
    var r=await fetch('/api/documents/'+id,{credentials:'same-origin'});
    if(!r.ok){ toast('書類を読み込めませんでした'); editDocId=null; rebuildSaveButtons(); addRow({name:'',unit:'式',unit_price:0}); recompute(); return; }
    var d=await r.json(); var doc=d.document||{}, items=d.items||[], co=d.company||{};
    function sv(id2,v){ var el=document.getElementById(id2); if(el&&v!=null) el.value=v; }
    sv('cl-name',doc.client_name); sv('cl-hon',doc.honorific||'御中');
    sv('issue',doc.issue_date); sv('due',doc.due_date||'');
    sv('notes',doc.notes||''); sv('doc-no',doc.doc_no||'');
    sv('co-name',co.company_name); sv('co-reg',co.reg_number); sv('co-addr',co.company_addr); sv('co-email',co.email); sv('co-bank',doc.bank||co.default_bank||'');
    rowsEl.innerHTML='';
    (items.length?items:[{name:'',unit:'式',unit_price:0}]).forEach(function(it){ rowsEl.insertAdjacentHTML('beforeend', rowHtml(it)); });
    var rws=rowsEl.querySelectorAll('.rw');
    items.forEach(function(it,i){ var rw=rws[i]; if(!rw)return; var rs=rw.querySelector('.i-rate'); if(rs&&it.tax_rate!=null)rs.value=String(it.tax_rate); var wc=rw.querySelector('.i-wh'); if(wc)wc.checked=(Number(it.withholding)===1); });
    recompute();
    toast('保存した書類を読み込みました（編集できます）');
  }catch(e){ toast('読み込みエラー'); editDocId=null; rebuildSaveButtons(); addRow({name:'',unit:'式',unit_price:0}); recompute(); }
}
async function doSave(btn, mode){
  var items=collect().filter(function(it){return it.name||it.unit_price;});
  if(!items.length){ toast('明細を入力してください'); return; }
  if(!document.getElementById('cl-name').value){ toast('取引先名を入力してください'); return; }
  var overwrite=(mode==='overwrite' && editDocId);
  btn.disabled=true; var old=btn.innerHTML; btn.textContent='保存中…';
  try{
    var url=overwrite?('/api/documents/'+editDocId):'/api/documents';
    var r=await fetch(url,{method:overwrite?'PUT':'POST',headers:{'content-type':'application/json'},credentials:'same-origin',body:JSON.stringify(buildSavePayload())});
    var j=await r.json().catch(function(){return{};});
    if(r.ok){
      if(overwrite){ toast('上書き保存しました'+(j.doc_no?'（'+j.doc_no+'）':'')); }
      else {
        toast('アカウントに保存しました'+(j.doc_no?'（'+j.doc_no+'）':''));
        if(j.id){ editDocId=String(j.id); try{ var u=new URL(location.href); u.searchParams.set('doc', j.id); history.replaceState(null,'',u.toString()); }catch(e){} rebuildSaveButtons(); }
      }
    }
    else if(r.status===403&&j.upsell){ if(confirm('無料プランで保存できる書類は5件までです。\nPROプラン（期間限定 月¥2,000）にアップグレードしますか？')) location.href='/pricing'; }
    else { toast('保存に失敗しました: '+(j.error||('HTTP '+r.status))); }
  }catch(e){ toast('通信エラーが発生しました'); }
  btn.disabled=false; btn.innerHTML=old;
}
function rebuildSaveButtons(){
  if(!_isAuthed) return;
  var mk=document.getElementById('make'); if(!mk||!mk.parentNode) return;
  ['acctsave','acctsave2'].forEach(function(id){ var e=document.getElementById(id); if(e&&e.parentNode) e.parentNode.removeChild(e); });
  var b=document.createElement('button'); b.type='button'; b.id='acctsave'; b.className=mk.className;
  b.style.cssText='margin-top:10px;background:#0f7a43;border-color:#0f7a43;color:#fff';
  b.innerHTML=editDocId?'<svg viewBox="0 0 24 24" aria-hidden="true" style="display:inline-block;vertical-align:-0.18em;width:1.1em;height:1.1em;fill:none;stroke:#1f6fe5;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 1px #4cc5ff) drop-shadow(0 0 4px rgba(37,111,229,.75))"><path d="M5 3h11l3 3v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M8 3v5h7"/><rect x="8" y="13" width="8" height="6"/></svg> 上書き保存':'<svg viewBox="0 0 24 24" aria-hidden="true" style="display:inline-block;vertical-align:-0.18em;width:1.1em;height:1.1em;fill:none;stroke:#1f6fe5;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 1px #4cc5ff) drop-shadow(0 0 4px rgba(37,111,229,.75))"><path d="M5 3h11l3 3v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M8 3v5h7"/><rect x="8" y="13" width="8" height="6"/></svg> アカウントに保存';
  b.addEventListener('click',function(){ doSave(b, editDocId?'overwrite':'new'); });
  mk.parentNode.insertBefore(b, mk.nextSibling);
  if(editDocId){
    var b2=document.createElement('button'); b2.type='button'; b2.id='acctsave2'; b2.className=mk.className;
    b2.style.cssText='margin-top:8px;background:#fff;border:1.5px solid #0f7a43;color:#0f7a43';
    b2.innerHTML='＋ 新規として保存';
    b2.addEventListener('click',function(){ doSave(b2, 'new'); });
    b.parentNode.insertBefore(b2, b.nextSibling);
  }
}
function setupSave(){
  fetch('/api/auth/me',{credentials:'same-origin'}).then(function(r){return r.json();}).then(function(me){
    if(!(me&&me.authed)) return;
    _isAuthed=true; rebuildSaveButtons();
  }).catch(function(){});
}

})();

/* ===== 埋め込みモード（?embed=1）: 外部サイトのiframeから利用。ヘッダー・フッター・記事を隠し、Powered by を表示 ===== */
(function(){
  var q; try{ q=new URLSearchParams(location.search); }catch(e){ return; }
  if(q.get('embed')!=='1') return;
  document.documentElement.classList.add('embed-view');
  var st=document.createElement('style'); st.textContent=
    '.embed-view body{background:#fff}'
   +'.embed-view .promo,.embed-view .hdr,.embed-view .fb-hdr,.embed-view #docnav,.embed-view .hero,.embed-view .art,.embed-view .sell,.embed-view .faqwrap,.embed-view footer.ft,.embed-view .fb-ft-auth{display:none!important}'
   +'.embed-view .wrap{padding-top:12px}'
   +'.fb-powered{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px 14px 16px;font:500 12.5px/1.4 "Noto Sans JP","Hiragino Sans",sans-serif;color:#6c7a8a}'
   +'.fb-powered a{color:#1E4DD8;font-weight:700;text-decoration:none}.fb-powered a:hover{text-decoration:underline}';
  document.head.appendChild(st);
  var ref=q.get('ref')||''; var utm='?utm_source=embed&utm_medium=iframe'+(ref?'&utm_campaign='+encodeURIComponent(ref):'');
  function addPowered(){
    if(document.querySelector('.fb-powered')) return;
    var d=document.createElement('div'); d.className='fb-powered';
    d.innerHTML='この書類ツールは <a href="https://free-bizdocs.com/'+utm+'" target="_blank" rel="noopener">Free BizDoc（無料ビジネス書類メーカー）</a> が提供しています';
    document.body.appendChild(d);
  }
  function reportH(){ try{ var h=Math.ceil(document.documentElement.scrollHeight)+2; parent.postMessage({t:'fbH',h:h},'*'); }catch(e){} }
  // 埋め込み内のページ遷移（書類タブ・変換バー等）でも embed=1 を引き継ぐ
  var KEEP=['/invoice','/quote','/delivery','/purchase-order','/receipt'];
  document.addEventListener('click',function(e){
    var a=e.target&&e.target.closest?e.target.closest('a[href]'):null; if(!a) return;
    var u; try{ u=new URL(a.getAttribute('href'),location.href); }catch(_){ return; }
    if(u.origin!==location.origin) { if(!a.target) a.target='_blank'; return; }
    if(KEEP.indexOf(u.pathname.replace(/\.html$/,''))<0) { if(!a.target) a.target='_blank'; return; }
    if(u.searchParams.get('embed')!=='1'){ u.searchParams.set('embed','1'); if(ref) u.searchParams.set('ref',ref); a.setAttribute('href',u.pathname+u.search+u.hash); }
  },true);
  function boot(){ addPowered(); reportH(); setInterval(reportH,800); window.addEventListener('resize',reportH); }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else boot();
})();

/* ===== review nudge (AEO / social proof): after a PDF download, invite happy users to leave a real review. shows once per browser, dismissible. ===== */
/* ダウンロード直後に「ほしい機能・テンプレート」をその場で1行送れる要望ボックス。
   登録不要・名前任意。送信後におまけでレビュー応援リンクを提示（レビューは副次）。 */
(function(){
  try{
    var KEY='fbd_req_nudge_v1';
    function shown(){ try{return localStorage.getItem(KEY)==='1';}catch(e){return false;} }
    function mark(){ try{localStorage.setItem(KEY,'1');}catch(e){} }
    var REVIEW='<div style="margin-top:12px;border-top:1px solid rgba(255,255,255,.12);padding-top:11px">'
      +'<div style="color:#9fb4cc;font-size:12.5px;margin-bottom:8px">気に入ったら、応援（レビュー）もぜひ 🙏</div>'
      +'<div style="display:flex;gap:8px;flex-wrap:wrap">'
      +'<a href="https://www.producthunt.com/products/free-bizdoc" target="_blank" rel="noopener" style="flex:1;min-width:130px;text-align:center;background:#da552f;color:#fff;text-decoration:none;font-weight:700;border-radius:9px;padding:8px 10px;font-size:13px">Product Huntで応援</a>'
      +'<a href="https://www.saashub.com/free-bizdoc" target="_blank" rel="noopener" style="flex:1;min-width:130px;text-align:center;background:#2f8cf0;color:#fff;text-decoration:none;font-weight:700;border-radius:9px;padding:8px 10px;font-size:13px">SaaSHubでレビュー</a></div></div>';
    function show(){
      if(shown()||document.getElementById('fbd-req')) return;
      var b=document.createElement('div'); b.id='fbd-req'; b.setAttribute('role','dialog'); b.setAttribute('aria-label','ご要望の送信');
      b.style.cssText='position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:99999;max-width:440px;width:calc(100% - 32px);background:#13263b;color:#fff;border-radius:14px;box-shadow:0 14px 40px -10px rgba(0,0,0,.5);padding:15px 16px;font-size:14px;line-height:1.6';
      b.innerHTML='<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px"><div style="font-weight:700">ほしい機能・テンプレートはありますか？</div><button type="button" id="fbd-x" aria-label="閉じる" style="background:none;border:none;color:#9fb4cc;font-size:18px;line-height:1;cursor:pointer;padding:0 2px">×</button></div>'
        +'<div id="fbd-main">'
        +'<div style="color:#cdd9e7;margin:6px 0 10px;font-size:13px">「こんな書類が欲しい」「ここが不便」——ひと言で開発に届きます（登録不要）。</div>'
        +'<textarea id="fbd-t" rows="2" maxlength="2000" placeholder="例：英語の請求書にEUのVAT欄がほしい／○○テンプレを追加してほしい" style="width:100%;box-sizing:border-box;border:1px solid #2d4258;background:#0f1d2e;color:#fff;border-radius:10px;padding:10px 12px;font-size:14px;font-family:inherit;line-height:1.6;resize:vertical"></textarea>'
        +'<input id="fbd-n" type="text" maxlength="100" placeholder="ニックネーム（任意）" style="width:100%;box-sizing:border-box;margin-top:8px;border:1px solid #2d4258;background:#0f1d2e;color:#fff;border-radius:10px;padding:9px 12px;font-size:13.5px;font-family:inherit">'
        +'<div style="display:flex;align-items:center;gap:10px;margin-top:10px"><button type="button" id="fbd-send" style="background:#2f8cf0;color:#fff;border:none;font-weight:800;border-radius:10px;padding:10px 18px;font-size:14px;cursor:pointer">送信</button><span id="fbd-st" style="font-size:12.5px;color:#9fb4cc"></span></div>'
        +'</div>';
      document.body.appendChild(b);
      var closed=false;
      function close(){ if(closed)return; closed=true; mark(); if(b.parentNode) b.remove(); }
      document.getElementById('fbd-x').addEventListener('click',close);
      document.getElementById('fbd-send').addEventListener('click',function(){
        var t=document.getElementById('fbd-t'), n=document.getElementById('fbd-n'), st=document.getElementById('fbd-st'), btn=this;
        var text=(t.value||'').trim(); if(text.length<2){ st.textContent='内容を入力してください'; t.focus(); return; }
        btn.disabled=true; btn.style.opacity='.6'; st.textContent='送信中…';
        fetch('/api/feedback',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({kind:'要望',body:text,name:(n.value||'').trim(),page:location.pathname,lang:'ja'})})
          .then(function(r){return r.json();})
          .then(function(j){
            if(j&&j.ok){ mark(); document.getElementById('fbd-main').innerHTML='<div style="color:#cdd9e7;margin:8px 0 2px;font-size:13.5px">ありがとうございます！開発の参考にします 🙏</div>'+REVIEW; }
            else { btn.disabled=false; btn.style.opacity='1'; st.textContent=(j&&j.error)||'送信に失敗しました'; }
          })
          .catch(function(){ btn.disabled=false; btn.style.opacity='1'; st.textContent='送信に失敗しました。時間をおいてお試しください'; });
      });
    }
    function arm(){ if(shown()) return; setTimeout(show,2500); }
    document.addEventListener('click',function(e){ if(e.target.closest('#make,#svdl')) arm(); }, true);
  }catch(e){}
})();

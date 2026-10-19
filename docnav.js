/* docnav.js — 全書類リンクの共通スライダー（1行・自動ループ・ドラッグ/スワイプ対応） */
(function(){
  'use strict';
  var DOCS=[
    ['/invoice','請求書'],['/quote','見積書'],['/delivery','納品書'],
    ['/purchase-order','発注書'],['/receipt','領収書'],['/inkan','電子印鑑'],
    ['/rirekisho','履歴書'],['/shokumu','職務経歴書'],['/soufu','送付状'],
    ['/taishoku','退職届'],['/shiboudouki','志望動機書'],['/entrysheet','ES'],
    ['/skillsheet','スキルシート']
  ];
  var host=document.getElementById('docnav');
  if(!host||host.dataset.ready) return;
  host.dataset.ready='1';

  var CSS='.docnav{position:relative;overflow:hidden;background:var(--surf,#fff);border-bottom:1px solid var(--bd,#e6ebf2);'
   +'-webkit-mask-image:linear-gradient(90deg,transparent,#000 5%,#000 95%,transparent);mask-image:linear-gradient(90deg,transparent,#000 5%,#000 95%,transparent)}'
   +'.docnav-track{display:flex;gap:8px;width:max-content;padding:12px 10px;cursor:grab;touch-action:pan-y;user-select:none;-webkit-user-select:none}'
   +'.docnav-track.grabbing{cursor:grabbing}'
   +'.docnav-item{flex:0 0 auto;font-size:13px;font-weight:700;color:var(--mut,#5a6b80);text-decoration:none;padding:8px 15px;border-radius:999px;'
   +'background:var(--surf2,#f1f5fb);border:1px solid var(--bd,#dce5f0);white-space:nowrap;-webkit-tap-highlight-color:transparent}'
   +'.docnav-item:hover{background:#eef4ff;color:var(--ac,#1766e6)}'
   +'.docnav-item.on{background:linear-gradient(120deg,var(--ac,#1766e6),#2f9bf0);color:#fff;border-color:transparent;box-shadow:0 4px 12px -4px rgba(23,102,230,.5)}';
  if(!document.getElementById('docnav-style')){
    var st=document.createElement('style');st.id='docnav-style';st.textContent=CSS;document.head.appendChild(st);
  }

  var path=location.pathname.replace(/\.html$/,'');
  if(path.length>1) path=path.replace(/\/$/,'');

  function makeSet(){
    var frag=document.createDocumentFragment();
    DOCS.forEach(function(d){
      var a=document.createElement('a');
      a.href=d[0];a.textContent=d[1];a.className='docnav-item';a.draggable=false;
      if(d[0]===path){a.className+=' on';a.setAttribute('aria-current','page');}
      frag.appendChild(a);
    });
    return frag;
  }

  var track=document.createElement('div');track.className='docnav-track';
  track.appendChild(makeSet());
  track.appendChild(makeSet());
  host.appendChild(track);

  var setW=0,x=0,dragging=false,startX=0,startOff=0,moved=0,paused=false;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion:reduce)').matches;
  var SPEED=0.4, THRESH=6, captured=false, pid=null;

  function measure(){setW=track.scrollWidth/2;}
  function norm(){ if(setW>0){ while(x<=-setW)x+=setW; while(x>0)x-=setW; } }
  function apply(){track.style.transform='translateX('+x+'px)';}
  measure();
  window.addEventListener('resize',measure);

  function frame(){
    if(!dragging&&!paused&&!reduce){x-=SPEED;norm();apply();}
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  track.addEventListener('pointerdown',function(e){
    dragging=true;moved=0;startX=e.clientX;startOff=x;pid=e.pointerId;captured=false;
    track.classList.add('grabbing');
  });
  // move/up on window so a drag keeps tracking even if the pointer leaves the strip
  window.addEventListener('pointermove',function(e){
    if(!dragging)return;
    var dx=e.clientX-startX;if(Math.abs(dx)>moved)moved=Math.abs(dx);
    // capture only once it is clearly a drag — a plain tap keeps the click on the <a> so the link navigates
    if(!captured&&moved>THRESH&&track.setPointerCapture){try{track.setPointerCapture(pid);captured=true;}catch(_){}}
    x=startOff+dx;norm();apply();
  });
  function endDrag(){
    if(dragging){
      dragging=false;track.classList.remove('grabbing');
      if(captured&&track.releasePointerCapture&&pid!=null){try{track.releasePointerCapture(pid);}catch(_){}}
      captured=false;pid=null;
    }
  }
  window.addEventListener('pointerup',endDrag);
  window.addEventListener('pointercancel',endDrag);

  // suppress the click only when the user actually dragged
  track.addEventListener('click',function(e){
    if(moved>THRESH){e.preventDefault();e.stopPropagation();}
  },true);

  host.addEventListener('mouseenter',function(){paused=true;});
  host.addEventListener('mouseleave',function(){paused=false;});
})();

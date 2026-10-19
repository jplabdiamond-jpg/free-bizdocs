/* 共通カラーテーマ選択（モノクロ＋5色）。各ページで読み込む。 */
(function(){
  var THEMES=[['mono','モノクロ','#333333'],['blue','青','#1766e6'],['red','赤','#cf2a2e'],['green','緑','#179a63'],['purple','紫','#7a39c4'],['orange','橙','#e8820e']];
  var MAP={mono:'#333333',blue:'#1766e6',red:'#cf2a2e',green:'#179a63',purple:'#7a39c4',orange:'#e8820e'};
  try{ window.__theme=localStorage.getItem('free_theme')||'mono'; }catch(e){ window.__theme='mono'; }
  function applyPreview(){ document.documentElement.style.setProperty('--docac', MAP[window.__theme]||'#333333'); }
  function injectStyle(){
    if(document.getElementById('themecss'))return;
    var st=document.createElement('style'); st.id='themecss';
    st.textContent=':root{--docink:color-mix(in srgb,var(--docac,#333) 82%,#000);--docbg:color-mix(in srgb,var(--docac,#333) 8%,#fff)}'
      +'.themeseg{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:0 0 16px}'
      +'.themeseg .tlb{font-size:11px;font-weight:700;color:#93a3b5;margin-right:2px}'
      +'.themeseg .sw{display:inline-flex;align-items:center;gap:5px;font-family:inherit;font-size:11.5px;font-weight:700;color:#5a6b7d;background:#fff;border:1px solid #e2eaf4;border-radius:999px;padding:5px 11px 5px 8px;cursor:pointer}'
      +'.themeseg .sw .dot{width:12px;height:12px;border-radius:50%;background:var(--sw);border:1px solid rgba(0,0,0,.12)}'
      +'.themeseg .sw.on{border-color:var(--sw);color:#13263b;box-shadow:0 0 0 2px var(--sw) inset,0 0 0 1px #fff inset}';
    document.head.appendChild(st);
  }
  function build(){
    injectStyle();
    var host=document.querySelector('.card.pad'); if(!host){ applyPreview(); return; }
    var box=document.createElement('div'); box.className='themeseg';
    var h='<span class="tlb">カラー</span>';
    THEMES.forEach(function(t){ h+='<button type="button" class="sw'+(t[0]===window.__theme?' on':'')+'" data-th="'+t[0]+'" style="--sw:'+t[2]+'"><span class="dot"></span>'+t[1]+'</button>'; });
    box.innerHTML=h;
    host.insertBefore(box, host.firstChild);
    box.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
      [].forEach.call(this.querySelectorAll('button'),function(x){x.classList.remove('on');}); b.classList.add('on');
      window.__theme=b.getAttribute('data-th');
      try{ localStorage.setItem('free_theme',window.__theme); }catch(e){}
      applyPreview();
    });
    applyPreview();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build); else build();
})();

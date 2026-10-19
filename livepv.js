/* ライブプレビュー: 各ツールのプレビューを「実際に出力されるPDF」そのもので表示する。
   HTMLで真似たプレビューを隠し、ダウンロードと同じPDF生成関数の結果を描画するため、
   プレビューとPDFの書式・配置が必ず一致する。 */
(function(){
  if(!window.API||!API.livePreview||!API.raw) return;
  var page=location.pathname.replace(/^\//,'').replace(/\.html$/,'')||'index';
  var R=API.raw;
  var GEN={
    invoice:function(){ return window.__pdfGen&&window.__pdfGen(); },
    quote:function(){ return window.__pdfGen&&window.__pdfGen(); },
    delivery:function(){ return window.__pdfGen&&window.__pdfGen(); },
    'purchase-order':function(){ return window.__pdfGen&&window.__pdfGen(); },
    receipt:function(){ return window.__pdfGen&&window.__pdfGen(); },
    rirekisho:function(){ return R.resumePdf(buildData()); },
    shokumu:function(){ return R.careerPdf(buildData()); },
    soufu:function(){ return R.letterPdf(buildData()); },
    taishoku:function(){ return R.resignPdf(buildData()); },
    shiboudouki:function(){ return R.docPdf(buildSpec()); },
    entrysheet:function(){ return R.docPdf(buildSpec()); },
    skillsheet:function(){ return R.docPdf(buildSpec()); }
  };
  var gen=GEN[page]; if(!gen) return;
  function start(){
    var body=document.querySelector('.card.right .pvbody')||document.querySelector('.pvbody'); if(!body) return;
    var old=body.querySelector(':scope > .pv, :scope > .rv, :scope > .cv, :scope > .lv, :scope > .dv, :scope > .rz');
    if(!old) return;
    var host=document.createElement('div'); host.id='livepv';
    old.parentNode.insertBefore(host, old);
    old.style.display='none'; old.setAttribute('aria-hidden','true');
    var hd=document.querySelector('.card.right .pvhd'); if(hd&&hd.lastChild&&hd.lastChild.nodeType===3) hd.lastChild.nodeValue='プレビュー（実際のPDFと同じ表示）';
    var upd=API.livePreview(host, gen, {maxPages:3});
    window.__livePvUpdate=upd;
    ['input','change'].forEach(function(ev){ document.addEventListener(ev,function(e){ if(e.target&&e.target.closest&&e.target.closest('#livepv'))return; upd(); },true); });
    document.addEventListener('click',function(e){ var b=e.target&&e.target.closest&&e.target.closest('button,[data-kind],[data-p],[data-tpl],[data-theme]'); if(b) setTimeout(upd,0); },true);
    var t; window.addEventListener('resize',function(){ clearTimeout(t); t=setTimeout(upd,300); });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',function(){ setTimeout(start,0); }); else setTimeout(start,0);
})();

/* Free BizDoc — English tools (Invoice / Estimate / Packing Slip / Purchase Order / Receipt)
   Region-aware (US / UK / AU / CA): currency, paper size, date format, tax model, tax-ID label, bank fields.
   Self-contained: inputs, calc, live PDF preview (pdf-lib + pdf.js), share link, draft autosave. */
(function(){
'use strict';

/* ================= Region definitions ================= */
var REGIONS={
  us:{ id:'us', name:'United States', flag:'🇺🇸', cur:'USD', sym:'$', paper:'letter', date:'mdy',
    taxName:'Sales Tax', taxIdLabel:'Tax ID / EIN (optional)', taxIdPh:'12-3456789',
    addrPh:'123 Main St, Suite 100\nAustin, TX 78701', bankPh:'Bank name\nRouting No. 021000021\nAccount No. 123456789',
    mode:'rate', rateLabel:'Sales tax rate (%)', defaultRate:0,
    taxOpts:[['tax','Taxable'],['none','Exempt']],
    titles:{invoice:'Invoice',quote:'Estimate',delivery:'Packing Slip',po:'Purchase Order',receipt:'Receipt',credit:'Credit Memo',proforma:'Pro Forma Invoice',salesorder:'Sales Order',timesheet:'Timesheet',workorder:'Work Order',expense:'Expense Report',billofsale:'Bill of Sale',donation:'Donation Receipt'},
    prefix:{invoice:'INV',quote:'EST',delivery:'PS',po:'PO',receipt:'RCT',credit:'CM',proforma:'PF',salesorder:'SO',timesheet:'TS',workorder:'WO',expense:'EXP',billofsale:'BOS',donation:'DR'} },
  uk:{ id:'uk', name:'United Kingdom', flag:'🇬🇧', cur:'GBP', sym:'£', paper:'a4', date:'dmy',
    taxName:'VAT', taxIdLabel:'VAT Reg. No. (if registered)', taxIdPh:'GB123456789',
    addrPh:'10 High Street\nLondon SW1A 1AA', bankPh:'Bank name\nSort code 12-34-56\nAccount No. 12345678',
    mode:'fixed',
    taxOpts:[['20','VAT 20%'],['5','VAT 5%'],['0','Zero-rated'],['none','Exempt']],
    titles:{invoice:'Invoice',quote:'Quotation',delivery:'Delivery Note',po:'Purchase Order',receipt:'Receipt',credit:'Credit Note',proforma:'Pro Forma Invoice',salesorder:'Sales Order',timesheet:'Timesheet',workorder:'Work Order',expense:'Expense Claim',billofsale:'Bill of Sale',donation:'Donation Receipt'},
    prefix:{invoice:'INV',quote:'QUO',delivery:'DN',po:'PO',receipt:'RCT',credit:'CN',proforma:'PF',salesorder:'SO',timesheet:'TS',workorder:'WO',expense:'EXP',billofsale:'BOS',donation:'DR'} },
  au:{ id:'au', name:'Australia', flag:'🇦🇺', cur:'AUD', sym:'$', paper:'a4', date:'dmy',
    taxName:'GST', taxIdLabel:'ABN', taxIdPh:'12 345 678 901',
    addrPh:'1 George Street\nSydney NSW 2000', bankPh:'Bank name\nBSB 062-000\nAccount No. 12345678',
    mode:'fixed',
    taxOpts:[['10','GST 10%'],['0','GST-free']],
    titles:{invoice:'Tax Invoice',quote:'Quote',delivery:'Delivery Note',po:'Purchase Order',receipt:'Receipt',credit:'Credit Note',proforma:'Pro Forma Invoice',salesorder:'Sales Order',timesheet:'Timesheet',workorder:'Work Order',expense:'Expense Claim',billofsale:'Bill of Sale',donation:'Donation Receipt'},
    prefix:{invoice:'INV',quote:'QUO',delivery:'DN',po:'PO',receipt:'RCT',credit:'CN',proforma:'PF',salesorder:'SO',timesheet:'TS',workorder:'WO',expense:'EXP',billofsale:'BOS',donation:'DR'} },
  ca:{ id:'ca', name:'Canada', flag:'🇨🇦', cur:'CAD', sym:'$', paper:'letter', date:'ymd',
    taxName:'GST/HST', taxIdLabel:'GST/HST No. (if registered)', taxIdPh:'123456789RT0001',
    addrPh:'100 King Street W\nToronto, ON M5X 1A1', bankPh:'Bank name\nInstitution No. 001  Transit No. 12345\nAccount No. 1234567',
    mode:'province',
    taxOpts:[['tax','Taxable'],['none','Exempt']],
    titles:{invoice:'Invoice',quote:'Estimate',delivery:'Packing Slip',po:'Purchase Order',receipt:'Receipt',credit:'Credit Note',proforma:'Pro Forma Invoice',salesorder:'Sales Order',timesheet:'Timesheet',workorder:'Work Order',expense:'Expense Report',billofsale:'Bill of Sale',donation:'Donation Receipt'},
    prefix:{invoice:'INV',quote:'EST',delivery:'PS',po:'PO',receipt:'RCT',credit:'CN',proforma:'PF',salesorder:'SO',timesheet:'TS',workorder:'WO',expense:'EXP',billofsale:'BOS',donation:'DR'} }
};
var CA_PROV=[['ON','Ontario (HST 13%)',[['HST',13]]],['BC','British Columbia (GST 5% + PST 7%)',[['GST',5],['PST',7]]],
  ['AB','Alberta (GST 5%)',[['GST',5]]],['QC','Quebec (GST 5% + QST 9.975%)',[['GST',5],['QST',9.975]]],
  ['MB','Manitoba (GST 5% + PST 7%)',[['GST',5],['PST',7]]],['SK','Saskatchewan (GST 5% + PST 6%)',[['GST',5],['PST',6]]],
  ['NS','Nova Scotia (HST 15%)',[['HST',15]]],['NB','New Brunswick (HST 15%)',[['HST',15]]],
  ['NL','Newfoundland & Labrador (HST 15%)',[['HST',15]]],['PE','Prince Edward Island (HST 15%)',[['HST',15]]],
  ['NT','Northwest Territories (GST 5%)',[['GST',5]]],['NU','Nunavut (GST 5%)',[['GST',5]]],['YT','Yukon (GST 5%)',[['GST',5]]]];

/* Document kinds */
var KINDS={
  invoice:{ due:true, terms:true, bank:true, prices:true, amountLabel:'Amount Due', totalLabel:'Total', dateLabel:'Invoice date', numLabel:'Invoice #', partyLabel:'Bill To' },
  quote:{ valid:true, prices:true, amountLabel:'Estimated Total', totalLabel:'Total', dateLabel:'Date', numLabel:'Estimate #', partyLabel:'Prepared For', accept:true },
  delivery:{ prices:false, shipTo:true, deliveryDate:true, amountLabel:'', totalLabel:'', dateLabel:'Date', numLabel:'Packing Slip #', partyLabel:'Bill To', sign:true },
  po:{ prices:true, shipTo:true, deliveryDate:true, amountLabel:'Order Total', totalLabel:'Total', dateLabel:'Order date', numLabel:'PO #', partyLabel:'Vendor', poSign:true },
  receipt:{ prices:true, paid:true, method:true, amountLabel:'Amount Paid', totalLabel:'Total', dateLabel:'Receipt date', numLabel:'Receipt #', partyLabel:'Received From' },
  credit:{ prices:true, credit:true, ref:true, amountLabel:'Total Credit', totalLabel:'Total Credit', dateLabel:'Credit date', numLabel:'Credit Note #', partyLabel:'Bill To' },
  proforma:{ prices:true, valid:true, bank:true, proforma:true, amountLabel:'Total', totalLabel:'Total', dateLabel:'Issue date', numLabel:'Pro Forma #', partyLabel:'Bill To' },
  salesorder:{ prices:true, shipTo:true, deliveryDate:true, confirm:true, amountLabel:'Order Total', totalLabel:'Total', dateLabel:'Order date', numLabel:'Sales Order #', partyLabel:'Customer' },
  timesheet:{ prices:true, notax:true, hoursTotal:true, colQty:'Hours', colPrice:'Rate', amountLabel:'Total', totalLabel:'Total', dateLabel:'Week ending', numLabel:'Timesheet #', partyLabel:'Bill To' },
  workorder:{ prices:true, shipTo:true, deliveryDate:true, woSign:true, amountLabel:'Total', totalLabel:'Total', dateLabel:'Date', numLabel:'Work Order #', partyLabel:'Customer' },
  expense:{ amountOnly:true, notax:true, amountLabel:'Total Reimbursement', totalLabel:'Total', dateLabel:'Period ending', numLabel:'Report #', partyLabel:'Submitted to' },
  billofsale:{ prices:true, notax:true, dualSign:true, bos:true, amountLabel:'Sale Price', totalLabel:'Total', dateLabel:'Date of sale', numLabel:'Bill of Sale #', partyLabel:'Buyer' },
  donation:{ amountOnly:true, notax:true, donation:true, donSign:true, amountLabel:'Total Donation', totalLabel:'Total', dateLabel:'Date received', numLabel:'Receipt #', partyLabel:'Donor' }
};
/* Region-specific document labels */
function kindLabels(kind,region){ var R=REGIONS[region]; var K=Object.assign({},KINDS[kind]); K.title=R.titles[kind];
  if(kind==='quote'){ K.numLabel=(R.titles.quote==='Estimate'?'Estimate #':'Quote #'); K.partyLabel='Prepared For'; }
  if(kind==='delivery'){ K.numLabel=R.titles.delivery+' #'; }
  if(kind==='credit'){ K.numLabel=R.titles.credit+' #'; }
  return K; }

/* ================= State & helpers ================= */
var root=document.getElementById('toolwrap');
var kind=(root&&root.getAttribute('data-kind'))||'invoice';
var region='us';
var rowsEl=document.getElementById('rows');
var $=function(id){ return document.getElementById(id); };
function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]; }); }
function r2(n){ return Math.round((Number(n)||0)*100)/100; }
function money(n,withCode){ var R=REGIONS[region]; n=r2(n); var s=Math.abs(n).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}); return (n<0?'-':'')+R.sym+s+(withCode?' '+R.cur:''); }
function fmtDate(iso){ if(!iso)return ''; var m=String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/); if(!m)return iso; var R=REGIONS[region]; var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  if(R.date==='mdy') return MON[+m[2]-1]+' '+(+m[3])+', '+m[1];
  if(R.date==='dmy') return (+m[3])+' '+MON[+m[2]-1]+' '+m[1];
  return m[1]+'-'+m[2]+'-'+m[3]; }
function todayISO(){ return new Date().toISOString().slice(0,10); }
function plusDays(n){ return new Date(Date.now()+864e5*n).toISOString().slice(0,10); }
function guessRegion(){ try{ var s=localStorage.getItem('free_en_region'); if(s&&REGIONS[s])return s; }catch(e){}
  var l=(navigator.language||'').toLowerCase(); if(l==='en-gb'||/-gb$|-ie$/.test(l))return 'uk'; if(/-au$|-nz$/.test(l))return 'au'; if(/-ca$/.test(l))return 'ca'; return 'us'; }
function pad4(n){ return ('000'+n).slice(-4); }
function nextDocNo(){ try{ var seq=parseInt(localStorage.getItem('free_en_seq')||'0',10)||0; return REGIONS[region].prefix[kind]+'-'+pad4(seq+1); }catch(e){ return 'INV-0001'; } }
function bumpDocNo(){ try{ var seq=parseInt(localStorage.getItem('free_en_seq')||'0',10)||0; localStorage.setItem('free_en_seq',String(seq+1)); }catch(e){} }
function toast(msg){ var t=$('__toast'); if(!t){ t=document.createElement('div'); t.id='__toast'; t.style.cssText='position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(20px);background:#13263b;color:#fff;font-size:13.5px;font-weight:700;padding:11px 18px;border-radius:12px;box-shadow:0 12px 30px -10px rgba(19,38,59,.6);z-index:9999;opacity:0;transition:.25s;max-width:90vw;text-align:center'; document.body.appendChild(t);} t.textContent=msg; requestAnimationFrame(function(){ t.style.opacity='1'; t.style.transform='translateX(-50%) translateY(0)'; }); clearTimeout(t.__h); t.__h=setTimeout(function(){ t.style.opacity='0'; t.style.transform='translateX(-50%) translateY(20px)'; },2600); }

/* ================= Line items ================= */
function taxOptionsHtml(sel){ var R=REGIONS[region]; return R.taxOpts.map(function(o){ return '<option value="'+o[0]+'"'+(String(sel)===o[0]?' selected':'')+'>'+o[1]+'</option>'; }).join(''); }
function defaultTax(){ var R=REGIONS[region]; return R.taxOpts[0][0]; }
function rowHtml(it){ it=it||{}; var tx=(it.tax!=null&&it.tax!=='')?it.tax:defaultTax();
  return '<div class="rw">'
  +'<input class="i-name" value="'+esc(it.name||'')+'" placeholder="Description of item or service">'
  +'<input class="i-qty n" inputmode="decimal" value="'+(it.qty!=null?it.qty:1)+'">'
  +'<input class="i-price n" inputmode="decimal" value="'+(it.unit_price!=null?it.unit_price:'')+'" placeholder="0.00">'
  +'<select class="i-tax">'+taxOptionsHtml(tx)+'</select>'
  +'<button class="del" type="button" aria-label="Remove line">×</button></div>'; }
function addRow(it){ rowsEl.insertAdjacentHTML('beforeend',rowHtml(it)); }
function collect(){ return Array.prototype.slice.call(rowsEl.querySelectorAll('.rw')).map(function(rw){ return {
  name:rw.querySelector('.i-name').value, qty:parseFloat(rw.querySelector('.i-qty').value)||0,
  unit_price:parseFloat(String(rw.querySelector('.i-price').value).replace(/[^0-9.\-]/g,''))||0,
  tax:rw.querySelector('.i-tax').value }; }); }
function liveItems(){ return collect().filter(function(it){ return it.name||it.unit_price; }); }
/* Re-render tax selects when the region changes (keeps other fields) */
function refreshTaxSelects(){ Array.prototype.forEach.call(rowsEl.querySelectorAll('.i-tax'),function(s){ var cur=s.value; var R=REGIONS[region]; var ok=R.taxOpts.some(function(o){return o[0]===cur;}); s.innerHTML=taxOptionsHtml(ok?cur:defaultTax()); }); }

/* ================= Tax calculation ================= */
/* returns {subtotal, taxLines:[{name,rate,base,tax}], tax, total} */
function calc(items){
  var R=REGIONS[region], subtotal=0, groups={}, order=[];
  (items||[]).forEach(function(it){
    var amt=r2((Number(it.qty)||0)*(Number(it.unit_price)||0)); subtotal=r2(subtotal+amt);
    if(KINDS[kind]&&KINDS[kind].notax) return;
    var rates=[];
    if(it.tax==='none') rates=[];
    else if(R.mode==='rate'){ var rt=parseFloat(($('tax-rate')&&$('tax-rate').value)||R.defaultRate)||0; if(rt>0) rates=[[R.taxName,rt]]; }
    else if(R.mode==='fixed'){ var f=parseFloat(it.tax); if(f>0) rates=[[R.taxName,f]]; }
    else if(R.mode==='province'){ var pv=($('ca-prov')&&$('ca-prov').value)||'ON'; var p=CA_PROV.filter(function(x){return x[0]===pv;})[0]; rates=p?p[2]:[]; }
    rates.forEach(function(rr){ var key=rr[0]+'@'+rr[1]; if(!groups[key]){ groups[key]={name:rr[0],rate:rr[1],base:0,tax:0}; order.push(key); } groups[key].base=r2(groups[key].base+amt); });
  });
  var taxLines=order.map(function(k){ var g=groups[k]; g.tax=r2(g.base*g.rate/100); return g; });
  var tax=taxLines.reduce(function(a,g){return r2(a+g.tax);},0);
  return { subtotal:subtotal, taxLines:taxLines, tax:tax, total:r2(subtotal+tax) };
}

/* ================= Persistence ================= */
var CO=['co-name','co-taxid','co-email','co-phone','co-addr','co-bank'];
function saveCo(){ try{ var o={}; CO.forEach(function(id){ if($(id)) o[id]=$(id).value; }); localStorage.setItem('free_en_company',JSON.stringify(o)); }catch(e){} }
function loadCo(){ try{ var s=JSON.parse(localStorage.getItem('free_en_company')||'{}'); CO.forEach(function(id){ if(s[id]!=null&&$(id)) $(id).value=s[id]; }); var d=$('co-details'); if(d) d.open=!s['co-name']; }catch(e){} }
window.__logo=''; try{ window.__logo=localStorage.getItem('free_en_logo')||''; }catch(e){}
function draftKey(){ return 'free_en_draft_'+kind; }
var _dsT=null;
var DRAFT_IDS=['cl-name','cl-addr','cl-email','doc-no','ref-no','issue','due','terms','ship-to','method','notes','terms-text','tax-rate','ca-prov'];
function saveDraft(){ clearTimeout(_dsT); _dsT=setTimeout(function(){ try{ var o={items:collect()}; DRAFT_IDS.forEach(function(id){ if($(id)) o[id]=$(id).value; }); localStorage.setItem(draftKey(),JSON.stringify(o)); }catch(e){} },400); }
function loadDraft(){ try{ var o=JSON.parse(localStorage.getItem(draftKey())||'null'); if(!o) return false; DRAFT_IDS.forEach(function(id){ if(o[id]!=null&&$(id)) $(id).value=o[id]; }); if(o.items&&o.items.length){ rowsEl.innerHTML=''; o.items.forEach(addRow); } return true; }catch(e){ return false; } }
function clearDraft(){ try{ localStorage.removeItem(draftKey()); }catch(e){} }

/* ================= Logo ================= */
function _downscale(durl,maxDim,cb){ var im=new Image(); im.onload=function(){ var w=im.width,h=im.height,sc=Math.min(1,maxDim/Math.max(w,h)); var cw=Math.max(1,Math.round(w*sc)),ch=Math.max(1,Math.round(h*sc)); var c=document.createElement('canvas'); c.width=cw;c.height=ch; c.getContext('2d').drawImage(im,0,0,cw,ch); try{cb(c.toDataURL('image/png'));}catch(e){cb('');} }; im.onerror=function(){cb('');}; im.src=durl; }
function renderLogoRow(){ var row=$('imgrow'); if(!row)return; row.innerHTML=window.__logo?'<span style="display:inline-flex;align-items:center;gap:6px;font-size:11.5px;color:#5a6b7d"><img src="'+window.__logo+'" style="max-height:30px;max-width:110px;border:1px solid #e2eaf4;border-radius:4px">Logo<button type="button" id="logodel" style="border:none;background:none;color:#c0392b;cursor:pointer;font-size:16px;line-height:1">×</button></span>':''; var b=$('co-logo-btn'); if(b) b.innerHTML=window.__logo?'Change image&hellip;':'Choose image&hellip;'; }
function setupLogo(){ var el=$('co-logo'); if(!el)return; el.addEventListener('change',function(){ var fl=el.files&&el.files[0]; if(!fl)return; var r=new FileReader(); r.onload=function(){ _downscale(r.result,480,function(d){ if(!d)return; window.__logo=d; try{localStorage.setItem('free_en_logo',d);}catch(e){} renderLogoRow(); schedulePv(); }); }; r.readAsDataURL(fl); });
  var row=$('imgrow'); if(row) row.addEventListener('click',function(e){ if(e.target.id!=='logodel')return; window.__logo=''; try{localStorage.removeItem('free_en_logo');}catch(e){} el.value=''; renderLogoRow(); schedulePv(); }); renderLogoRow(); }

/* ================= Data object ================= */
function v(id){ var el=$(id); return el?el.value:''; }
function buildDoc(){ return {
  kind:kind, region:region, theme:window.__theme||'mono',
  doc_no:v('doc-no'), ref_no:v('ref-no'), issue:v('issue'), due:v('due'), terms:v('terms'), method:v('method'),
  client:{name:v('cl-name'), addr:v('cl-addr'), email:v('cl-email')}, ship_to:v('ship-to'),
  co:{name:v('co-name'), taxid:v('co-taxid'), email:v('co-email'), phone:v('co-phone'), addr:v('co-addr'), bank:v('co-bank'), logo:window.__logo||''},
  notes:v('notes'), terms_text:v('terms-text'), tax_rate:v('tax-rate'), prov:v('ca-prov'),
  items:liveItems() }; }

/* ================= UI: region & kind ================= */
var TERMS=[['receipt','Due on receipt',0],['7','Net 7',7],['15','Net 15',15],['30','Net 30',30],['45','Net 45',45],['60','Net 60',60]];
function applyRegion(r,keepDue){
  region=REGIONS[r]?r:'us'; var R=REGIONS[region];
  try{ localStorage.setItem('free_en_region',region); }catch(e){}
  Array.prototype.forEach.call(document.querySelectorAll('#regseg button'),function(b){ b.classList.toggle('on',b.getAttribute('data-region')===region); });
  var lb=$('co-taxid-lb'); if(lb) lb.textContent=R.taxIdLabel; if($('co-taxid')) $('co-taxid').placeholder=R.taxIdPh;
  if($('co-addr')) $('co-addr').placeholder=R.addrPh; if($('co-bank')) $('co-bank').placeholder=R.bankPh;
  if($('cl-addr')) $('cl-addr').placeholder=R.addrPh;
  var rw=$('taxrate-wrap'); if(rw) rw.style.display=(R.mode==='rate')?'':'none';
  var pw=$('prov-wrap'); if(pw) pw.style.display=(R.mode==='province')?'':'none';
  var th=$('th-tax'); if(th) th.textContent=(R.mode==='rate'||R.mode==='province')?'Tax':R.taxName;
  var cl=$('cur-lb'); if(cl) cl.textContent=R.cur;
  refreshTaxSelects();
  var dn=$('doc-no'); if(dn&&(!dn.value||/^[A-Z]+-\d{4}$/.test(dn.value))) dn.value=nextDocNo();
  applyKind(kind,true);
}
function applyKind(k,silent){
  kind=KINDS[k]?k:'invoice'; var K=kindLabels(kind,region), R=REGIONS[region];
  Array.prototype.forEach.call(document.querySelectorAll('#seg button'),function(b){ b.classList.toggle('on',b.getAttribute('data-kind')===kind); });
  function show(id,on){ var el=$(id); if(el) el.style.display=on?'':'none'; }
  show('due-wrap',!!(K.due||K.valid||K.deliveryDate)); show('terms-wrap',!!K.terms);
  var dl=$('due-lb'); if(dl) dl.textContent=K.due?'Due date':(K.valid?'Valid until':(kind==='workorder'?'Scheduled date':((kind==='po'||kind==='salesorder')?'Delivery date':'Ship date')));
  show('method-wrap',!!K.method); show('shipto-wrap',!!K.shipTo); show('bank-wrap',kind==='invoice'||kind==='proforma');
  var nl=$('num-lb'); if(nl) nl.textContent=K.numLabel; var il=$('issue-lb'); if(il) il.textContent=K.dateLabel;
  var pl=$('party-lb'); if(pl) pl.textContent=K.partyLabel+' (name)';
  var h=$('pv-kind'); if(h) h.textContent=K.title;
  var mk=$('make'); if(mk) mk.lastChild.nodeValue=' Download '+K.title+' PDF (free)';
  if($('due')&&K.due&&!$('due').value) $('due').value=plusDays(30);
  if($('due')&&K.valid&&!$('due').value) $('due').value=plusDays(30);
  var amtOnly=!!K.amountOnly, noTaxUI=!!(K.notax||amtOnly);
  var trw=$('taxrate-wrap'); if(trw) trw.style.display=(!noTaxUI&&R.mode==='rate')?'':'none';
  var pvw=$('prov-wrap'); if(pvw) pvw.style.display=(!noTaxUI&&R.mode==='province')?'':'none';
  var thq=$('th-qty'); if(thq) thq.textContent=(K.colQty||'Qty');
  var thp=$('th-price'); if(thp) thp.innerHTML=esc(amtOnly?'Amount':(K.colPrice||'Unit price'))+' ('+esc(R.cur)+')';
  var itemsBox=rowsEl.closest('.items');
  if(itemsBox){ itemsBox.classList.toggle('noprice',!K.prices&&!amtOnly); itemsBox.classList.toggle('amountonly',amtOnly); itemsBox.classList.toggle('notax',!!K.notax&&!amtOnly); }
  if(!silent) schedulePv();
}
function setupTermsSelect(){ var s=$('terms'); if(!s)return; s.innerHTML=TERMS.map(function(t){return '<option value="'+t[0]+'"'+(t[0]==='30'?' selected':'')+'>'+t[1]+'</option>';}).join('');
  s.addEventListener('change',function(){ var t=TERMS.filter(function(x){return x[0]===s.value;})[0]; if(t&&$('issue')&&$('due')){ var base=$('issue').value?new Date($('issue').value):new Date(); $('due').value=new Date(base.getTime()+864e5*t[2]).toISOString().slice(0,10); } }); }
function setupProv(){ var s=$('ca-prov'); if(!s)return; s.innerHTML=CA_PROV.map(function(p){return '<option value="'+p[0]+'">'+p[1]+'</option>';}).join(''); }
function convertTo(k){ applyKind(k); var dn=$('doc-no'); if(dn) dn.value=nextDocNo(); if($('issue')) $('issue').value=todayISO(); if(KINDS[k].due||KINDS[k].valid){ if($('due')) $('due').value=plusDays(30); } window.__savedId=null; if(typeof renderSave==='function') renderSave(); saveDraft(); schedulePv(); toast('Converted to '+kindLabels(k,region).title+' — same details, new number'); try{ document.querySelector('.card.right').scrollIntoView({behavior:'smooth',block:'start'}); }catch(e){} renderConvertBar(); }
function renderConvertBar(){ var bar=$('convbar'); if(!bar)return; var ks=['invoice','quote','delivery','po','receipt','credit','proforma','salesorder','timesheet','workorder','expense','billofsale','donation'].filter(function(x){return x!==kind;});
  bar.innerHTML='<div class="cv-lb">✓ Same details, <b>different document</b> — one click</div><div class="cv-bs">'+ks.map(function(x){return '<button type="button" data-to="'+x+'">'+kindLabels(x,region).title+'</button>';}).join('')+'</div>'; }

/* ================= PDF (pdf-lib, Helvetica — no font download needed) ================= */
var _libP=null;
function loadScript(src){ return new Promise(function(res,rej){ var s=document.createElement('script'); s.src=src; s.onload=res; s.onerror=function(){rej(new Error('load fail '+src));}; document.head.appendChild(s); }); }
function ensureLib(){ if(_libP)return _libP; _libP=(async function(){ if(!window.PDFLib) await loadScript('https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js'); })(); return _libP; }
var THEME_DEFS={ mono:[0.12,0.12,0.13], blue:[0.09,0.40,0.90], red:[0.80,0.16,0.18], green:[0.09,0.50,0.33], purple:[0.42,0.22,0.68], orange:[0.88,0.46,0.08] };
/* WinAnsi-safe text (Helvetica cannot encode CJK etc.) */
var OK_EXTRA='\u2018\u2019\u201c\u201d\u2013\u2014\u2026\u2022\u20ac\u2122\u00a0';
function clean(s){ s=String(s==null?'':s); var o=''; for(var i=0;i<s.length;i++){ var c=s.charCodeAt(i); var ch=s[i]; if(c<0x20){ if(ch==='\n'||ch==='\t') o+=' '; continue; } if(c<=0xff||OK_EXTRA.indexOf(ch)>=0) o+=ch; else o+='?'; } return o; }
function lines(s){ return String(s==null?'':s).split(/\r?\n/).map(function(x){return x.trim();}).filter(Boolean); }

async function buildPdf(D){
  await ensureLib();
  var P=window.PDFLib, rgb=P.rgb, R=REGIONS[D.region], K=kindLabels(D.kind,D.region), c=calc(D.items);
  var amountOnly=!!K.amountOnly, hasAmount=!!(K.prices||amountOnly);
  var pdf=await P.PDFDocument.create();
  var font=await pdf.embedFont(P.StandardFonts.Helvetica), bold=await pdf.embedFont(P.StandardFonts.HelveticaBold);
  var W=R.paper==='letter'?612:595.28, H=R.paper==='letter'?792:841.89, M=46;
  var page=pdf.addPage([W,H]);
  var b=THEME_DEFS[D.theme]||THEME_DEFS.mono; function mw(p){return rgb(b[0]*p+(1-p),b[1]*p+(1-p),b[2]*p+(1-p));} function dk(p){return rgb(b[0]*p,b[1]*p,b[2]*p);}
  var ink=rgb(0.1,0.1,0.12), mut=rgb(0.42,0.44,0.48), line=rgb(0.78,0.8,0.83), ac=dk(0.85), head=mw(0.12), band=mw(0.08), zebra=mw(0.04);
  var tw=function(s,sz,f){ return (f||font).widthOfTextAtSize(clean(s),sz); };
  var dr=function(s,x,y,sz,col,f){ page.drawText(clean(s),{x:x,y:y,size:sz,font:f||font,color:col||ink}); };
  var drR=function(s,xr,y,sz,col,f){ s=clean(s); page.drawText(s,{x:xr-(f||font).widthOfTextAtSize(s,sz),y:y,size:sz,font:f||font,color:col||ink}); };
  var ell=function(s,sz,max,f){ s=clean(s); if(tw(s,sz,f)<=max)return s; while(s.length>1&&tw(s+'…',sz,f)>max) s=s.slice(0,-1); return s+'…'; };
  var hline=function(y,th,col){ page.drawLine({start:{x:M,y:y},end:{x:W-M,y:y},thickness:th||0.6,color:col||line}); };
  var mny=function(n){ return clean(money.call(null,n)); };
  var y=H-M;

  /* ---- Header: logo / business (left), title + meta (right) ---- */
  var title=K.title.toUpperCase();
  if(D.kind==='invoice'&&D.region==='au'&&!(D.co.taxid&&c.tax>0)) title='INVOICE';
  drR(title,W-M,y-22,24,ac,bold);
  var my=y-40;
  var meta=[[K.numLabel,D.doc_no||'—'],[K.dateLabel,fmtDate(D.issue)]];
  if(K.due) meta.push(['Due date',fmtDate(D.due)||'—']);
  if(K.valid) meta.push(['Valid until',fmtDate(D.due)||'—']);
  if(K.deliveryDate&&D.due) meta.push([D.kind==='workorder'?'Scheduled date':((D.kind==='po'||D.kind==='salesorder')?'Delivery date':'Ship date'),fmtDate(D.due)]);
  if(D.ref_no) meta.push([(D.kind==='po')?'Reference':(D.kind==='credit')?'Original invoice #':(D.kind==='salesorder')?'Customer PO #':'PO / Ref. #',D.ref_no]);
  if(K.terms&&D.terms){ var t=TERMS.filter(function(x){return x[0]===D.terms;})[0]; if(t) meta.push(['Terms',t[1]]); }
  if(K.method&&D.method) meta.push(['Payment method',D.method]);
  meta.forEach(function(m){ drR(m[1],W-M,my,9.5,ink); drR(m[0],W-M-tw(m[1],9.5)-6,my,9,mut); my-=13; });
  var ly=y-4, logo=null;
  if(D.co.logo&&D.co.logo.indexOf('data:')===0){ try{ var i=D.co.logo.indexOf(','); var bin=atob(D.co.logo.slice(i+1)); var u=new Uint8Array(bin.length); for(var k2=0;k2<bin.length;k2++)u[k2]=bin.charCodeAt(k2); logo=/png/i.test(D.co.logo.slice(0,i))?await pdf.embedPng(u):await pdf.embedJpg(u); }catch(e){ logo=null; } }
  if(logo){ var sc=Math.min(150/logo.width,44/logo.height); page.drawImage(logo,{x:M,y:ly-44,width:logo.width*sc,height:logo.height*sc}); ly-=52; }
  dr(ell(D.co.name||'Your Business Name',logo?12:16,300,bold),M,ly-(logo?12:16),logo?12:16,ink,bold); ly-=(logo?15:21);
  lines(D.co.addr).forEach(function(l){ dr(ell(l,8.5,300),M,ly-9,8.5,mut); ly-=11; });
  var contact=[D.co.email,D.co.phone].filter(Boolean).join('  ·  '); if(contact){ dr(ell(contact,8.5,300),M,ly-9,8.5,mut); ly-=11; }
  if(D.co.taxid){ dr(ell(R.taxIdLabel.replace(/ \(.*\)$/,'')+': '+D.co.taxid,8.5,300),M,ly-9,8.5,ac,bold); ly-=11; }
  y=Math.min(ly,my)-14; hline(y,1.4,ac); y-=22;

  /* ---- Parties ---- */
  var cols=K.shipTo&&(D.ship_to||D.kind==='delivery')?2:1; var cw=(W-2*M)/(cols===2?2:1);
  function party(x,label,name,addr,email){ var yy=y; dr(label.toUpperCase(),x,yy,8,mut,bold); yy-=14; if(name!=null){ dr(ell(name||'—',11,cw-16,bold),x,yy,11,ink,bold); yy-=14; } lines(addr).forEach(function(l){ dr(ell(l,9,cw-16),x,yy,9,ink); yy-=12; }); if(email){ dr(ell(email,9,cw-16),x,yy,9,mut); yy-=12; } return yy; }
  var y1=party(M,K.partyLabel,D.client.name,D.client.addr,D.client.email), y2=y1;
  if(cols===2) y2=party(M+cw,'Ship To',(D.ship_to?null:D.client.name),D.ship_to||D.client.addr,'');
  y=Math.min(y1,y2)-14;

  /* ---- Amount band ---- */
  if(hasAmount&&K.amountLabel){ page.drawRectangle({x:M,y:y-36,width:W-2*M,height:36,color:band}); dr(K.amountLabel,M+12,y-23,10.5,ink,bold); drR(mny(c.total)+' '+R.cur,W-M-12,y-24,16,ac,bold); y-=52; }
  else y-=6;

  /* ---- Table ---- */
  var showTax=K.prices&&!K.notax&&!amountOnly, showPrice=K.prices&&!amountOnly;
  var qtyHead=(K.colQty||'Qty').toUpperCase(), priceHead=(K.colPrice||'Unit price').toUpperCase();
  // right-edge anchors for each numeric column
  var xAmt=W-M-6;
  var xTax=showTax?xAmt-78:xAmt;
  var xPrice=showPrice?xTax-64:xAmt;
  var xQty=amountOnly?0:(showPrice?xPrice-74:(hasAmount?xAmt-10:W-M-10));
  var descRight=amountOnly?xAmt-70:(showPrice?xQty-48:(hasAmount?xAmt-40:xQty-40));
  var descMax=descRight-(M+8);
  var taxHead=(R.mode==='fixed')?R.taxName.toUpperCase():'TAX';
  page.drawRectangle({x:M,y:y-20,width:W-2*M,height:20,color:head});
  dr('DESCRIPTION',M+8,y-14,8,ink,bold);
  if(!amountOnly) drR(qtyHead,xQty,y-14,8,ink,bold);
  if(showPrice) drR(priceHead,xPrice,y-14,8,ink,bold);
  if(showTax) drR(taxHead,xTax,y-14,8,ink,bold);
  if(hasAmount) drR('AMOUNT',xAmt,y-14,8,ink,bold);
  y-=20;
  var items=D.items, maxRows=Math.max(1,Math.floor((y-(M+170))/19)), ovf=0, draw=items;
  if(items.length>maxRows){ draw=items.slice(0,maxRows-1); ovf=items.length-draw.length; }
  function taxLabel(it){ if(it.tax==='none') return 'Exempt'; if(R.mode==='fixed'){ var o=R.taxOpts.filter(function(x){return x[0]===it.tax;})[0]; return o?o[1].replace(/^(VAT|GST) /,''):''; } return 'Taxable'; }
  draw.forEach(function(it,i){ var amt=r2((it.qty||0)*(it.unit_price||0)); if(i%2===1) page.drawRectangle({x:M,y:y-19,width:W-2*M,height:19,color:zebra});
    dr(ell(it.name,9,descMax),M+8,y-13,9,ink);
    if(!amountOnly) drR(String(it.qty),xQty,y-13,9);
    if(showPrice) drR(mny(it.unit_price),xPrice,y-13,9);
    if(showTax) drR(ell(taxLabel(it),8,xAmt-xTax-6),xTax,y-13,8,mut);
    if(hasAmount) drR(mny(amt),xAmt,y-13,9);
    hline(y-19,0.4); y-=19; });
  if(ovf>0){ dr('+ '+ovf+' more line'+(ovf>1?'s':''),M+8,y-13,8.5,mut); hline(y-19,0.4); y-=19; }
  y-=18;

  /* ---- Totals ---- */
  if(hasAmount){ var sx=W-M-230;
    var row=function(l,vv,col,sz,f){ dr(l,sx,y,sz||9.5,col||ink,f); drR(vv,W-M-6,y,sz||9.5,col||ink,f); y-=15; };
    if(!K.notax){ row('Subtotal',mny(c.subtotal));
      c.taxLines.forEach(function(t){ row(t.name+' ('+t.rate+'%)',mny(t.tax),mut); });
      if(!c.taxLines.length&&D.region!=='us') row(R.taxName,mny(0),mut); }
    if(K.hoursTotal){ var th=0; (D.items||[]).forEach(function(it){ th=r2(th+(Number(it.qty)||0)); }); row('Total hours',String(th),mut); }
    y-=3; page.drawLine({start:{x:sx,y:y+7},end:{x:W-M,y:y+7},thickness:1,color:ac}); y-=12;
    row(K.totalLabel+' ('+R.cur+')',mny(c.total),ac,12,bold);
    if(K.paid){ y-=2; row('Amount paid',mny(c.total),ink,9.5); row('Balance due',mny(0),mut,9.5); }
    y-=10; }

  /* ---- Bottom boxes ---- */
  var boxes=[];
  if(D.kind==='proforma') boxes.push(['Pro forma invoice',['For information only - this is not a tax invoice or VAT invoice, and not a demand for payment.','It confirms the price and terms before the goods or services are supplied; a final invoice follows.']]);
  if(D.kind==='credit') boxes.push(['About this credit note',['This credit note cancels or reduces the amount of the referenced invoice'+(D.ref_no?' ('+D.ref_no+')':'')+'.','Apply it against that invoice or a future one, or refund the amount as agreed.']]);
  if(D.kind==='billofsale') boxes.push(['Terms of sale',['The seller sells the item(s) above to the buyer for the total shown, "as-is" unless noted.','The seller certifies they are the lawful owner with the right to sell, free of undisclosed liens.']]);
  if(D.kind==='donation'){ var ds=['Thank you for your generous contribution.']; ds.push('No goods or services were provided in exchange for this donation'+(D.region==='us'?', which may be tax-deductible to the extent allowed by law.':'.')); if(D.co.taxid) ds.push((D.region==='us'?'Tax-exempt ID (EIN): ':'Charity / tax reg. no.: ')+D.co.taxid); ds.push('Please retain this receipt for your records.'); boxes.push(['Tax receipt',ds]); }
  if(K.bank&&D.co.bank&&(D.kind==='invoice'||D.kind==='proforma')) boxes.push([D.kind==='proforma'?'How to pay in advance':'Payment details',lines(D.co.bank)]);
  if(D.notes) boxes.push(['Notes',lines(D.notes)]);
  if(D.terms_text) boxes.push([D.kind==='quote'?'Terms':'Terms & conditions',lines(D.terms_text)]);
  boxes.forEach(function(bx){ var n=Math.min(bx[1].length,5), h=24+n*12; if(y-h<M+40) return; page.drawRectangle({x:M,y:y-h,width:W-2*M,height:h,borderColor:line,borderWidth:0.7,color:rgb(0.985,0.985,0.985)}); dr(bx[0],M+10,y-15,9,ink,bold); var yy=y-29; bx[1].slice(0,n).forEach(function(l){ dr(ell(l,8.8,W-2*M-24),M+10,yy,8.8,mut); yy-=12; }); y-=h+10; });
  if(K.accept&&y>M+60){ dr('Accepted by: ______________________________    Date: ______________',M,y-16,9.5,ink); dr('Signing confirms acceptance of this '+K.title.toLowerCase()+' and its terms.',M,y-30,8,mut); y-=40; }
  if((K.sign||K.poSign)&&y>M+60){ dr((K.poSign?'Authorized by':'Received by')+': ______________________________    Date: ______________',M,y-16,9.5,ink); y-=30; }
  if(K.dualSign&&y>M+80){ dr('Seller: ______________________________    Date: ______________',M,y-16,9.5,ink); dr('Buyer:  ______________________________    Date: ______________',M,y-34,9.5,ink); y-=46; }
  if(K.woSign&&y>M+80){ dr('Authorized by (customer): ____________________    Date: __________',M,y-16,9.5,ink); dr('Work completed by: ___________________________    Date: __________',M,y-34,9.5,ink); y-=46; }
  if(K.donSign&&y>M+50){ dr('Authorized signature: ______________________________',M,y-16,9.5,ink); y-=28; }
  if(D.kind==='expense'&&y>M+50){ dr('Approved by: ______________________________    Date: ______________',M,y-16,9.5,ink); y-=30; }
  if(K.paid){ page.drawRectangle({x:W-M-96,y:M+44,width:96,height:36,borderColor:ac,borderWidth:2,color:mw(0.06)}); drR('PAID',W-M-14,M+55,20,ac,bold); }
  /* footer */
  var FOOT={quote:'Thank you for the opportunity.',receipt:'Thank you for your payment.',credit:'Credit note - this is not a request for payment.',proforma:'Pro forma invoice - not a tax invoice. Please do not pay from this document unless agreed in advance.',salesorder:'Thank you for your order - we will confirm dispatch separately.',timesheet:'Hours billable at the rates shown. Approve and convert to an invoice when ready.',workorder:'Please sign to confirm the work is authorized and, on completion, that it was carried out.',expense:'Please attach a receipt for each expense listed above.',billofsale:'This bill of sale records the transfer of ownership described above.',donation:'Thank you for your support.'};
  var foot=FOOT[D.kind]||'Thank you for your business.';
  if(D.region==='au'&&D.kind==='invoice'&&c.tax>0) foot+='   Total price includes GST.';
  dr(foot,M,M-6,8.5,mut);
  return await pdf.save();
}
window.__buildPdf=buildPdf;

/* ================= Live preview (pdf.js) ================= */
var _pdfjsP=null;
function ensurePdfjs(){ if(_pdfjsP)return _pdfjsP; _pdfjsP=(async function(){ if(!window.pdfjsLib) await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js'); window.pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'; })(); return _pdfjsP; }
var _pvT=null,_pvRun=null,_pvAgain=false,_pvSeq=0;
function schedulePv(){ clearTimeout(_pvT); _pvT=setTimeout(runPv,650); }
async function runPv(){
  var host=$('livepv'); if(!host)return; if(_pvRun){ _pvAgain=true; return; }
  var my=++_pvSeq, st=host.querySelector('.livepv-st'), pagesEl=host.querySelector('.livepv-pages'); if(st) st.style.opacity='1';
  _pvRun=(async function(){
    var bytes=await buildPdf(buildDoc()); await ensurePdfjs();
    var doc=await window.pdfjsLib.getDocument({data:bytes}).promise;
    var cw=Math.max(200,pagesEl.clientWidth||host.clientWidth||360), dpr=Math.min(window.devicePixelRatio||1,2), frag=document.createDocumentFragment();
    var n=Math.min(doc.numPages,2);
    for(var i=1;i<=n;i++){ var pg=await doc.getPage(i); var vp0=pg.getViewport({scale:1}); var vp=pg.getViewport({scale:(cw/vp0.width)*dpr}); var cv=document.createElement('canvas'); cv.width=Math.floor(vp.width); cv.height=Math.floor(vp.height); cv.className='livepv-page'; var cx=cv.getContext('2d'); cx.fillStyle='#fff'; cx.fillRect(0,0,cv.width,cv.height); await pg.render({canvasContext:cx,viewport:vp,intent:'print'}).promise; frag.appendChild(cv); }
    if(my===_pvSeq){ pagesEl.innerHTML=''; pagesEl.appendChild(frag); }
  })();
  try{ await _pvRun; if(st) st.textContent='Updating preview…'; }catch(e){ if(st) st.textContent='Preview unavailable'; console.error(e); }
  finally{ _pvRun=null; if(st) st.style.opacity='0'; if(_pvAgain){ _pvAgain=false; schedulePv(); } }
}
function setupPreview(){ var host=$('livepv'); if(!host)return; host.innerHTML='<div class="livepv-pages"></div><div class="livepv-st">Building preview…</div>';
  var css=document.createElement('style'); css.textContent='.livepv{position:relative;background:linear-gradient(180deg,#eef2f8,#e4ebf5);border:1px solid #dbe4f0;border-radius:12px;padding:14px;min-height:240px}.livepv-pages{display:flex;flex-direction:column;gap:12px}.livepv-page{display:block;width:100%;height:auto;background:#fff;box-shadow:0 12px 30px -16px rgba(19,38,59,.4);border:1px solid #d5deea}.livepv-st{position:absolute;top:10px;right:12px;font-size:11px;font-weight:700;color:#5a6b7d;background:rgba(255,255,255,.92);border:1px solid #dbe4f0;border-radius:999px;padding:4px 10px;transition:opacity .2s;pointer-events:none}'; document.head.appendChild(css);
  var t; window.addEventListener('resize',function(){ clearTimeout(t); t=setTimeout(schedulePv,300); }); }

/* ================= Download (free: 2 per hour, same limiter as the Japanese tools) ================= */
async function download(){
  var items=liveItems(), m=$('msg'); m.className='msg'; m.textContent='';
  if(!items.length){ m.textContent='Add at least one line item.'; m.className='msg err'; return; }
  if(!v('cl-name')){ m.textContent='Enter the '+kindLabels(kind,region).partyLabel.toLowerCase()+' name.'; m.className='msg err'; return; }
  var btn=$('make'); btn.disabled=true; var old=btn.innerHTML; btn.textContent='Generating…';
  try{
    if(_pvRun){ try{ await _pvRun; }catch(e){} }
    var isPro=!!(window.__me&&window.__me.plan==='pro');
    if(!isPro){
      var chk=await fetch('/api/free/check',{method:'POST'}); var cj=await chk.json();
      if(chk.status===429||!cj.ok){ var lb=$('limitbox'); lb.style.display='block'; lb.innerHTML='The free tool allows <b>2 PDFs per hour</b>. You can create another in about <b>'+(cj.retry_min||60)+' min</b>.<br><a href="/en/pricing" style="color:#1766e6;font-weight:800">Upgrade to PRO for unlimited downloads &rarr;</a>'; btn.disabled=false; btn.innerHTML=old; return; }
    }
    var bytes=await buildPdf(buildDoc());
    var blob=new Blob([bytes],{type:'application/pdf'}), url=URL.createObjectURL(blob), a=document.createElement('a'); a.href=url; a.download=(v('doc-no')||kind)+'.pdf'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function(){URL.revokeObjectURL(url);},4000);
    bumpDocNo(); if($('doc-no')) $('doc-no').value=nextDocNo(); saveDraft();
    var rem=$('remain'); if(rem){ if(isPro) rem.innerHTML='<b>PRO</b> · unlimited downloads'; else rem.innerHTML='<b>'+cj.remaining+'</b> free PDF'+(cj.remaining===1?'':'s')+' left this hour'; }
  }catch(e){ m.textContent='Could not generate the PDF: '+e.message; m.className='msg err'; }
  btn.disabled=false; btn.innerHTML=old;
}
async function refreshRemain(){ if(window.__me&&window.__me.plan==='pro'){ var ep=$('remain'); if(ep) ep.innerHTML='<b>PRO</b> · unlimited downloads'; return; } try{ var r=await fetch('/api/free/check'); var j=await r.json(); var el=$('remain'); if(el) el.innerHTML='<b>'+j.remaining+'</b> free PDF'+(j.remaining===1?'':'s')+' left this hour · no sign-up needed'; }catch(e){} }

/* ================= Share link (data lives in the URL hash only — nothing stored on our server) ================= */
function _b64e(str){ return btoa(unescape(encodeURIComponent(str))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); }
function _b64d(s){ s=String(s).replace(/-/g,'+').replace(/_/g,'/'); while(s.length%4)s+='='; return decodeURIComponent(escape(atob(s))); }
function sharePayload(){ var D=buildDoc(); D.co=Object.assign({},D.co); delete D.co.logo; D.theme=undefined; return D; }
function parseShare(){ try{ var m=(location.hash||'').match(/[#&]s=([^&]+)/); if(!m)return null; var o=JSON.parse(_b64d(decodeURIComponent(m[1]))); return (o&&o.items)?o:null; }catch(e){ return null; } }
function setupShare(){ var box=$('sharebox'); if(!box)return;
  box.innerHTML='<button type="button" id="sharebtn" class="sharebtn">🔗 Create a share link (send a URL instead of attaching a PDF)</button><div id="shareout" class="shareout" style="display:none"><div class="so-lb">Send this link. The recipient can view the document in their browser and download the PDF.</div><div class="so-row"><input id="shareurl" readonly><button type="button" id="sharecopy">Copy</button></div><div class="so-note">Your logo is not included in the link. The content lives only in the URL — nothing is saved on our servers.</div></div>';
  box.addEventListener('click',function(e){ if(e.target.id==='sharebtn'){ if(!liveItems().length){ toast('Add a line item first'); return; } if(!v('cl-name')){ toast('Enter the recipient name first'); return; } var url=location.origin+location.pathname+'#s='+_b64e(JSON.stringify(sharePayload())); $('shareout').style.display='block'; var inp=$('shareurl'); inp.value=url; inp.focus(); inp.select(); }
    else if(e.target.id==='sharecopy'){ var inp2=$('shareurl'); inp2.select(); var ok=false; try{ ok=document.execCommand('copy'); }catch(e2){} if(navigator.clipboard){ navigator.clipboard.writeText(inp2.value).then(function(){toast('Link copied');},function(){toast(ok?'Link copied':'Please copy manually');}); } else toast(ok?'Link copied':'Please copy manually'); } }); }
function enterShareView(P){
  window.__logo='';
  function set(id,val){ var el=$(id); if(el&&val!=null) el.value=val; }
  applyRegion(P.region||'us'); set('co-name',P.co.name); set('co-taxid',P.co.taxid); set('co-email',P.co.email); set('co-phone',P.co.phone); set('co-addr',P.co.addr); set('co-bank',P.co.bank);
  set('cl-name',P.client.name); set('cl-addr',P.client.addr); set('cl-email',P.client.email); set('ship-to',P.ship_to);
  set('doc-no',P.doc_no); set('ref-no',P.ref_no); set('issue',P.issue); set('due',P.due); set('terms',P.terms); set('method',P.method); set('notes',P.notes); set('terms-text',P.terms_text); set('tax-rate',P.tax_rate); set('ca-prov',P.prov);
  rowsEl.innerHTML=''; (P.items||[]).forEach(addRow);
  applyKind(P.kind||'invoice',true);
  document.body.classList.add('shared-view');
  var st=document.createElement('style'); st.textContent='body.shared-view .hero,body.shared-view .art,body.shared-view .faqwrap,body.shared-view .card.pad,body.shared-view #convbar,body.shared-view #sharebox,body.shared-view #savebox,body.shared-view .remain,body.shared-view .limitbox,body.shared-view #clearbtn,body.shared-view #docnav-en{display:none!important}body.shared-view .wrap{grid-template-columns:1fr!important;max-width:720px;margin:0 auto}.paybar{background:linear-gradient(120deg,#0f2f7a,#1766e6);color:#fff;border-radius:16px;padding:18px 20px;margin:0 0 14px}.paybar .pb-from{font-size:12.5px;opacity:.9}.paybar .pb-amt{font-size:30px;font-weight:900;letter-spacing:-.02em;margin:2px 0 6px}.paybar .pb-row{font-size:13px;margin:3px 0}.paybar .pb-bank{background:rgba(255,255,255,.15);border-radius:10px;padding:9px 12px;margin-top:9px;font-size:13px;font-weight:700;white-space:pre-line}.sv-mk{text-align:center;font-size:12.5px;color:#5a6b7b;margin-top:10px}.sv-mk a{color:#1766e6;font-weight:700}'; document.head.appendChild(st);
  var K=kindLabels(kind,region), c=calc(liveItems());
  var pb=document.createElement('div'); pb.className='paybar';
  var h='<div class="pb-from">'+K.title+' from '+esc(P.co.name||'—')+'</div><div class="pb-amt">'+esc(money(c.total,true))+'</div>';
  if(K.due&&P.due) h+='<div class="pb-row">Due: '+esc(fmtDate(P.due))+'</div>';
  if(K.bank&&P.co.bank) h+='<div class="pb-bank">'+esc(P.co.bank)+'</div>';
  pb.innerHTML=h; var pvb=document.querySelector('.card.right .pvbody'); if(pvb) pvb.insertBefore(pb,pvb.firstChild);
  var mk=document.createElement('div'); mk.className='sv-mk'; mk.innerHTML='Create your own free '+esc(K.title.toLowerCase())+' at <a href="/en/invoice">Free BizDoc</a> — no sign-up.'; var cta=document.querySelector('.cta'); if(cta) cta.appendChild(mk);
  try{ document.title=(P.co.name?P.co.name+' — ':'')+K.title; }catch(e){}
  setupPreview(); schedulePv();
  var mkb=$('make'); if(mkb) mkb.lastChild.nodeValue=' Download this '+K.title+' (PDF)';
}

/* ================= Theme swatches / nav / CSS ================= */
var THEMES=[['mono','Mono','#333333'],['blue','Blue','#1766e6'],['red','Red','#cf2a2e'],['green','Green','#179a63'],['purple','Purple','#7a39c4'],['orange','Orange','#e8820e']];
function setupTheme(){ try{ window.__theme=localStorage.getItem('free_theme')||'mono'; }catch(e){ window.__theme='mono'; } var host=$('themeseg'); if(!host)return;
  host.innerHTML='<span class="tlb">Color</span>'+THEMES.map(function(t){ return '<button type="button" class="sw'+(t[0]===window.__theme?' on':'')+'" data-th="'+t[0]+'" style="--sw:'+t[2]+'"><span class="dot"></span>'+t[1]+'</button>'; }).join('');
  host.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return; [].forEach.call(host.querySelectorAll('button'),function(x){x.classList.remove('on');}); b.classList.add('on'); window.__theme=b.getAttribute('data-th'); try{ localStorage.setItem('free_theme',window.__theme); }catch(e2){} schedulePv(); }); }
var DOCS=[['/en/invoice','Invoice'],['/en/estimate','Estimate / Quote'],['/en/receipt','Receipt'],['/en/purchase-order','Purchase Order'],['/en/packing-slip','Packing Slip / Delivery Note'],['/en/credit-note','Credit Note'],['/en/proforma-invoice','Pro Forma Invoice'],['/en/sales-order','Sales Order'],['/en/timesheet','Timesheet'],['/en/work-order','Work Order'],['/en/expense-report','Expense Report'],['/en/bill-of-sale','Bill of Sale'],['/en/donation-receipt','Donation Receipt']];
function setupNav(){ var host=$('docnav-en'); if(!host)return; var path=location.pathname.replace(/\.html$/,'').replace(/\/$/,''); host.innerHTML='<div class="docnav-track">'+DOCS.map(function(d){ return '<a class="docnav-item'+(d[0]===path?' on':'')+'" href="'+d[0]+'">'+d[1]+'</a>'; }).join('')+'</div>'; }
function injectCSS(){ var s=document.createElement('style'); s.textContent=
   '#docnav-en{background:var(--surf,#fff);border-bottom:1px solid var(--bd,#e6ebf2);overflow-x:auto;scrollbar-width:none}#docnav-en::-webkit-scrollbar{display:none}'
  +'#docnav-en .docnav-track{display:flex;gap:8px;width:max-content;padding:12px 16px;margin:0 auto}'
  +'#docnav-en .docnav-item{flex:0 0 auto;font-size:13px;font-weight:700;color:var(--mut,#5a6b80);text-decoration:none;padding:8px 15px;border-radius:999px;background:var(--surf2,#f1f5fb);border:1px solid var(--bd,#dce5f0);white-space:nowrap}'
  +'#docnav-en .docnav-item.on{background:linear-gradient(120deg,var(--ac,#1766e6),#2f9bf0);color:#fff;border-color:transparent}'
  +'.regseg{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}.regseg .rlb{font-size:11px;font-weight:700;color:#93a3b5;align-self:center;margin-right:2px}'
  +'.regseg button{font-family:inherit;font-size:12.5px;font-weight:700;color:#45607a;background:#fff;border:1px solid #dce5f0;border-radius:999px;padding:7px 12px;cursor:pointer}'
  +'.regseg button.on{background:#13263b;border-color:#13263b;color:#fff}'
  +'.themeseg{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:0 0 16px}.themeseg .tlb{font-size:11px;font-weight:700;color:#93a3b5;margin-right:2px}'
  +'.themeseg .sw{display:inline-flex;align-items:center;gap:5px;font-family:inherit;font-size:11.5px;font-weight:700;color:#5a6b7d;background:#fff;border:1px solid #e2eaf4;border-radius:999px;padding:5px 11px 5px 8px;cursor:pointer}'
  +'.themeseg .sw .dot{width:12px;height:12px;border-radius:50%;background:var(--sw);border:1px solid rgba(0,0,0,.12)}.themeseg .sw.on{border-color:var(--sw);color:#13263b;box-shadow:0 0 0 2px var(--sw) inset,0 0 0 1px #fff inset}'
  +'.items .hd,.items .rw{grid-template-columns:1fr 54px 92px 108px 24px;min-width:420px}'
  +'.items.noprice .hd,.items.noprice .rw{grid-template-columns:1fr 54px 24px;min-width:0}.items.noprice .i-price,.items.noprice .i-tax,.items.noprice #th-price,.items.noprice #th-tax{display:none}'
  +'.items.notax .hd,.items.notax .rw{grid-template-columns:1fr 70px 108px 24px;min-width:360px}.items.notax .i-tax,.items.notax #th-tax{display:none}'
  +'.items.amountonly .hd,.items.amountonly .rw{grid-template-columns:1fr 120px 24px;min-width:0}.items.amountonly .i-qty,.items.amountonly .i-tax,.items.amountonly #th-qty,.items.amountonly #th-tax{display:none}'
  +'textarea{font-family:inherit;font-size:13.5px;padding:10px 12px;border:1px solid var(--bd,#dce5f0);border-radius:9px;background:var(--surf,#fff);color:var(--ink,#13263b);width:100%;min-width:0;resize:vertical;line-height:1.45}'
  +'.convbar{margin:14px 0 2px;padding:12px 14px;border:1px dashed var(--ac,#1766e6);border-radius:12px;background:var(--surf2,#f3f8ff)}.convbar .cv-lb{font-size:12.5px;color:var(--mut,#45607a);margin-bottom:8px}.convbar .cv-lb b{color:var(--ac,#1766e6)}.convbar .cv-bs{display:flex;flex-wrap:wrap;gap:7px}'
  +'.convbar .cv-bs button{font-family:inherit;font-size:12.5px;font-weight:700;border:1px solid var(--ac,#1766e6);color:var(--ac,#1766e6);background:#fff;border-radius:999px;padding:7px 13px;cursor:pointer}.convbar .cv-bs button:hover{background:var(--ac,#1766e6);color:#fff}'
  +'.sharebox{margin-top:10px}.sharebtn{display:block;width:100%;font-family:inherit;font-size:13.5px;font-weight:800;border:1.5px solid var(--ac,#1766e6);color:var(--ac,#1766e6);background:#fff;border-radius:11px;padding:11px;cursor:pointer;text-align:center;text-decoration:none;box-sizing:border-box}.sharebtn:hover{background:#eaf1fe}'
  +'.savebox{margin-top:10px}.savebtn{display:block;width:100%;font-family:inherit;font-size:13.5px;font-weight:800;border:none;border-radius:11px;padding:12px;cursor:pointer;text-align:center;text-decoration:none;box-sizing:border-box;color:#fff;background:linear-gradient(120deg,#0f8a5f,#13a06f)}.savebtn:hover{filter:brightness(1.04)}.savebtn.ghost{background:#f3f6fb;color:#45607a;border:1px solid #dce5f0;font-weight:700}.savebtn.ghost:hover{background:#eceff5}'
  +'.savemsg{font-size:12px;text-align:center;margin-top:7px;min-height:14px}.savemsg.ok{color:#0e8a5f}.savemsg.err{color:#c0392b}.savemsg a{color:#1766e6;font-weight:700}'
  +'.shareout{margin-top:10px;background:#f3f8ff;border:1px solid #e2eaf4;border-radius:11px;padding:11px 12px}.shareout .so-lb{font-size:12px;color:#45607a;margin-bottom:7px}.shareout .so-row{display:flex;gap:6px}.shareout .so-row input{flex:1;min-width:0;font-size:12px;padding:8px 9px}.shareout .so-row button{font-family:inherit;font-size:12.5px;font-weight:800;border:none;border-radius:8px;padding:8px 14px;background:var(--ac,#1766e6);color:#fff;cursor:pointer}.shareout .so-note{font-size:11px;color:#8aa0b6;margin-top:7px;line-height:1.5}'
  +'.fl .hint{display:block;font-size:11px;color:#93a3b5;font-weight:500;margin-top:3px}'
  +'.filein{display:none}'
  +'.filebtn{display:flex;align-items:center;justify-content:center;gap:7px;width:100%;min-height:40px;padding:9px 12px;border:1px dashed var(--bd,#cfe0f2);border-radius:9px;background:var(--surf,#fff);color:var(--ac,#1766e6);font-family:inherit;font-size:13px;font-weight:700;cursor:pointer;text-align:center;line-height:1.2;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
  +'.filebtn:hover{background:#eaf1fe;border-color:var(--ac,#1766e6)}'
  +'.filebtn::before{content:"";width:15px;height:15px;flex:none;background:currentColor;-webkit-mask:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'white\' stroke-width=\'2.2\'><path d=\'M12 16V4m0 0 4 4m-4-4-4 4\'/><path d=\'M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2\'/></svg>") center/contain no-repeat;mask:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'white\' stroke-width=\'2.2\'><path d=\'M12 16V4m0 0 4 4m-4-4-4 4\'/><path d=\'M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2\'/></svg>") center/contain no-repeat}';
  document.head.appendChild(s); }

/* ================= Accounts & PRO (save to account, PRO unlock) ================= */
var KIND_TO_SLUG={ invoice:'invoice', quote:'estimate', delivery:'packing-slip', po:'purchase-order', receipt:'receipt', credit:'credit-note', proforma:'proforma-invoice', salesorder:'sales-order', timesheet:'timesheet', workorder:'work-order', expense:'expense-report', billofsale:'bill-of-sale', donation:'donation-receipt' };
window.__savedId=null;
function enType(){ return 'en_'+(KIND_TO_SLUG[kind]||'invoice'); }
function saveLabel(){ var n=v('cl-name')||kindLabels(kind,region).title; var no=v('doc-no'); return (no?no+' · ':'')+n; }
function relabelAcct(){ var a=document.getElementById('acctlink'); if(!a)return; a.textContent=(window.__me&&window.__me.authed)?'Account':'Sign in'; a.href=(window.__me&&window.__me.authed)?'/en/account':'/en/login'; }
async function fetchMe(){ try{ var r=await fetch('/api/auth/me',{credentials:'same-origin'}); window.__me=await r.json(); }catch(e){ window.__me={authed:false}; } relabelAcct(); refreshRemain(); renderSave(); }
function renderSave(){
  var box=$('savebox'); if(!box)return;
  if(document.body.classList.contains('shared-view')){ box.innerHTML=''; return; }
  var me=window.__me;
  if(!me||!me.authed){
    box.innerHTML='<a class="savebtn ghost" href="/en/login">💾 Sign in to save this document to your account</a>';
    return;
  }
  var editing=!!window.__savedId;
  box.innerHTML='<button type="button" id="savebtn2" class="savebtn">'+(editing?'✓ Update saved document':'💾 Save to account')+'</button><div id="savemsg" class="savemsg"></div>';
}
async function doSave(){
  var me=window.__me; if(!me||!me.authed){ location.href='/en/login'; return; }
  if(!liveItems().length){ toast('Add a line item first'); return; }
  if(!v('cl-name')){ toast('Enter the recipient name first'); return; }
  var btn=$('savebtn2'), sm=$('savemsg'); if(btn){ btn.disabled=true; btn.textContent='Saving…'; }
  var payload={ type:enType(), label:saveLabel(), data:buildDoc() };
  try{
    var r,j;
    if(window.__savedId){
      r=await fetch('/api/saved/'+window.__savedId,{method:'PUT',credentials:'same-origin',headers:{'content-type':'application/json'},body:JSON.stringify({label:payload.label,data:payload.data})});
      j=await r.json().catch(function(){return{};});
      if(r.ok){ if(sm){ sm.className='savemsg ok'; sm.textContent='Saved.'; } toast('Document updated'); }
      else { if(sm){ sm.className='savemsg err'; sm.textContent=j.error||'Could not update.'; } }
    } else {
      r=await fetch('/api/saved',{method:'POST',credentials:'same-origin',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
      j=await r.json().catch(function(){return{};});
      if(r.ok){ window.__savedId=j.id; if(sm){ sm.className='savemsg ok'; sm.innerHTML='Saved to your account. <a href="/en/account">View saved documents →</a>'; } toast('Saved to your account'); }
      else if(r.status===403&&j.upsell){ if(sm){ sm.className='savemsg err'; sm.innerHTML=(j.error||'Free plan limit reached.')+' <a href="/en/pricing" style="font-weight:800">Upgrade to PRO →</a>'; } }
      else if(r.status===401){ location.href='/en/login'; return; }
      else { if(sm){ sm.className='savemsg err'; sm.textContent=j.error||'Could not save.'; } }
    }
  }catch(e){ if(sm){ sm.className='savemsg err'; sm.textContent='A network error occurred.'; } }
  renderSave();
}
function fillFromDoc(P){
  window.__logo=(P.co&&P.co.logo)||''; try{ if(window.__logo) localStorage.setItem('free_en_logo',window.__logo); }catch(e){}
  if(P.theme){ window.__theme=P.theme; try{ localStorage.setItem('free_theme',P.theme); }catch(e){} var hs=$('themeseg'); if(hs){ [].forEach.call(hs.querySelectorAll('button'),function(x){ x.classList.toggle('on',x.getAttribute('data-th')===P.theme); }); } }
  function set(id,val){ var el=$(id); if(el&&val!=null) el.value=val; }
  applyRegion(P.region||'us');
  if(P.co){ set('co-name',P.co.name); set('co-taxid',P.co.taxid); set('co-email',P.co.email); set('co-phone',P.co.phone); set('co-addr',P.co.addr); set('co-bank',P.co.bank); }
  if(P.client){ set('cl-name',P.client.name); set('cl-addr',P.client.addr); set('cl-email',P.client.email); }
  set('ship-to',P.ship_to); set('doc-no',P.doc_no); set('ref-no',P.ref_no); set('issue',P.issue); set('due',P.due);
  set('terms',P.terms); set('method',P.method); set('notes',P.notes); set('terms-text',P.terms_text); set('tax-rate',P.tax_rate); set('ca-prov',P.prov);
  rowsEl.innerHTML=''; (P.items||[]).forEach(addRow); if(!rowsEl.children.length) addRow({});
  applyKind(P.kind||'invoice',true);
  renderLogoRow(); refreshTaxSelects(); schedulePv();
}
async function loadSavedParam(){
  var id=null; try{ id=new URLSearchParams(location.search).get('doc'); }catch(e){}
  if(!id)return false;
  try{
    var r=await fetch('/api/saved/'+encodeURIComponent(id),{credentials:'same-origin'});
    if(r.status===401){ location.href='/en/login?next=account'; return true; }
    if(!r.ok) return false;
    var j=await r.json(); if(!j||!j.data) return false;
    window.__savedId=j.id; fillFromDoc(j.data); renderSave();
    toast('Loaded “'+(j.label||'saved document')+'”');
    return true;
  }catch(e){ return false; }
}

/* ================= Init ================= */
(function init(){
  injectCSS(); setupNav(); setupTheme(); setupTermsSelect(); setupProv();
  region=guessRegion();
  var SH=parseShare();
  if(SH){ try{ enterShareView(SH); }catch(e){ console.error(e); } }
  else {
    applyRegion(region,true); loadCo(); setupLogo();
    if($('issue')) $('issue').value=todayISO();
    if($('doc-no')&&!$('doc-no').value) $('doc-no').value=nextDocNo();
    if(!loadDraft()){ addRow({}); } else { refreshTaxSelects(); }
    var qt=null; try{ qt=new URLSearchParams(location.search).get('type'); }catch(e){}
    applyKind(qt||kind,true);
    if($('due')&&!$('due').value&&(KINDS[kind].due||KINDS[kind].valid)) $('due').value=plusDays(30);
    setupPreview(); setupShare(); renderConvertBar(); refreshRemain(); schedulePv();
    // Accounts: load auth state, then (if ?doc) load the saved document.
    fetchMe().then(function(){ loadSavedParam(); });
  }
  /* events */
  var savebox=$('savebox'); if(savebox) savebox.addEventListener('click',function(e){ if(e.target&&e.target.id==='savebtn2'){ doSave(); } });
  var regseg=$('regseg'); if(regseg) regseg.addEventListener('click',function(e){ var b=e.target.closest('button[data-region]'); if(!b)return; applyRegion(b.getAttribute('data-region')); saveDraft(); schedulePv(); });
  var seg=$('seg'); if(seg) seg.addEventListener('click',function(e){ var b=e.target.closest('button[data-kind]'); if(!b)return; applyKind(b.getAttribute('data-kind')); if($('doc-no')) $('doc-no').value=nextDocNo(); renderConvertBar(); saveDraft(); });
  var cb=$('convbar'); if(cb) cb.addEventListener('click',function(e){ var b=e.target.closest('button[data-to]'); if(!b)return; convertTo(b.getAttribute('data-to')); });
  rowsEl.addEventListener('input',function(){ saveDraft(); schedulePv(); }); rowsEl.addEventListener('change',function(){ saveDraft(); schedulePv(); });
  rowsEl.addEventListener('click',function(e){ var d=e.target.closest('.del'); if(d){ d.closest('.rw').remove(); if(!rowsEl.children.length) addRow({}); saveDraft(); schedulePv(); } });
  var ar=$('addrow'); if(ar) ar.addEventListener('click',function(){ addRow({}); rowsEl.lastElementChild.querySelector('.i-name').focus(); saveDraft(); });
  DRAFT_IDS.concat(CO).forEach(function(id){ var el=$(id); if(!el)return; ['input','change'].forEach(function(ev){ el.addEventListener(ev,function(){ if(CO.indexOf(id)>=0) saveCo(); else saveDraft(); schedulePv(); }); }); });
  var mk=$('make'); if(mk) mk.addEventListener('click',download);
  var cl=$('clearbtn'); if(cl) cl.addEventListener('click',function(){ if(!confirm('Clear the recipient and line items and start a new document?\n(Your business details and logo are kept.)'))return; clearDraft(); ['cl-name','cl-addr','cl-email','ref-no','ship-to','notes','terms-text'].forEach(function(id){ if($(id)) $(id).value=''; }); if($('issue')) $('issue').value=todayISO(); if($('due')) $('due').value=plusDays(30); rowsEl.innerHTML=''; addRow({}); if($('doc-no')) $('doc-no').value=nextDocNo(); window.__savedId=null; renderSave(); schedulePv(); });
})();
})();

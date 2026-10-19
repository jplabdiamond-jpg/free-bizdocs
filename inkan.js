/* 電子印鑑ジェネレータ（個人印・会社丸印・会社角印・社判/住所印）。
   Canvasで描画し透過PNGとして出力。free_seal へ保存すると各書類ツールの印影になる。
   かすれ加工（5段階）・手押し風の歪みに対応。 */
(function(){
'use strict';
var E=function(id){return document.getElementById(id);};
var cv=E('cv'), ctx=cv.getContext('2d');
var MMPX=40; // 1mm=40px（高解像度）

var FONTS={
  mincho:'"Yu Mincho","YuMincho","Hiragino Mincho ProN","HGS明朝E","MS Mincho","Noto Serif JP",serif',
  gothic:'"NotoJP","Noto Sans JP","Yu Gothic","Hiragino Kaku Gothic ProN","Meiryo",sans-serif',
  maru:'"Hiragino Maru Gothic ProN","Rounded Mplus 1c","Quicksand","Meiryo",sans-serif'
};
try{ if(window.FontFace){ var ff=new FontFace('NotoJP','url(/fonts/noto-jp.ttf)'); ff.load().then(function(f){try{document.fonts.add(f);}catch(_){ } render();}).catch(function(){}); } }catch(e){}

var state={type:'personal',color:'#cf3a2e',font:'mincho',frame:'std',texture:1,distort:0,ink:true,bg:'transparent'};

/* ===== 乱数（シード固定で決定的に） ===== */
var _rng=Math.random, _fs=10;
function mulberry32(a){ return function(){ a|=0; a=a+0x6D2B79F5|0; var t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
function hashStr(s){ var h=2166136261; for(var i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619); } return h>>>0; }
function rr(a,b){ return a+(b-a)*_rng(); }
function seedString(){
  var v=function(id){return (E(id)||{}).value||'';};
  var t=state.type, s='';
  if(t==='personal') s=v('p-name')+'|'+v('p-dir');
  else if(t==='round') s=companyName('c')+'|'+v('c-role');
  else if(t==='square') s=companyName('sq')+'|'+v('sq-suf');
  else s=[v('a-zip'),v('a-addr'),companyName('a'),v('a-rep'),v('a-tel'),v('a-fax'),v('a-email'),v('a-url')].join('|');
  return t+'::'+s+'::'+state.texture+'::'+state.distort+'::'+(state.ink?1:0);
}

function sizeMM(){ var v=parseFloat((E('sizesel')||{}).value); return isFinite(v)&&v>0?v:15; }
function frameRatio(){ return state.frame==='thin'?0.020:state.frame==='bold'?0.050:0.034; }
function fontOf(){ return FONTS[state.font]||FONTS.mincho; }

function newCanvas(w,h){
  cv.width=Math.round(w); cv.height=Math.round(h);
  ctx.clearRect(0,0,cv.width,cv.height);
  if(state.bg==='white'){ ctx.fillStyle='#ffffff'; ctx.fillRect(0,0,cv.width,cv.height); }
  ctx.fillStyle=state.color; ctx.strokeStyle=state.color;
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.lineJoin='round'; ctx.lineCap='round';
  cv.style.width=Math.min(360,cv.width)+'px'; cv.style.height='auto';
}
function setFont(px){ _fs=px; ctx.font='900 '+px+'px '+fontOf(); }

/* 1文字描画（歪みON時は微小な回転・移動・拡縮） */
function dFactor(){ return state.distort===1?0.5:(state.distort>=2?1:0); }
function glyph(ch,x,y){
  if(!state.distort){ ctx.fillText(ch,x,y); return; }
  var f=dFactor(), j=_fs*0.035*f;
  ctx.save();
  ctx.translate(x+rr(-j,j), y+rr(-j,j));
  ctx.rotate(rr(-0.045,0.045)*f);
  ctx.scale(1+rr(-0.035,0.04)*f, 1+rr(-0.035,0.04)*f);
  ctx.fillText(ch,0,0);
  ctx.restore();
}

/* 歪んだ円（距離に小さなノイズ）／真円 */
function circle(cx,cy,r,lw){
  ctx.lineWidth=lw;
  if(!state.distort){ ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.stroke(); return; }
  var amp=r*0.016*dFactor(), k1=rr(0,6.28),k2=rr(0,6.28),k3=rr(0,6.28);
  var a1=amp*rr(0.5,1),a2=amp*rr(0.25,0.6),a3=amp*rr(0.1,0.4);
  var N=160; ctx.beginPath();
  for(var i=0;i<=N;i++){ var t=i/N*Math.PI*2;
    var rad=r+a1*Math.sin(t*2+k1)+a2*Math.sin(t*3+k2)+a3*Math.sin(t*5+k3);
    var x=cx+rad*Math.cos(t), y=cy+rad*Math.sin(t);
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  }
  ctx.closePath(); ctx.stroke();
}
/* 歪んだ長方形／真四角 */
function rect(x0,y0,w,h,lw){
  ctx.lineWidth=lw;
  if(!state.distort){ ctx.strokeRect(x0,y0,w,h); return; }
  var amp=Math.min(w,h)*0.012*dFactor();
  var pts=[], per=14;
  function edge(ax,ay,bx,by){ for(var i=0;i<per;i++){ var tt=i/per; pts.push([ax+(bx-ax)*tt+rr(-amp,amp), ay+(by-ay)*tt+rr(-amp,amp)]); } }
  edge(x0,y0,x0+w,y0); edge(x0+w,y0,x0+w,y0+h); edge(x0+w,y0+h,x0,y0+h); edge(x0,y0+h,x0,y0);
  ctx.beginPath(); pts.forEach(function(p,i){ if(i===0)ctx.moveTo(p[0],p[1]); else ctx.lineTo(p[0],p[1]); }); ctx.closePath(); ctx.stroke();
}

function vLine(chars, cx, cy, chH, fs){
  setFont(fs); var n=chars.length, top=cy-(n*chH)/2+chH/2;
  for(var i=0;i<n;i++) glyph(chars[i], cx, top+i*chH);
}
function vCols(str, cx, cy, boxW, boxH){
  var n=str.length; var ncol=n<=3?1:(n<=8?2:3);
  var per=Math.ceil(n/ncol); var cols=[]; for(var i=0;i<n;i+=per) cols.push(str.slice(i,i+per));
  ncol=cols.length; var colW=boxW/ncol;
  var rows=0; cols.forEach(function(c){rows=Math.max(rows,c.length);});
  var chH=boxH/rows; var fs=Math.min(colW,chH)*0.92;
  setFont(fs);
  for(var ci=0;ci<ncol;ci++){ var col=cols[ci];
    var x=cx+boxW/2-colW*(ci+0.5);
    var top=cy-(col.length*chH)/2+chH/2;
    for(var ri=0;ri<col.length;ri++) glyph(col[ri], x, top+ri*chH);
  }
}
function arcText(str, cx, cy, radius, centerAngle, stepDeg, fs){
  setFont(fs); var n=str.length, step=stepDeg*Math.PI/180;
  for(var i=0;i<n;i++){ var a=centerAngle+(i-(n-1)/2)*step;
    var x=cx+radius*Math.cos(a), y=cy+radius*Math.sin(a);
    ctx.save(); ctx.translate(x,y); ctx.rotate(a+Math.PI/2); glyph(str[i],0,0); ctx.restore();
  }
}

function companyName(prefix){
  var kind=(E(prefix+'-kind')||{}).value||'なし';
  var pos=(E(prefix+'-pos')||{}).value||'pre';
  var nm=((E(prefix+'-name')||{}).value||'山田商事').trim();
  if(kind==='なし') return nm;
  return pos==='post'? nm+kind : kind+nm;
}

/* ① 個人印（丸・一重） */
function drawPersonal(){
  var px=sizeMM()*MMPX; newCanvas(px,px);
  var cx=px/2, cy=px/2, fw=px*frameRatio();
  var r=px/2-fw/2-px*0.012;
  circle(cx,cy,r,fw);
  var nm=((E('p-name')||{}).value||'山田').trim(); if(!nm)nm='山田';
  var inner=r-fw*0.6;
  if((E('p-dir')||{}).value==='horiz'){
    var fs=Math.min(inner*1.7/Math.max(nm.length,1), inner*1.2); setFont(fs); glyph(nm, cx, cy);
  } else {
    var av=2*inner*0.82, n=nm.length, chH=av/n; var fs2=Math.min(chH*0.96, 2*inner*0.74);
    vLine(nm.split(''), cx, cy, chH, fs2);
  }
  finish(px,px);
}

/* ② 会社代表者印（二重丸：外周=社名、中央=役職） */
function drawRound(){
  var px=sizeMM()*MMPX; newCanvas(px,px);
  var cx=px/2, cy=px/2, fw=px*frameRatio();
  var rOut=px/2-fw/2-px*0.01, rIn=rOut*0.60;
  circle(cx,cy,rOut,fw); circle(cx,cy,rIn,fw*0.62);
  var comp=companyName('c'); var ringW=rOut-rIn, rText=rIn+ringW*0.55;
  var stepDeg=comp.length>1?360/comp.length:0;
  var arcSp=rText*stepDeg*Math.PI/180;
  var fsArc=Math.min(ringW*0.74, arcSp*0.92);
  arcText(comp, cx, cy, rText, -Math.PI/2, stepDeg, fsArc);
  var role=((E('c-role')||{}).value||'代表取締役印').trim(); if(!role)role='代表取締役印';
  vCols(role, cx, cy, rIn*1.45, rIn*1.45);
  finish(px,px);
}

/* ③ 会社角印（正方形） */
function drawSquare(){
  var px=sizeMM()*MMPX; newCanvas(px,px);
  var fw=px*frameRatio()*1.15, m=fw/2+px*0.02;
  rect(m,m,px-2*m,px-2*m,fw);
  var suf=(E('sq-suf')||{}).value||'之印';
  var text=companyName('sq')+(suf==='なし'?'':suf);
  var pad=m+fw/2+px*0.04, areaX=pad, areaY=pad, areaW=px-2*pad, areaH=px-2*pad;
  var n=text.length, ncol=Math.max(1,Math.round(Math.sqrt(n)));
  var rows=Math.ceil(n/ncol); ncol=Math.ceil(n/rows);
  var colW=areaW/ncol, chH=areaH/rows, fs=Math.min(colW,chH)*0.98; setFont(fs);
  var idx=0;
  for(var ci=0;ci<ncol;ci++){
    var cnt=Math.min(rows, n-ci*rows); if(cnt<=0)break;
    var x=areaX+areaW-colW*(ci+0.5), top=areaY+(areaH-cnt*chH)/2;
    for(var ri=0;ri<cnt;ri++){ glyph(text[idx++], x, top+chH*(ri+0.5)); }
  }
  finish(px,px);
}

/* ④ 社判／住所印（長方形・多行） */
function drawAddress(){
  var Wmm=parseFloat((E('a-width')||{}).value)||60; var W=Wmm*MMPX;
  var dir=(E('a-dir')||{}).value||'left';
  var lines=[];
  var zip=((E('a-zip')||{}).value||'').trim();
  var addr=((E('a-addr')||{}).value||'').trim();
  var head=(zip?('〒'+zip.replace(/^〒/,'')+'　'):'')+addr;
  if(head.trim()) lines.push({t:head,cap:0.052});
  var nm=companyName('a'); if(nm) lines.push({t:nm,cap:0.105,strong:true});
  var rep=((E('a-rep')||{}).value||'').trim(); if(rep) lines.push({t:rep,cap:0.080,strong:true});
  var tel=((E('a-tel')||{}).value||'').trim(), fax=((E('a-fax')||{}).value||'').trim();
  var tf=[tel?('TEL '+tel):'',fax?('FAX '+fax):''].filter(Boolean).join('　'); if(tf) lines.push({t:tf,cap:0.050});
  var em=((E('a-email')||{}).value||'').trim(); if(em) lines.push({t:em,cap:0.046});
  var url=((E('a-url')||{}).value||'').trim(); if(url) lines.push({t:url,cap:0.046});
  if(!lines.length) lines.push({t:'株式会社 山田商事',cap:0.105,strong:true});
  var pad=W*0.05, contentW=W-2*pad;
  lines.forEach(function(L){ ctx.font=(L.strong?'900 ':'600 ')+'100px '+fontOf();
    var w=ctx.measureText(L.t).width||1; L.fs=Math.min(contentW*100/w, W*L.cap); });
  var lh=1.5, H=pad*2; lines.forEach(function(L){H+=L.fs*lh;});
  newCanvas(W,H);
  var fw=W*0.012*(state.frame==='bold'?1.6:state.frame==='thin'?0.7:1);
  rect(fw/2+2, fw/2+2, W-fw-4, H-fw-4, fw);
  var y=pad;
  lines.forEach(function(L){
    _fs=L.fs; ctx.font=(L.strong?'900 ':'600 ')+L.fs+'px '+fontOf();
    y+=L.fs*lh/2;
    if(dir==='center'){ ctx.textAlign='center'; glyph(L.t, W/2, y); }
    else { ctx.textAlign='left'; glyph(L.t, pad, y); }
    y+=L.fs*lh/2;
  });
  ctx.textAlign='center';
  finish(W,H);
}

/* 不定形のインク抜けマーク（ブラシ風：正円ではなく歪んだ・伸びた形） */
function erodeMark(x,y,size){
  var ang=rr(0,6.283), ex=rr(0.7,2.3), ey=rr(0.48,1.12);
  ctx.save(); ctx.translate(x,y); ctx.rotate(ang); ctx.scale(ex,ey);
  var n=6+(_rng()*5|0); ctx.beginPath();
  for(var i=0;i<=n;i++){ var a=i/n*6.283, rad=size*rr(0.42,1.18);
    var px=Math.cos(a)*rad, py=Math.sin(a)*rad; if(i===0)ctx.moveTo(px,py); else ctx.lineTo(px,py); }
  ctx.closePath(); ctx.fill(); ctx.restore();
}
function darken(hex,amt){ var c=(hex||'#cf3a2e').replace('#',''); if(c.length===3)c=c.replace(/./g,'$&$&');
  var r=parseInt(c.substr(0,2),16),g=parseInt(c.substr(2,2),16),b=parseInt(c.substr(4,2),16);
  r=Math.round(r*(1-amt));g=Math.round(g*(1-amt));b=Math.round(b*(1-amt)); return 'rgb('+r+','+g+','+b+')'; }

/* かすれ加工（0=なし / 1弱 2中 3強 4特強 5最強）。ブラシ風の不定形マークで掠れを表現 */
var FRAC=[0,0.06,0.13,0.26,0.40,0.56];
function _erode(w,h){
  var lv=state.texture|0; if(lv<=0) return;
  ctx.save(); ctx.globalCompositeOperation='destination-out'; ctx.fillStyle='#000';
  var area=w*h, base=Math.sqrt(area), frac=FRAC[lv]||0, step=Math.max(5, base/130);
  // 粒状のインク抜け（主役）
  for(var y=0;y<h;y+=step){ for(var x=0;x<w;x+=step){
    if(_rng()<frac){ ctx.globalAlpha=rr(0.5,1); erodeMark(x+rr(-step*0.5,step*0.5), y+rr(-step*0.5,step*0.5), rr(step*0.4,step*1.35)); }
  }}
  // 大きめの欠け（中以上）
  if(lv>=2){ var patch=Math.floor(area*0.00016*(lv-1));
    for(var k=0;k<patch;k++){ ctx.globalAlpha=rr(0.55,1); erodeMark(rr(0,w), rr(0,h), rr(base*0.006, base*0.006+base*0.011*(lv-1))); } }
  // かすれ筋（特強以上）
  if(lv>=4){ var streaks=Math.floor(base*0.16*(lv-3)); ctx.lineCap='round';
    for(var s=0;s<streaks;s++){ ctx.globalAlpha=rr(0.4,0.9); ctx.lineWidth=rr(0.8,2.6);
      var sx=rr(0,w), sy=rr(0,h), ang=rr(0,6.283), len=rr(base*0.05, base*0.2);
      ctx.beginPath(); ctx.moveTo(sx,sy); ctx.lineTo(sx+Math.cos(ang)*len, sy+Math.sin(ang)*len); ctx.stroke(); } }
  // 縁のかすれ
  var edge=Math.floor((w+h)*0.08*lv);
  for(var e=0;e<edge;e++){ ctx.globalAlpha=rr(0.3,0.65); erodeMark(rr(0,w), rr(0,h), rr(1,step*0.8)); }
  ctx.restore(); ctx.globalAlpha=1; ctx.globalCompositeOperation='source-over';
}

/* インク溜まり（盛り）：既存インクの上にだけ濃い色を重ね、部分的に厚塗り・付着した質感を出す */
function inkBuild(w,h){
  if(!state.ink) return;
  ctx.save(); ctx.globalCompositeOperation='source-atop';
  var area=w*h, base=Math.sqrt(area);
  ctx.fillStyle=darken(state.color,0.42);
  var n=Math.floor(area*0.0007);
  for(var i=0;i<n;i++){ ctx.globalAlpha=rr(0.06,0.22); erodeMark(rr(0,w), rr(0,h), rr(base*0.008, base*0.04)); }
  ctx.fillStyle=darken(state.color,0.58);
  var pools=Math.floor(base*0.10);
  for(var p=0;p<pools;p++){ ctx.globalAlpha=rr(0.12,0.34); erodeMark(rr(0,w), rr(0,h), rr(base*0.015, base*0.06)); }
  ctx.restore(); ctx.globalAlpha=1; ctx.globalCompositeOperation='source-over';
}

/* 仕上げ：インク溜まり → かすれ の順で重ねる */
function finish(w,h){ inkBuild(w,h); _erode(w,h); }

function render(){
  try{
    _rng = (state.texture||state.distort||state.ink) ? mulberry32(hashStr(seedString())) : Math.random;
    if(state.type==='personal') drawPersonal();
    else if(state.type==='round') drawRound();
    else if(state.type==='square') drawSquare();
    else drawAddress();
  }catch(e){ /* noop */ }
}

/* ===== UI ===== */
var SIZES={
  personal:[['10.5','認印 10.5mm',false],['12','12mm',false],['13.5','銀行印 13.5mm',true],['15','実印 15mm',false],['16.5','実印 16.5mm',false],['18','18mm',false]],
  round:[['16.5','16.5mm',false],['18','会社実印 18mm',true],['21','21mm',false],['24','24mm',false]],
  square:[['21','21mm',true],['24','角印 24mm',false],['27','27mm',false],['30','30mm',false]],
  address:[['60','—',true]]
};
function showPanel(){
  ['panel-personal','panel-round','panel-square','panel-address'].forEach(function(id){ var el=E(id); if(el) el.style.display='none'; });
  var map={personal:'panel-personal',round:'panel-round',square:'panel-square',address:'panel-address'};
  var p=E(map[state.type]); if(p) p.style.display='';
  var sel=E('sizesel'); if(sel){ var opt=SIZES[state.type]; sel.innerHTML=opt.map(function(o){return '<option value="'+o[0]+'"'+(o[2]?' selected':'')+'>'+o[1]+'</option>';}).join(''); sel.style.display=(state.type==='address')?'none':''; }
  var aw=E('addrwidthwrap'); if(aw) aw.style.display=(state.type==='address')?'':'none';
}
function bind(){
  var seg=E('typeseg');
  if(seg) seg.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
    [].forEach.call(this.children,function(x){x.classList.remove('on');}); b.classList.add('on');
    state.type=b.getAttribute('data-t'); showPanel(); render(); });
  var cseg=E('colorseg');
  if(cseg) cseg.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
    [].forEach.call(this.querySelectorAll('button'),function(x){x.classList.remove('on');}); b.classList.add('on');
    state.color=b.getAttribute('data-c'); var cc=E('color-custom'); if(cc)cc.value=state.color; render(); });
  var cc=E('color-custom'); if(cc) cc.addEventListener('input',function(){ state.color=cc.value;
    [].forEach.call(E('colorseg').querySelectorAll('button'),function(x){x.classList.remove('on');}); render(); });
  var fs=E('fontsel'); if(fs) fs.addEventListener('change',function(){state.font=fs.value;render();});
  var fr=E('framesel'); if(fr) fr.addEventListener('change',function(){state.frame=fr.value;render();});
  var tx=E('texturesel'); if(tx) tx.addEventListener('change',function(){state.texture=parseInt(tx.value,10)||0;render();});
  var di=E('distortsel'); if(di) di.addEventListener('change',function(){state.distort=parseInt(di.value,10)||0;render();});
  var ip=E('inkpool'); if(ip) ip.addEventListener('change',function(){state.ink=ip.checked;render();});
  var bgseg=E('bgseg'); if(bgseg) bgseg.addEventListener('click',function(e){ var b=e.target.closest('button'); if(!b)return;
    [].forEach.call(this.children,function(x){x.classList.remove('on');}); b.classList.add('on');
    state.bg=b.getAttribute('data-bg'); E('cvwrap').classList.toggle('whitebg', state.bg==='white'); render(); });
  var sz=E('sizesel'); if(sz) sz.addEventListener('change',render);
  ['p-name','p-dir','c-kind','c-pos','c-name','c-role','sq-kind','sq-pos','sq-name','sq-suf',
   'a-zip','a-addr','a-kind','a-pos','a-name','a-rep','a-tel','a-fax','a-email','a-url','a-dir','a-width'
  ].forEach(function(id){ var el=E(id); if(!el)return; el.addEventListener('input',render); el.addEventListener('change',render); });
  E('dl').addEventListener('click',function(){ try{ var a=document.createElement('a');
    a.download='inkan_'+state.type+'.png'; a.href=cv.toDataURL('image/png'); document.body.appendChild(a); a.click(); a.remove();
  }catch(e){ alert('ダウンロードに失敗しました: '+e.message); } });
  var us=E('useseal'); if(us) us.addEventListener('click',function(){ try{
    localStorage.setItem('free_seal', cv.toDataURL('image/png'));
    var m=E('savemsg'); if(m){ m.textContent='保存しました。請求書・見積書など各ツールの印影に設定されます。'; m.style.display='block'; setTimeout(function(){m.style.display='none';},4000); }
  }catch(e){ alert('保存に失敗しました: '+e.message); } });
}
(function init(){ showPanel(); bind(); render(); })();
})();

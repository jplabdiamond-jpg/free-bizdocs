/* Free BizDoc — 公式PDF(損益計算書)への記入ロジック（UMD: ブラウザ/Node共用）
   page: pdf-lib の PDFPage / font: 埋め込み済みフォント / map: aoiro-ippan-map.json
   computed: {コード:数値} / header: {キー:文字列} / color: pdf-lib の rgb() 色 */
(function(root,factory){
  if(typeof module==='object'&&module.exports){module.exports=factory();}
  else{root.AoiroFill=factory();}
}(typeof self!=='undefined'?self:this,function(){
  function yen(n){return Number(n).toLocaleString('en-US');}
  function fitSize(font,s,size,maxW){ // 枠に収まらない長文字列はフォントを縮小
    while(size>5 && font.widthOfTextAtSize(s,size)>maxW){ size-=0.5; }
    return size;
  }
  function fillPage(page, font, map, computed, header, color){
    var H=map.h;
    function draw(text,x,baseTop,size,align,maxW){
      if(text==null||text==='')return;
      var s=String(text);
      if(maxW) size=fitSize(font,s,size,maxW);
      var w=font.widthOfTextAtSize(s,size), dx=x;
      if(align==='R')dx=x-w; else if(align==='C')dx=x-w/2;
      page.drawText(s,{x:dx,y:H-baseTop,size:size,font:font,color:color});
    }
    Object.keys(map.header).forEach(function(k){
      var v=header[k]; if(v==null||v==='')return;
      var f=map.header[k]; draw(v,f.x,f.baseTop,f.size,f.align,f.maxW);
    });
    Object.keys(computed).forEach(function(code){
      var v=computed[code]; if(!v)return;        // 0・空欄は記入しない
      var c=map.amounts[code]; if(!c)return;
      var val=v;
      if(c.strip){ val=Math.round(v/Math.pow(10,c.strip)); if(!val)return; } // 印字済み末尾0の左に非0部を記入
      draw(yen(val), c.rightX, c.baseTop, c.size||9, 'R', c.maxW);
    });
  }
  return {fillPage:fillPage};
}));

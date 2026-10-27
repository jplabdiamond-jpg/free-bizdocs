/* PR帯：PROプラン 特別価格カウントダウン（全ページ共通） */
(function(){
  var host=document.querySelector('.promo .in'); if(!host) return;
  host.classList.add('promo-cd');
  host.innerHTML=''
    +'<span class="pc-txt">🔥 PRO 期間限定 <b>月¥2,000</b>（通常¥3,000）｜保存・入金管理まで<b>まるごと</b></span>'
    +'<span class="pc-timer" role="timer" aria-label="特別価格終了までの残り時間">'
    +  '<span class="pc-lbl">特別価格 終了まで</span>'
    +  '<span class="pc-dig">'
    +    '<span class="pc-n" id="pcD">00</span><span class="u">日</span>'
    +    '<span class="pc-n" id="pcH">00</span><i>:</i>'
    +    '<span class="pc-n" id="pcM">00</span><i>:</i>'
    +    '<span class="pc-n" id="pcS">00</span>'
    +  '</span>'
    +'</span>'
    +'<a class="pc-cta" href="/pricing">今すぐ申し込む →</a>';
  var eD=document.getElementById('pcD'),eH=document.getElementById('pcH'),
      eM=document.getElementById('pcM'),eS=document.getElementById('pcS');
  // 今月末締め（＝翌月1日0:00）までをカウントダウン。毎月自動で更新。
  function target(){var n=new Date();return new Date(n.getFullYear(),n.getMonth()+1,1,0,0,0,0);}
  function p(n){return (n<10?'0':'')+n;}
  function tick(){
    var diff=Math.max(0,target()-new Date());
    var s=Math.floor(diff/1000);
    var d=Math.floor(s/86400); s-=d*86400;
    var h=Math.floor(s/3600);  s-=h*3600;
    var m=Math.floor(s/60);    s-=m*60;
    eD.textContent=p(d); eH.textContent=p(h); eM.textContent=p(m); eS.textContent=p(s);
  }
  tick(); setInterval(tick,1000);

  /* ===== 確定申告シーズンの再訪バー（12/1〜翌3/15に自動表示。?fbseason=1 で常時プレビュー） ===== */
  (function seasonBar(){
    try{
      var q=new URLSearchParams(location.search), force=q.get('fbseason');
      var now=new Date(), m=now.getMonth()+1, d=now.getDate();
      var inSeason=(m===12)||(m===1)||(m===2)||(m===3&&d<=15);
      if(force==='1') inSeason=true; else if(force==='0') inSeason=false;
      if(!inSeason) return;
      // 一度閉じたら3日間は非表示を記憶（再訪では再表示される）
      try{ var ds=localStorage.getItem('fb_season_dismiss'); if(force!=='1'&&ds&&(Date.now()-parseInt(ds,10))<3*864e5) return; }catch(e){}
      var promoEl=host.closest?host.closest('.promo'):host.parentElement; if(!promoEl||!promoEl.parentNode) return;
      var css=''
        +'.fb-season{background:linear-gradient(100deg,#0d5c3f,#12805a);color:#fff;font-family:inherit}'
        +'.fb-season .in{max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:12px;padding:8px 16px;font-size:13px}'
        +'.fb-season .t{flex:1;line-height:1.5}.fb-season .t b{font-weight:800}'
        +'.fb-season a.go{flex:none;background:#fff;color:#0d5c3f;font-weight:800;text-decoration:none;border-radius:999px;padding:6px 14px;font-size:12.5px;white-space:nowrap}'
        +'.fb-season a.go:hover{background:#eafaf2}'
        +'.fb-season .x{flex:none;background:none;border:none;color:rgba(255,255,255,.82);font-size:17px;line-height:1;cursor:pointer;padding:2px 4px}'
        +'@media(max-width:640px){.fb-season .in{font-size:12px;gap:9px;padding:8px 12px}.fb-season a.go{padding:6px 11px}}';
      var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);
      var bar=document.createElement('div'); bar.className='fb-season';
      bar.innerHTML='<div class="in"><span class="t">📝 <b>確定申告の準備</b>はできていますか？請求書控え・源泉徴収・経費の計算をまとめて。</span>'
        +'<a class="go" href="/kakutei-shinkoku?utm_source=season_bar&utm_medium=onsite&utm_campaign=kakutei">準備ガイドを見る →</a>'
        +'<button class="x" type="button" aria-label="閉じる">×</button></div>';
      promoEl.parentNode.insertBefore(bar, promoEl.nextSibling);
      bar.querySelector('.x').addEventListener('click',function(){ bar.remove(); try{ localStorage.setItem('fb_season_dismiss', String(Date.now())); }catch(e){} });
    }catch(e){}
  })();
})();

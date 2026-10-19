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
})();

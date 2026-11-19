/* 다송세무회계 "이런 분은 검토해 보세요" 위젯
   사용법: <div id="dasong-checkups"></div>
          <script src="https://cdn.jsdelivr.net/gh/dasongtax/dasongtax-news@main/checkups.js" defer></script> */
(function(){
  var DISCLAIMER="본 내용은 일반적인 세무 정보 안내이며, 실제 적용 여부와 환급 가능성은 개인별 사실관계에 따라 달라집니다. 반드시 세무 전문가의 충분한 검토를 받으시기 바랍니다. 본 내용만을 근거로 한 판단이나 신고 결과에 대하여 다송세무회계는 책임을 지지 않습니다.";
  function esc(s){return String(s||"").replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
  function render(el,items){
    var css="<style>#dasong-checkups{margin-top:48px}#dasong-checkups h3{font-size:22px;margin:0 0 6px;font-weight:700}#dasong-checkups .dc-sub{color:#667085;font-size:14px;margin:0 0 16px}#dasong-checkups .dc-item{border-top:1px solid #e4e7ec;padding:18px 0}#dasong-checkups .dc-meta{font-size:12px;color:#2563C9;font-weight:600;margin-bottom:4px}#dasong-checkups .dc-title{font-size:17px;font-weight:700;margin:0 0 8px;line-height:1.45}#dasong-checkups ul{margin:0 0 8px 18px;padding:0;font-size:14px;line-height:1.6}#dasong-checkups .dc-benefit{font-size:14px;line-height:1.6;margin:0 0 6px}#dasong-checkups .dc-kw{font-size:12px;color:#667085}#dasong-checkups .dc-basis{font-size:12px;color:#98a2b3;margin-top:4px}#dasong-checkups .dc-disc{font-size:12px;color:#667085;background:#f5f7fa;border-radius:8px;padding:12px 14px;margin-top:12px;line-height:1.6}</style>";
    var h=css+"<h3>이런 분은 검토해 보세요</h3><p class='dc-sub'>세법 조문·판례를 검토해 받을 수 있는 세금 혜택과 경정청구(환급) 가능성을 매주 정리합니다.</p>";
    items.forEach(function(it){
      h+="<article class='dc-item'><div class='dc-meta'>"+esc(it.tax)+" · "+esc(it.date)+"</div><h4 class='dc-title'>"+esc(it.title)+"</h4><ul>"+(it.targets||[]).map(function(t){return"<li>"+esc(t)+"</li>";}).join("")+"</ul><p class='dc-benefit'>"+esc(it.benefit)+"</p><div class='dc-kw'>"+(it.keywords||[]).map(function(k){return"#"+esc(k).replace(/\s/g,"");}).join(" ")+"</div>"+(it.basis?"<div class='dc-basis'>근거: "+esc(it.basis)+"</div>":"")+"</article>";
    });
    h+="<p class='dc-disc'>※ "+DISCLAIMER+"</p>";
    el.innerHTML=h;
  }
  function go(){
    var el=document.getElementById("dasong-checkups"); if(!el) return;
    fetch("https://raw.githubusercontent.com/dasongtax/dasongtax-news/main/news.json",{cache:"no-store"})
      .then(function(r){return r.json();})
      .then(function(d){var it=(d.checkups||[]); if(it.length) render(el,it);})
      .catch(function(){});
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",go); else go();
})();

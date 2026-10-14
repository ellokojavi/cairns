// Test mode for the planner (planner.html?r=<route>&sim=1).
// Replaces the phone's clock and GPS with simulated ones, so the whole hike can be
// rehearsed from a sofa: a walker moves along the route at the planned pace (with the
// planned stops), time runs faster on demand, and you can jump to any point or step
// off the trail. Check-ins are saved apart from the real ones and never mix with them.
//
// Loaded from the <head> before the planner script: the clock and GPS must be in place
// before the planner reads them. The control panel is built once the page has loaded.
"use strict";
(function(){
  const RealDate=Date, realNow=()=>RealDate.now();
  // ---------- simulated clock ----------
  const SIM=window.__SIM={base:realNow(),at:realNow(),rate:1,
    now(){return this.base+(realNow()-this.at)*this.rate},
    set(ms){this.base=ms;this.at=realNow()},
    setRate(r){this.base=this.now();this.at=realNow();this.rate=r},
    m:0,off:0,pause:0,playing:false,pace:1,watchers:new Map(),nextWatch:1};
  class SimDate extends RealDate{
    constructor(...a){if(a.length)super(...a);else super(SIM.now())}
    static now(){return SIM.now()}
  }
  window.Date=SimDate;

  // ---------- simulated GPS: the walker's position, or a step off the trail ----------
  function position(){
    const T=typeof TRK!=='undefined'?TRK:null;if(!T)return null;
    let k=0;while(k<T.n-2&&T.cd[k+1]<SIM.m)k++;
    const f=Math.max(0,Math.min(1,(SIM.m-T.cd[k])/Math.max(1,T.cd[k+1]-T.cd[k])));
    let la=T.la[k]+(T.la[k+1]-T.la[k])*f, lo=T.lo[k]+(T.lo[k+1]-T.lo[k])*f;
    if(SIM.off){   // sideways from the direction of travel
      const kx=111320*Math.cos(la*Math.PI/180),dx=(T.lo[k+1]-T.lo[k])*kx,dy=(T.la[k+1]-T.la[k])*110540,L=Math.hypot(dx,dy)||1;
      lo+=(-dy/L)*SIM.off/kx; la+=(dx/L)*SIM.off/110540;
    }
    return{coords:{latitude:la,longitude:lo,accuracy:8,altitude:null},timestamp:SIM.now()};
  }
  const fakeGeo={
    getCurrentPosition(ok,err){setTimeout(()=>{const p=position();p?ok(p):err&&err({code:2})},350)},
    watchPosition(ok,err){const id=SIM.nextWatch++;SIM.watchers.set(id,ok);setTimeout(()=>{const p=position();if(p)ok(p)},350);return id},
    clearWatch(id){SIM.watchers.delete(id)}
  };
  try{Object.defineProperty(navigator,'geolocation',{value:fakeGeo,configurable:true})}catch(e){}
  SIM.emit=()=>{const p=position();if(p)SIM.watchers.forEach(cb=>cb(p))};

  // ---------- control panel ----------
  const css=`
#simbar{position:fixed;left:0;right:0;bottom:0;z-index:20;background:#2B1D3A;color:#F3ECFA;font:14px/1.35 system-ui,-apple-system,sans-serif;
  padding:8px 12px calc(10px + env(safe-area-inset-bottom,0px));box-shadow:0 -4px 18px rgba(0,0,0,.25)}
#simbar .r{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;max-width:560px;margin:0 auto}
#simbar .r+.r{margin-top:6px}
#simbar b.tag{background:#E8B931;color:#2B1D3A;border-radius:4px;padding:1px 7px;font-size:12px;letter-spacing:.06em}
#simbar .clk{font:700 20px/1 system-ui;font-variant-numeric:tabular-nums}
#simbar button,#simbar select{font:600 13px system-ui;border-radius:6px;border:1px solid rgba(255,255,255,.35);background:transparent;color:inherit;padding:5px 9px}
#simbar button.on{background:#E8B931;color:#2B1D3A;border-color:#E8B931}
#simbar input[type=range]{flex:1 1 160px;accent-color:#E8B931}
#simbar .pos{flex:1 1 100%;font-size:12.5px;opacity:.85;font-variant-numeric:tabular-nums}
#simbar .chips{display:flex;gap:4px;flex-wrap:wrap}
#simbar .chips button{padding:3px 8px;min-width:28px}
#simbar a{color:inherit}
#simbar .min{margin-left:auto}
#simbar.small .more{display:none}
body.sim main{padding-bottom:230px}
body.sim #bar{outline:3px dashed #E8B931;outline-offset:2px}`;

  function build(){
    // the planner's own globals (top-level const/let are shared between classic scripts, not on window)
    const R=window.ROUTE,ST=STOPS,T=TRK,TOTAL=TOT,SIDX=SI;
    document.body.classList.add('sim');
    const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
    const d=document.createElement('div');d.id='simbar';
    d.innerHTML=`<div class="r"><b class="tag">SIMULATION</b><span class="clk" id="sclk"></span>
        <button id="splay" type="button">▶ Walk</button>
        <select id="srate" aria-label="Speed"><option value="1">1×</option><option value="10">10×</option><option value="60" selected>60×</option><option value="300">300×</option></select>
        <button class="min" id="smin" type="button">Hide</button></div>
      <div class="r more"><input type="range" id="skm" min="0" max="${Math.round(TOTAL)}" step="10" value="0" aria-label="Position along the route">
        <span class="pos" id="spos"></span></div>
      <div class="r more"><span>Go to</span><span class="chips" id="schips">${ST.map((s,i)=>`<button type="button" data-i="${i}" title="${s.n}">${i+1}</button>`).join('')}</span></div>
      <div class="r more"><label>Pace <select id="space"><option value="0.8">faster than plan</option><option value="1" selected>as planned</option><option value="1.25">25% slower</option><option value="1.5">50% slower</option></select></label>
        <label>Off trail <select id="soff"><option value="0">on it</option><option value="60">60 m</option><option value="250">250 m</option><option value="1500">1.5 km</option></select></label>
        <button id="sreset" type="button">Restart</button><a href="${location.pathname}?r=${encodeURIComponent(R.id)}">Exit simulation</a></div>`;
    document.body.appendChild(d);
    const $=id=>document.getElementById(id);
    const fmt=t=>{const x=new Date(t);return String(x.getHours()).padStart(2,'0')+':'+String(x.getMinutes()).padStart(2,'0')};
    const elAt=m=>{let k=0;while(k<T.n-2&&T.cd[k+1]<m)k++;const f=(m-T.cd[k])/Math.max(1,T.cd[k+1]-T.cd[k]);return T.el[k]+(T.el[k+1]-T.el[k])*Math.max(0,Math.min(1,f))};
    const stopAt=m=>ST.findIndex((s,i)=>Math.abs(T.cd[SIDX[i]]-m)<15);
    const legOf=m=>{for(let i=1;i<ST.length;i++)if(m<T.cd[SIDX[i]])return i;return ST.length-1};
    // the sim state survives a reload, kept apart from real check-ins
    const KEY='hike-sim-walker-'+R.id;
    function save(){try{localStorage.setItem(KEY,JSON.stringify({t:SIM.now(),m:SIM.m,off:SIM.off,rate:SIM.rate,pace:SIM.pace}))}catch(e){}}
    function restart(){
      // start 20 minutes before the planned departure, today, standing at the trailhead
      const dep=$('dep').value||R.dep||'08:00',[h,mi]=dep.split(':').map(Number),x=new RealDate();x.setHours(h,mi-20,0,0);
      SIM.set(x.getTime());SIM.m=0;SIM.off=0;SIM.pause=0;SIM.playing=false;
      try{localStorage.removeItem('hike-sim-'+R.id)}catch(e){}
      state.ci=state.ci.map(()=>null);fix=null;
      $('soff').value='0';save();location.reload();
    }
    try{const s=JSON.parse(localStorage.getItem(KEY)||'null');
      if(s){SIM.set(s.t);SIM.m=s.m;SIM.off=s.off;SIM.pace=s.pace||1;SIM.setRate(s.rate||60);$('srate').value=String(s.rate||60);$('space').value=String(s.pace||1);$('soff').value=String(s.off||0)}
      else{const dep=(R.dep||'08:00').split(':').map(Number),x=new RealDate();x.setHours(dep[0],dep[1]-20,0,0);SIM.set(x.getTime());SIM.setRate(60)}
    }catch(e){}
    function show(){
      $('sclk').textContent=fmt(SIM.now());
      $('skm').value=Math.round(SIM.m);
      const si=stopAt(SIM.m),leg=legOf(SIM.m);
      $('spos').textContent=`Simulated position: km ${(SIM.m/1000).toFixed(2)} of ${(TOTAL/1000).toFixed(1)}, ${Math.round(elAt(SIM.m))} m`
        +(si>=0?` · at stop ${si+1}, ${ST[si].n}`:` · between ${leg} and ${leg+1}`)
        +(SIM.off?` · ${SIM.off} m off the trail`:'')+(SIM.pause>0?` · resting ${Math.ceil(SIM.pause)} min`:'');
      $('splay').textContent=SIM.playing?'❚❚ Pause':'▶ Walk';$('splay').classList.toggle('on',SIM.playing);
    }
    function moved(){SIM.emit();if(!SIM.watchers.size)fixOnce(true);show();save()}
    // the walker: each leg at its planned moving time (times the pace), resting the planned break at each stop
    let last=realNow(),lastEmit=0;
    setInterval(()=>{
      const now=realNow(),dtMin=(now-last)/60000*SIM.rate;last=now;
      if(SIM.playing&&SIM.m<TOTAL){
        let left=dtMin;
        while(left>0&&SIM.m<TOTAL){
          if(SIM.pause>0){const p=Math.min(SIM.pause,left);SIM.pause-=p;left-=p;continue}
          const i=legOf(SIM.m),a=T.cd[SIDX[i-1]],b=T.cd[SIDX[i]],v=(b-a)/Math.max(1,ST[i].mv*SIM.pace);   // m per minute
          const need=(b-SIM.m)/v;
          if(left>=need){SIM.m=b;left-=need;SIM.pause=i<ST.length-1?ST[i].b:0}
          else{SIM.m+=v*left;left=0}
        }
        if(SIM.m>=TOTAL){SIM.m=TOTAL;SIM.playing=false}
      }
      if(SIM.watchers.size&&now-lastEmit>=3000){SIM.emit();lastEmit=now}   // a GPS left on keeps reporting, walking or not
      if(armed===null)update();
      show();save();
    },1000);
    $('splay').onclick=()=>{SIM.playing=!SIM.playing;
      if(SIM.playing){watchStart();const w=$('watchchk');if(w)w.checked=true}
      show()};
    $('srate').onchange=e=>{SIM.setRate(+e.target.value);save()};
    $('space').onchange=e=>{SIM.pace=+e.target.value;save()};
    $('soff').onchange=e=>{SIM.off=+e.target.value;moved()};
    $('skm').oninput=e=>{SIM.playing=false;SIM.pause=0;SIM.m=+e.target.value;show()};
    $('skm').onchange=()=>moved();
    $('schips').onclick=e=>{const b=e.target.closest('button[data-i]');if(!b)return;SIM.playing=false;SIM.pause=0;SIM.m=T.cd[SIDX[+b.dataset.i]];moved()};
    $('sreset').onclick=restart;
    $('smin').onclick=()=>{d.classList.toggle('small');$('smin').textContent=d.classList.contains('small')?'More':'Hide'};
    show();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build);else build();
})();

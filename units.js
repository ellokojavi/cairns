// Units for every number a person reads: 'metric' (km, m, °C, km/h) or 'us' (mi, ft, °F, mph).
// The route data and every calculation stay metric; only what is shown changes. Shared by the
// route picker and the planner; the choice is kept in localStorage ('cairns-units').
"use strict";
(function(){
  let sys='metric';try{sys=localStorage.getItem('cairns-units')==='us'?'us':'metric'}catch(e){}
  const MI=1609.344,FT=3.28084,n=v=>Math.round(v).toLocaleString('en-US');
  const U=self.U={
    get us(){return sys==='us'},
    set(s){sys=s==='us'?'us':'metric';try{localStorage.setItem('cairns-units',sys)}catch(e){}},
    dU:()=>U.us?'mi':'km', eU:()=>U.us?'ft':'m', tU:()=>U.us?'°F':'°C',
    num:(m,d=1)=>(U.us?m/MI:m/1000).toFixed(d),                  // a distance in km or mi, number only
    dist:(m,d=1)=>U.num(m,d)+' '+U.dU(),                           // 12.2 km / 7.6 mi
    at:(m,d=2)=>(U.us?'mile ':'km ')+U.num(m,d),                    // a point along the route: km 4.47 / mile 2.78
    near:m=>U.us?(m<0.2*MI?n(m*FT)+' ft':(m/MI).toFixed(2)+' mi'):(m<950?n(m)+' m':(m/1000).toFixed(2)+' km'),   // how far to the next stop
    loose:m=>U.us?(m>=10*MI?(m/MI).toFixed(0)+' mi':m>=0.5*MI?(m/MI).toFixed(1)+' mi':n(m*FT)+' ft')
                 :(m>=10000?(m/1000).toFixed(0)+' km':m>=1000?(m/1000).toFixed(1)+' km':n(m)+' m'),               // off-route distances
    h:m=>n(U.us?m*FT:m),                                           // a height or a climb, number only
    elev:m=>U.h(m)+' '+U.eU(),                                     // 1,474 m / 4,836 ft
    t:c=>Math.round(U.us?c*9/5+32:c),                              // a temperature, number only
    temp:c=>U.t(c)+' '+U.tU(),
    speed:k=>U.us?Math.round(k/1.609344)+' mph':Math.round(k)+' km/h',
    snow:cm=>U.us?(cm/2.54).toFixed(1)+' in':cm.toFixed(1)+' cm',
    // the km / mi switch: a two-button control that marks the current system
    control:onChange=>{const d=document.createElement('div');d.className='units';d.setAttribute('role','group');d.setAttribute('aria-label','Units');
      d.innerHTML='<button type="button" data-u="metric" title="Kilometres, metres, °C">km</button><button type="button" data-u="us" title="Miles, feet, °F">mi</button>';
      const mark=()=>d.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.u==='us')===U.us)));mark();
      d.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||(b.dataset.u==='us')===U.us)return;U.set(b.dataset.u);mark();onChange()});
      return d}
  };
})();

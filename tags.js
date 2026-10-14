// The labels every hike gets, in one place so the route list, its filters, the cover pills and the
// planner's header always agree: difficulty, distance, time and highlights. Loaded after units.js
// and routes/catalog.js.
"use strict";
// Difficulty from effort: km + climb/100 (a kilometre on the flat ≈ 100 m of climb). Under 13 easy, under 19 medium.
function DIFF(h){const e=h.km+h.up/100;return e<13?'easy':e<19?'medium':'hard'}
const DIFF_NAME={easy:'Easy',medium:'Medium',hard:'Hard'};
const FILTERS=[
  {id:'dist',name:'Distance',opts:[['short','Short',h=>h.km<8,()=>'under '+U.dist(8000)],['medium','Medium',h=>h.km>=8&&h.km<12,()=>U.num(8000)+'–'+U.dist(12000)],['long','Long',h=>h.km>=12&&h.km<20,()=>U.num(12000)+'–'+U.dist(20000)],['vlong','Very long',h=>h.km>=20,()=>U.dist(20000)+' +']]},
  {id:'diff',name:'Difficulty',opts:[['easy','Easy',h=>DIFF(h)==='easy'],['medium','Medium',h=>DIFF(h)==='medium'],['hard','Hard',h=>DIFF(h)==='hard']]},
  {id:'time',name:'Time',opts:[['t4','Under 4 h',h=>h.moving+h.breaks<240],['t6','4–6 h',h=>h.moving+h.breaks>=240&&h.moving+h.breaks<360],['t9','6 h +',h=>h.moving+h.breaks>=360]]},
  {id:'pass',name:'Pass',opts:[['discover','Discover Pass',h=>h.pass==='discover'],['nwfp','NW Forest Pass',h=>h.pass==='nwfp']]},
  {id:'hl',name:'Highlight',opts:[['summit','Summit',h=>(h.hl||[]).includes('summit')],['waterfall','Waterfall',h=>(h.hl||[]).includes('waterfall')],['lakes','Lakes',h=>(h.hl||[]).includes('lakes')]]},
];
// the same groups as the filters, so a card says why it shows up: difficulty, distance, time, highlights
function coverPills(h){
  const pick=id=>FILTERS.find(f=>f.id===id).opts.filter(o=>o[2](h));
  const d=DIFF(h),dist=pick('dist')[0],time=pick('time')[0];
  const DIST_ON_COVER={medium:'Mid-length'};   // "Medium" alone would read as the difficulty
  return [`<span class="chip"><i class="${d}"></i>${DIFF_NAME[d]}</span>`,
    dist&&`<span class="chip">${DIST_ON_COVER[dist[0]]||dist[1]}</span>`,
    time&&`<span class="chip">${time[1]}</span>`,
    ...pick('hl').map(o=>`<span class="chip">${o[1]}</span>`),
    h.done&&`<span class="chip done">✓ ${h.done}</span>`].filter(Boolean).join('');
}

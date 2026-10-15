// Cairns (hike planner) - offline cache. Every route in routes/catalog.js is stored on install.
const BUILD='2026-10-15 22:45';
const CACHE='hike-'+BUILD;
importScripts('./routes/catalog.js');
const CORE=['./','./index.html','./planner.html','./sim.js','./units.js','./tags.js','./manifest.webmanifest','./cairns-icon-192.png','./cairns-icon-512.png','./cairns-maskable-192.png','./cairns-maskable-512.png','./cairns-apple-180.png','./logo.png','./logo-dark.png','./favicon.png','./routes/catalog.js','./routes/overview.webp']
  .concat(self.HIKES.flatMap(h=>h.assets.concat([h.cover,h.file])).map(u=>'./'+u))
  .filter((u,i,a)=>a.indexOf(u)===i);
self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(CORE.map(u=>c.add(new Request(u,{cache:'reload'}))))));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('message',e=>{if(e.data==='version')e.source.postMessage({build:BUILD})});
self.addEventListener('fetch',e=>{
  const r=e.request;
  if(r.method!=='GET')return;
  if(new URL(r.url).searchParams.has('live'))return;   // freshness probe: always go to the network
  e.respondWith(
    caches.match(r,{ignoreSearch:true}).then(hit=>{
      if(hit){
        fetch(r).then(res=>{if(res&&res.ok)caches.open(CACHE).then(c=>c.put(r,res.clone()))}).catch(()=>{});
        return hit;
      }
      return fetch(r).then(res=>{
        if(res&&res.ok&&new URL(r.url).origin===location.origin)
          caches.open(CACHE).then(c=>c.put(r,res.clone()));
        return res;
      }).catch(()=>caches.match('./index.html',{ignoreSearch:true}));
    })
  );
});

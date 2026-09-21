// Enchantments planner - offline cache
const BUILD='2026-09-21 14:50';
const CACHE='ench-'+BUILD;
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
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

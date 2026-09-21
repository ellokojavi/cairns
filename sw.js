// Enchantments planner - offline cache
const CACHE='ench-2026-09-22-v1';
const CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>{
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(CORE.map(u=>c.add(u)))));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  const r=e.request;
  if(r.method!=='GET')return;
  e.respondWith(
    caches.match(r,{ignoreSearch:true}).then(hit=>{
      if(hit){ // refresh in the background while serving the cached copy
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

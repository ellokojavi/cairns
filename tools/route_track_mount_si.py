import pyarrow.parquet as pq, shapely.wkb as w, networkx as nx, math, json, rasterio, numpy as np
from pyproj import Transformer
G=nx.Graph()
key=lambda c:(round(c[0],7),round(c[1],7))
for r in pq.read_table('seg.parquet').to_pylist():
  n=(r['names'] or {}).get('primary') or r['class']
  if r['class'] not in ('path','footway','track','steps','service','unclassified','residential'): continue
  cs=list(w.loads(r['geometry']).coords)
  for a,b in zip(cs,cs[1:]): G.add_edge(key(a),key(b),d=math.hypot((a[0]-b[0])*75300,(a[1]-b[1])*111200),name=n)
H=nx.Graph([(u,v,d) for u,v,d in G.edges(data=True) if d['name']=='Mount Si Trail'])
deg=[n for n in H if H.degree(n)==1]
TH=min(deg,key=lambda n:n[1]); END=max(deg,key=lambda n:n[1])
print('TH',TH,'END',END)
p=nx.shortest_path(H,TH,END,weight='d')
def dens(p,step=5):
  o=[p[0]]
  for a,b in zip(p,p[1:]):
    d=math.hypot((a[0]-b[0])*75300,(a[1]-b[1])*111200);k=max(1,int(d//step))
    o+=[(a[0]+(b[0]-a[0])*i/k,a[1]+(b[1]-a[1])*i/k) for i in range(1,k+1)]
  return o
q=dens(p);tr=Transformer.from_crs(4326,26910,always_xy=True);xy=[tr.transform(*c) for c in q]
dem=rasterio.open('dem2m.tif');el=np.array([v[0] for v in dem.sample(xy)])
d=np.concatenate([[0],np.cumsum(np.hypot(np.diff([a for a,b in xy]),np.diff([b for a,b in xy])))])
print(f'one-way {d[-1]:.0f} m, {el[0]:.0f} -> {el.max():.0f} (end {el[-1]:.0f})')
for e in (400,600,700,900,1000,1100,1150): print(' el',e,'at km',round(d[np.argmax(el>=e)]/1000,2))
json.dump({'ll':q,'el':el.tolist(),'d':d.tolist()},open('si_oneway.json','w'))
# Old Si trail junction / Snag Flats / Haystack
for nm in ['Old Si Trail','Mount Teneriffe Trail']:
  for n in H:
    if any(G[n][m]['name']==nm for m in G[n]): 
      k=min(range(len(q)),key=lambda i:math.hypot((q[i][0]-n[0])*75300,(q[i][1]-n[1])*111200));print(nm,'joins at km',round(d[k]/1000,2),round(el[k]))

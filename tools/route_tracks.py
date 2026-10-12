import pickle, networkx as nx, rasterio, numpy as np, json, math
from pyproj import Transformer
G=pickle.load(open('G.pkl','rb'))
TH=(-121.6726182, 47.4660155); SUM=(-121.6392795, 47.4624091)
def path(allowed,pen={}):
  H=nx.Graph()
  for u,v,d in G.edges(data=True):
    if d['name'] in allowed: H.add_edge(u,v,w=d['d']*pen.get(d['name'],1),**d)
  p=nx.shortest_path(H,TH,SUM,weight='w')
  return p,[H[a][b]['name'] for a,b in zip(p,p[1:])]
new,nn=path({'Mailbox Peak Trail'})
old,on=path({'Mailbox Peak Old Trail','Mailbox Peak Trail','Grouse Ridge way'},{'Mailbox Peak Trail':3})
dem=rasterio.open('dem2m.tif'); tr=Transformer.from_crs(4326,26910,always_xy=True)
def densify(p,step=5):
  out=[p[0]]
  for a,b in zip(p,p[1:]):
    d=math.hypot((a[0]-b[0])*75300,(a[1]-b[1])*111200); k=max(1,int(d//step))
    for i in range(1,k+1): out.append((a[0]+(b[0]-a[0])*i/k,a[1]+(b[1]-a[1])*i/k))
  return out
for nm,p,names in [('new',new,nn),('old',old,on)]:
  from itertools import groupby
  print(nm,[(k,len(list(g))) for k,g in groupby(names)])
  q=densify(p)
  xy=[tr.transform(*c) for c in q]
  el=np.array([v[0] for v in dem.sample(xy)])
  d=np.concatenate([[0],np.cumsum(np.hypot(np.diff([a for a,b in xy]),np.diff([b for a,b in xy])))])
  # gain with 3m hysteresis
  up=dn=0;ref=el[0]
  for e in el:
    if e-ref>3: up+=e-ref;ref=e
    elif ref-e>3: dn+=ref-e;ref=e
  print(f'  one-way {d[-1]:.0f} m, start {el[0]:.0f} max {el.max():.0f} at {np.argmax(el)}/{len(el)} end {el[-1]:.0f} up {up:.0f} dn {dn:.0f}')
  json.dump({'ll':q,'el':el.tolist(),'d':d.tolist()},open(f'{nm}_oneway.json','w'))
# summit check
w=rasterio.windows.from_bounds(*[*tr.transform(-121.645,47.458),*tr.transform(-121.632,47.468)],dem.transform)
a=dem.read(1,window=w); i=np.unravel_index(a.argmax(),a.shape)
x,y=rasterio.windows.transform(w,dem.transform)*(i[1],i[0]); print('dem max near summit',a.max(),Transformer.from_crs(26910,4326,always_xy=True).transform(x,y))

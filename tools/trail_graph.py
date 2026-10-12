import pyarrow.parquet as pq, shapely.wkb as w, networkx as nx, json, math
t=pq.read_table('seg.parquet').to_pylist()
G=nx.Graph(); names={}
def key(c): return (round(c[0],7),round(c[1],7))
for r in t:
  if r['class'] not in ('path','footway','track','steps','service','unclassified','residential'): continue
  g=w.loads(r['geometry']); cs=list(g.coords)
  n=(r['names'] or {}).get('primary') or r['class']
  for a,b in zip(cs,cs[1:]):
    d=math.hypot((a[0]-b[0])*75300,(a[1]-b[1])*111200)
    G.add_edge(key(a),key(b),d=d,name=n,cls=r['class'])
print(G.number_of_nodes())
import pickle; pickle.dump(G,open('G.pkl','wb'))
# candidate endpoints
for n in ['Mailbox Peak Parking lot','Mailbox Peak Trail','Mailbox Peak Old Trail','Mailbox south trail']:
  es=[(u,v) for u,v,d in G.edges(data=True) if d['name']==n]
  deg={}
  for u,v in es:
    deg[u]=deg.get(u,0)+1; deg[v]=deg.get(v,0)+1
  ends=[k for k,v in deg.items() if v==1]
  print(n,[(k,G.degree(k)) for k in ends])
  print('  junctions',[(k,G.degree(k),set(G[k][x]['name'] for x in G[k])) for k in deg if G.degree(k)>2])

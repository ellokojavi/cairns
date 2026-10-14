"""Trailhead-to-goal track over the OpenStreetMap trail network, with lidar elevations.

  python3 route_track.py <name> <start lon> <start lat> <end lon> <end lat> "<Trail A>,<Trail B>"
Reads seg.parquet and dem2m.tif in the current folder, writes <name>_oneway.json (the input of
routekit.roundtrip). The path prefers the listed trails (and short unnamed connectors); any
other way costs 6x, so the route only leaves the named trails where the map leaves no choice.
"""
import sys, math, json, itertools
import pyarrow.parquet as pq, shapely.wkb as w, networkx as nx, rasterio, numpy as np
from pyproj import Transformer
nm = sys.argv[1]; A = tuple(map(float, sys.argv[2:4])); B = tuple(map(float, sys.argv[4:6]))
pref = set(sys.argv[6].split(','))
G = nx.Graph(); key = lambda c: (round(c[0], 7), round(c[1], 7))
dist = lambda a, b: math.hypot((a[0] - b[0]) * 75300, (a[1] - b[1]) * 111200)
for r in pq.read_table('seg.parquet').to_pylist():
    c = r['class']
    if c not in ('path', 'footway', 'track', 'steps', 'service', 'unclassified', 'residential', 'bridleway', 'cycleway'): continue
    n = (r['names'] or {}).get('primary') or ''
    k = 1 if n in pref else 1.5 if not n and c in ('path', 'footway', 'steps') else 6
    cs = list(w.loads(r['geometry']).coords)
    for a, b in zip(cs, cs[1:]): G.add_edge(key(a), key(b), d=dist(a, b), w=dist(a, b) * k, name=n or c)
s = min(G, key=lambda n: dist(n, A)); e = min(G, key=lambda n: dist(n, B))
print('snap start', round(dist(s, A)), 'm, end', round(dist(e, B)), 'm')
p = nx.shortest_path(G, s, e, weight='w')
print([(k, round(sum(G[a][b]['d'] for a, b in g))) for k, g in itertools.groupby(zip(p, p[1:]), key=lambda ab: G[ab[0]][ab[1]]['name'])])
q = [p[0]]
for a, b in zip(p, p[1:]):
    k = max(1, int(dist(a, b) // 5)); q += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
tr = Transformer.from_crs(4326, 26910, always_xy=True); xy = [tr.transform(*c) for c in q]
el = np.array([v[0] for v in rasterio.open('dem2m.tif').sample(xy)])
d = np.concatenate([[0], np.cumsum(np.hypot(np.diff([a for a, b in xy]), np.diff([b for a, b in xy])))])
print(f'one-way {d[-1]:.0f} m, {el[0]:.0f} -> max {el.max():.0f} (end {el[-1]:.0f})')
for km in np.arange(0, d[-1] / 1000, 0.5): i = int(np.argmin(abs(d - km * 1000))); print(f'  km {km:.1f}: {el[i]:.0f} m  {q[i][1]:.5f},{q[i][0]:.5f}')
json.dump({'ll': q, 'el': el.tolist(), 'd': d.tolist()}, open(f'{nm}_oneway.json', 'w'))

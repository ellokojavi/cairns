"""Shared helpers for the route builders (tools/build_*.py).

A one-way track (trailhead to top, lon/lat + lidar elevation) becomes the planner's
round trip: simplified, encoded, timed leg by leg, traced onto the rendered map and
written out as a milestone GPX.
"""
import json, math
import numpy as np
from pyproj import Transformer
from shapely.geometry import LineString

fw = Transformer.from_crs(4326, 26910, always_xy=True)

def roundtrip(path):
    j = json.load(open(path))
    ll, el = j['ll'], j['el']
    xy = [fw.transform(*c) for c in ll]
    # keep the shape to within 2.5 m, but never more than 40 m between points
    keep = set()
    simp = LineString(xy).simplify(2.5, preserve_topology=False)
    sx = {(round(x, 3), round(y, 3)) for x, y in simp.coords}
    last = -1e9; cum = 0
    for i in range(len(xy)):
        if i: cum += math.dist(xy[i - 1], xy[i])
        if (round(xy[i][0], 3), round(xy[i][1], 3)) in sx or cum - last >= 40 or i in (0, len(xy) - 1):
            keep.add(i); last = cum
    idx = sorted(keep)
    up = [(ll[i][1], ll[i][0], el[i], xy[i]) for i in idx]
    pts = up + up[-2::-1]              # summit once, then the same line back down
    cd = [0.0]
    for a, b in zip(pts, pts[1:]): cd.append(cd[-1] + math.dist(a[3], b[3]))
    return pts, cd

def encode(pts, cd):
    cols = [[round(p[0] * 1e5) for p in pts], [round(p[1] * 1e5) for p in pts],
            [round(p[2]) for p in pts], [round(c) for c in cd]]
    out = []
    for c in cols:
        out.append(','.join(str(v - (c[i - 1] if i else 0)) for i, v in enumerate(c)))
    return '|'.join(out)

def gain(el):
    up = dn = 0; ref = el[0]
    for e in el:
        if e - ref > 3: up += e - ref; ref = e
        elif ref - e > 3: dn += ref - e; ref = e
    return round(up), round(dn)

# leg time model, calibrated on the Enchantments plan the group walked:
# 5 km/h on the flat, +700 m/h climbing, descent costs more the steeper it gets
def leg_minutes(pts, cd, a, b):
    t = 0.0
    for k in range(a, b):
        d = cd[k + 1] - cd[k]; dz = pts[k + 1][2] - pts[k][2]
        g = abs(dz) / d if d else 0
        t += d / 5000 * 60
        if dz > 0: t += dz / 700 * 60
        else: t += -dz / (900 if g > .30 else 1500 if g > .15 else 3000) * 60
    return round(t / 5) * 5

def at_km(cd, km):
    return int(np.argmin(np.abs(np.array(cd) - km * 1000)))

def at_ele(pts, cd, e, after=0, before=None):
    rng = range(after, before if before is not None else len(pts))
    return min(rng, key=lambda k: abs(pts[k][2] - e))

def summit_idx(pts):
    return int(np.argmax([p[2] for p in pts]))

def pixel(p, frame):
    x, y = p[3]
    return ((x - frame['X0']) / frame['MPP'], (frame['Y1'] - y) / frame['MPP'])

def map_pts(pts, si, frame):
    """Pixel trace for the map overlay: one point every ~8 px, every stop kept and tagged."""
    out = []; last = None; stops = {k: i for i, k in enumerate(si)}
    for k, p in enumerate(pts):
        x, y = pixel(p, frame)
        if k in stops:
            out.append([round(x), round(y), stops[k]]); last = (x, y); continue
        if last is None or math.dist(last, (x, y)) >= 8:
            out.append([round(x), round(y)]); last = (x, y)
    return out

def gpx(name, desc, pts, si, stops):
    w = []
    for i, k in enumerate(si):
        p = pts[k]; s = stops[i]
        w.append(f'  <wpt lat="{p[0]:.6f}" lon="{p[1]:.6f}">\n    <ele>{p[2]:.1f}</ele>\n'
                 f'    <name>{i + 1} {s["n"]}</name>\n    <desc>{s["note"]}</desc>\n'
                 f'    <sym>Flag, Blue</sym>\n    <type>Milestone</type>\n  </wpt>')
    t = '\n'.join(f'      <trkpt lat="{p[0]:.6f}" lon="{p[1]:.6f}"><ele>{p[2]:.1f}</ele></trkpt>' for p in pts)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="Cairns hike planner" '
            f'xmlns="http://www.topografix.com/GPX/1/1">\n  <metadata>\n    <name>{name}</name>\n'
            f'    <desc>{desc}</desc>\n  </metadata>\n' + '\n'.join(w) +
            f'\n  <trk>\n    <name>{name}</name>\n    <trkseg>\n{t}\n    </trkseg>\n  </trk>\n</gpx>\n')


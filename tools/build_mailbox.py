"""Build the two Mailbox Peak routes (New Trail = long, Old Trail = short).

Inputs (made by the scripts in tools/README.md, kept out of the repo):
  new_oneway.json / old_oneway.json  trailhead->summit track, from OpenStreetMap
                                     (Overture Maps) with USGS 3DEP 1 m lidar elevations
  map.png, cover_new.png, cover_old.png  rendered from the same lidar
Outputs: routes/mailbox/*
"""
import json, math, sys, os
import numpy as np
from PIL import Image
from pyproj import Transformer
from shapely.geometry import LineString

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
fw = Transformer.from_crs(4326, 26910, always_xy=True)
frame = json.load(open(f'{SRC}/frame.json'))

def roundtrip(nm):
    j = json.load(open(f'{SRC}/{nm}_oneway.json'))
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

def pixel(p):
    x, y = p[3]
    return ((x - frame['X0']) / frame['MPP'], (frame['Y1'] - y) / frame['MPP'])

def map_pts(pts, si):
    """Pixel trace for the map overlay: one point every ~8 px, every stop kept and tagged."""
    out = []; last = None; stops = {k: i for i, k in enumerate(si)}
    for k, p in enumerate(pts):
        x, y = pixel(p)
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
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="Hike planner" '
            f'xmlns="http://www.topografix.com/GPX/1/1">\n  <metadata>\n    <name>{name}</name>\n'
            f'    <desc>{desc}</desc>\n  </metadata>\n' + '\n'.join(w) +
            f'\n  <trk>\n    <name>{name}</name>\n    <trkseg>\n{t}\n    </trkseg>\n  </trk>\n</gpx>\n')

COMMON_TEXT = {
    'turn': "Turn around here if you are not here by {lim}: the summit and the whole descent still have to fit before the parking gate closes. {rel}",
    'turnDone': ["Arrived after the {lim} cutoff. Go down now unless everyone is moving well; the car is behind a gate.",
                 "Arrived {ahead} before the cutoff."],
    'twilight': 'Headlamps out before the last kilometre of forest; it gets dark under the trees first.',
    'gpsHint': '<b>Keep GPS on</b> only in the boulder field and around the summit, where boot paths split, and in fog.',
}

ROUTES = {
 'new': dict(
  id='mailbox-new', title='Mailbox Peak', variant='New Trail', size='long',
  blurb='The graded trail: long, steady switchbacks through forest, then one steep, rocky kilometre to the mailbox.',
  stops=lambda pts, cd, S: [
   (0, dict(n='Trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
     note='Discover Pass on the dashboard. Carry all your water: 2 L each, there is no reliable source on the trail. Headlamp in the pack, whatever the plan says.')),
   (at_ele(pts, cd, 600, 0, S), dict(n='Switchbacks, 600 m', b=5, pace=True,
     note='Steady grade in tall forest. Settle into a pace you could hold all day; this is a quarter of the climb.')),
   (at_ele(pts, cd, 870, 0, S), dict(n='Halfway up, 870 m', b=10, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
     note='Half the height is done. Eat something now, not at the top.')),
   (at_km(cd, 7.214), dict(n='Old Trail junction', b=5, gate='turn', wind=True,
     note='The trails merge for the last 0.8 km and 250 m. Trees thin out, then the boulder field: steep and rocky, with built steps. Layer up before it, not on it.')),
   (S, dict(n='Summit, the mailbox', b=20, wind=True, take=[['gel', 'Lunch']],
     note='Sign the register in the mailbox. Rainier is to the south on a clear day. Dry layer and shell on before you sit down; wind is the norm here.')),
   (len(pts) - 1 - at_km(cd, 7.214), dict(n='Old Trail junction (down)', b=5,
     note='Keep LEFT onto the New Trail. The Old Trail drops straight down the ridge; it is 4 km shorter but brutal on knees.')),
   (len(pts) - 1 - at_ele(pts, cd, 870, 0, S), dict(n='Halfway down, 870 m', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
     note='Half the descent done. Quick stop; legs stay warmer moving.')),
   (len(pts) - 1, dict(n='Trailhead', b=0, note='Finish. Back at the car.')),
  ]),
 'old': dict(
  id='mailbox-old', title='Mailbox Peak', variant='Old Trail', size='short',
  blurb='The original route straight up the ridge: half the distance, the same climb. Roots, mud and 40% grades.',
  stops=lambda pts, cd, S: [
   (0, dict(n='Trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
     note='Discover Pass on the dashboard. Carry all your water: 2 L each. Poles help a lot on this trail, mostly on the way down.')),
   (at_km(cd, 0.394), dict(n='Old Trail sign', b=0,
     note='Leave the gravel road here for the Old Trail. From now on it barely lets up: no switchbacks, root steps up to knee height.')),
   (at_ele(pts, cd, 870, 0, S), dict(n='Halfway up, 870 m', b=10, pace=True, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
     note='Half the height in 2 km. Average grade so far is over 30%. Eat now.')),
   (at_km(cd, 2.994), dict(n='New Trail junction', b=5, gate='turn', wind=True,
     note='The New Trail joins from the left. Last 0.8 km and 250 m: the boulder field, with built steps. Layer up before it.')),
   (S, dict(n='Summit, the mailbox', b=20, wind=True, take=[['gel', 'Lunch']],
     note='Sign the register in the mailbox. Dry layer and shell before you sit. Decide here: down the Old Trail (2 h, steep), or the New Trail (+4.2 km, about 30 min longer, far kinder to knees).')),
   (len(pts) - 1 - at_km(cd, 2.994), dict(n='New Trail junction (down)', b=5,
     note='Straight on for the Old Trail. Shorten poles, small steps, face in on the root steps. Most injuries here happen going down.')),
   (len(pts) - 1 - at_ele(pts, cd, 870, 0, S), dict(n='Halfway down, 870 m', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
     note='Half the descent. Knees and quads: slow is fine, falls are not.')),
   (len(pts) - 1 - at_km(cd, 0.394), dict(n='Old Trail sign (down)', b=0,
     note='Back on the gravel road. Ten easy minutes to the car.')),
   (len(pts) - 1, dict(n='Trailhead', b=0, note='Finish. Back at the car.')),
  ]),
}

catalog = []
for nm, R in ROUTES.items():
    pts, cd = roundtrip(nm)
    S = summit_idx(pts)
    plan = R['stops'](pts, cd, S)
    si = [k for k, _ in plan]
    assert si == sorted(si) and len(set(si)) == len(si), si
    stops = []
    for i, (k, s) in enumerate(plan):
        s = dict(s); s['mv'] = 0 if i == 0 else leg_minutes(pts, cd, si[i - 1], k)
        stops.append(s)
    up, dn = gain([p[2] for p in pts])
    km = cd[-1] / 1000; hi = max(p[2] for p in pts)
    mv = sum(s['mv'] for s in stops); br = sum(s['b'] for s in stops[:-1])
    print(nm, f'{km:.2f} km +{up} -{dn} hi {hi:.0f}, {len(pts)} pts, moving {mv//60}:{mv%60:02d} breaks {br}', [s['mv'] for s in stops])
    route = dict(
        id=R['id'], title=R['title'], variant=R['variant'], size=R['size'],
        place='Middle Fork Snoqualmie, near North Bend, WA',
        summary=f"Mailbox Peak trailhead to the summit and back by the {R['variant']}. {km:.1f} km, +{up:,} m, −{dn:,} m.",
        lat=round(pts[0][0], 5), lon=round(pts[0][1], 5),
        dep='08:30', climate=dict(ref=270, low=7, high=15),
        deadline=dict(kind='gate', label='parking gate', dusk=-60),
        trk=encode(pts, cd), si=si, stops=stops,
        tz='America/Los_Angeles',
        map=dict(src='routes/mailbox/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si), route=True,
                 credit='Map and cover: terrain from USGS 3DEP 1 m lidar (King County 2021), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
        gpx=f'routes/mailbox/{R["id"]}.gpx', cover=f'routes/mailbox/cover-{nm}.webp',
        text=COMMON_TEXT,
    )
    with open(f'{OUT}/{nm}.js', 'w') as f:
        f.write('// generated by tools/build_mailbox.py — edit the generator, not this file\n')
        f.write('window.ROUTE=' + json.dumps(route, ensure_ascii=False, separators=(',', ':')) + ';\n')
    with open(f'{OUT}/{R["id"]}.gpx', 'w') as f:
        f.write(gpx(f'Mailbox Peak, {R["variant"]}', route['summary'], pts, si, stops))
    catalog.append(dict(id=R['id'], km=round(km, 1), up=up, hi=round(hi), moving=mv, breaks=br, blurb=R['blurb']))
    Image.open(f'{SRC}/cover_{nm}.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(f'{OUT}/cover-{nm}.webp', quality=78, method=6)
Image.open(f'{SRC}/map.png').convert('RGB').save(f'{OUT}/map.webp', quality=82, method=6)
print(json.dumps(catalog, indent=1))

"""Build Little Bandera Mountain (Ira Spring Trail, then the Bandera Mountain Trail; out and back).

Inputs, in a scratch folder (see tools/README.md): lb_oneway.json (trailhead to the top of
Little Bandera, OpenStreetMap via Overture, USGS 3DEP 1 m lidar elevations), frame.json and
map.png from render_map.py (map-config-little-bandera.json), cover_lb.png from render_cover.py,
and the photo candidates in tools/photo-candidates/little-bandera/.
Outputs: routes/little-bandera/*
"""
import json, os, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routekit import roundtrip, encode, gain, leg_minutes, at_km, at_ele, summit_idx, map_pts, gpx

SRC, OUT, CAND = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f'{OUT}/photos', exist_ok=True)
frame = json.load(open(f'{SRC}/frame.json'))
pts, cd = roundtrip(f'{SRC}/lb_oneway.json')
S = summit_idx(pts)
back = lambda k: len(pts) - 1 - k

LIC = {'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0', 'CC BY 2.0': 'https://creativecommons.org/licenses/by/2.0'}
def ph(n, f, caption, author, lic, commons):
    im = Image.open(f'{CAND}/{n}.jpg').convert('RGB'); im.thumbnail((1024, 1024), Image.LANCZOS)
    im.save(f'{OUT}/photos/{f}.webp', quality=78, method=6)
    return [f'routes/little-bandera/photos/{f}.webp', f"{caption}<br><span class='cred'>Photo: {author} &middot; "
            f"<a href='{LIC[lic]}' target='_blank' rel='noopener'>{lic}</a> &middot; "
            f"<a href='https://commons.wikimedia.org/wiki/File:{commons}' target='_blank' rel='noopener'>source</a></span>"]
P = dict(
    pratt=ph('034', 'bandera-from-pratt', 'Bandera Mountain from Pratt Mountain to the east: Little Bandera is the shoulder at the west (left) end of the ridge', 'Buidhe', 'CC BY-SA 4.0',
             'Bandera_from_Pratt_Mountain.jpg'),
    kaleetan=ph('020', 'kaleetan-from-trail', 'Kaleetan Peak from the Bandera Mountain Trail, on the open slope above the junction', 'Ron Clausen', 'CC BY-SA 4.0',
                'Kaleetan_Peak_from_Bandera.jpg'),
    top=ph('061', 'from-little-bandera', 'From the top of Little Bandera: Mount Roosevelt and Kaleetan Peak to the north', 'Martin Bravenboer', 'CC BY 2.0',
           'Roosevelt_and_Kaleetan_from_Little_Bandera.jpg'),
    chair=ph('019', 'chair-peak', 'Chair Peak to the northeast, from the Bandera ridge in early July', 'Ron Clausen', 'CC BY-SA 4.0', 'Chair_Peak_from_Bandera.jpg'),
    lakes=ph('038', 'lakes-below', 'Bandera and Mount Defiance above Mason Lake basin (seen from Pratt Mountain); the lakes sit just north of the summit ridge', 'Buidhe', 'CC BY-SA 4.0',
             'Bandera_and_Defiance_from_Pratt%27s_scree_field.jpg'),
    winter=ph('022', 'bandera-winter', 'Bandera in winter: the open south slope holds snow late, and avalanches on it in winter', 'Peter Stevens', 'CC BY 2.0', 'Bandera_Mountain_winter.jpg'),
)
cov = ImageOps.fit(Image.open(f'{CAND}/018.jpg').convert('RGB'), (960, 540), Image.LANCZOS, centering=(0.5, 0.4))
cov.save(f'{OUT}/cover-photo.webp', quality=78, method=6)
Image.open(f'{SRC}/cover_lb.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(f'{OUT}/cover-3d.webp', quality=78, method=6)
Image.open(f'{SRC}/map.png').convert('RGB').save(f'{OUT}/map.webp', quality=82, method=6)

OLD = at_km(cd, 1.38); OPEN = at_ele(pts, cd, 1000, 0, S); JCT = at_km(cd, 4.43)
plan = [
 (0, dict(n='Ira Spring trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
   note='Northwest Forest Pass (or an Interagency pass) on the dashboard. Vault toilet, no water. The last miles of FR 9031 are potholed gravel; the lot fills early on summer and autumn weekends. Carry 2 L each: the creek near the start is the only water.')),
 (OLD, dict(n='Old Mason Lake Trail junction', b=5, pace=True,
   note='The old trail splits off here; stay on the Ira Spring Trail. So far it has been an old roadbed at a steady 10–13%, past the Mason Creek crossing.')),
 (OPEN, dict(n='Out of the trees, 1,000 m', b=10, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
   note='Switchbacks on the open south slope: beargrass, huckleberries and the I-90 valley below. Hot in afternoon sun, no shade until the top. Eat now.')),
 (JCT, dict(n='Bandera Mountain Trail junction', b=5, gate='turn', wind=True,
   note='Leave the Ira Spring Trail (it carries on to Mason Lake) and turn right, straight up the ridge. The last 0.9 km climbs 310 m: steep, rocky, with talus near the top. Poles out.')),
 (S, dict(n='Little Bandera summit', b=20, wind=True, take=[['gel', 'Lunch']],
   note='Rainier to the south, Mason Lake and the lakes basin below to the north, Kaleetan and Chair Peak beyond. The true Bandera summit is about 1 km east along the ridge (+60 m, boulder hopping, harder coming back). Skip it when wet, icy or short of time.')),
 (back(JCT), dict(n='Bandera junction (down)', b=0,
   note='Back on the Ira Spring Trail: go left, downhill. The branch climbing ahead goes to Mason Lake. The steep pitch above is where knees and ankles suffer; slow is fine.')),
 (back(OPEN), dict(n='Into the trees (down)', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
   note='Shade again. The rest is a steady, gentle descent on the old roadbed.')),
 (len(pts) - 1, dict(n='Ira Spring trailhead', b=0, note='Finish. Back at the car.')),
]
si = [k for k, _ in plan]
assert si == sorted(si) and len(set(si)) == len(si), si
stops = []
for i, (k, s) in enumerate(plan):
    s = dict(s); s['mv'] = 0 if i == 0 else leg_minutes(pts, cd, si[i - 1], k); stops.append(s)
up, dn = gain([p[2] for p in pts]); km = cd[-1] / 1000; hi = max(p[2] for p in pts)
mv = sum(s['mv'] for s in stops); br = sum(s['b'] for s in stops[:-1])
print(f'little-bandera {km:.2f} km +{up} -{dn} hi {hi:.0f}, {len(pts)} pts, moving {mv//60}:{mv%60:02d} breaks {br}', [s['mv'] for s in stops])

REVIEWS = dict(
    points=[
        'Two halves: a long, friendly climb on the Ira Spring Trail, then a short, very steep push up the ridge from the Bandera junction. Most of the effort is in that last kilometre.',
        'The upper ridge is rocky and rooty, with talus near the top. Many say it is harder going down than up; poles help.',
        'Big views for the effort: Rainier, the I-90 corridor, and the lakes basin and Snoqualmie Pass peaks to the north.',
        'The south slope is open and sunny. Hot on summer afternoons, and it holds snow into June; early-season hikers carry microspikes.',
        'Popular on weekends, and the gravel road to the trailhead is rough but passable for most cars.',
        'Continuing to the true Bandera summit adds a short boulder scramble along the ridge; many stop at Little Bandera.',
    ],
    sources=[['WTA: Bandera Mountain', 'https://www.wta.org/go-hiking/hikes/bandera-mountain'],
             ['Mountaineers trip reports', 'https://www.mountaineers.org/activities/trip-reports/dy-hike-scramble-bandera-and-little-bandera'],
             ['SummitPost climbers log', 'https://www.summitpost.org/bandera-mountain/climbers-log/152006'],
             ['Outdoor Project', 'https://www.outdoorproject.com/united-states/washington/bandera-mountain-hike']])

route = dict(
    id='little-bandera', title='Little Bandera Mountain', variant='Ira Spring Trail', size='long',
    place='Alpine Lakes Wilderness, I-90 exit 45, WA',
    summary=f'Ira Spring trailhead to Little Bandera and back. {km:.1f} km, +{up:,} m, −{dn:,} m.',
    lat=round(pts[0][0], 5), lon=round(pts[0][1], 5), tz='America/Los_Angeles',
    date='2026-10-17', dep='07:30', climate=dict(ref=650, low=4, high=14), deadline=dict(kind='dark'),
    trk=encode(pts, cd), si=si, stops=stops,
    map=dict(src='routes/little-bandera/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si, frame), route=True,
             credit='Map and 3D view: terrain from USGS 3DEP 1 m lidar (King County 2021), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
    gpx='routes/little-bandera/little-bandera.gpx', cover='routes/little-bandera/cover-photo.webp',
    photos={0: [P['pratt'], ['routes/little-bandera/cover-3d.webp', 'The route from across the I-90 valley: the long traverse, then the steep ridge (terrain from USGS lidar, no trees drawn)']],
            2: [P['winter']], 3: [P['kaleetan']], 4: [P['top'], P['chair'], P['lakes']]},
    reviews=REVIEWS,
    text={'turn': 'Turn around here if you are not here by {lim}: the steep top and the whole descent still have to fit before dark. {rel}',
          'turnDone': ['Arrived after the {lim} cutoff. Head down now; the steep ridge is no place to be in the dark.', 'Arrived {ahead} before the cutoff.'],
          'twilight': 'Headlamps out for the forest below 1,000 m; it gets dark under the trees first.',
          'gpsHint': '<b>Keep GPS on</b> above the Bandera junction, where boot paths braid on the open ridge, and in fog.'},
)
with open(f'{OUT}/route.js', 'w') as f:
    f.write('// generated by tools/build_little_bandera.py — edit the generator, not this file\n')
    f.write('window.ROUTE=' + json.dumps(route, ensure_ascii=False, separators=(',', ':')) + ';\n')
with open(f'{OUT}/little-bandera.gpx', 'w') as f:
    f.write(gpx('Little Bandera Mountain', route['summary'], pts, si, stops))
print(json.dumps(dict(km=round(km, 1), up=up, hi=round(hi), moving=mv, breaks=br)))

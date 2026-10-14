"""Build Wallace Falls (Woody Trail from the Wallace Falls State Park trailhead to the Upper Falls; out and back).

Inputs, in a scratch folder (see tools/README.md): wal_oneway.json from route_track.py, frame.json and
map.png from render_map.py (map-config-wallace-falls.json), cover_wal.png from render_cover.py, and the
photo candidates in tools/photo-candidates/wallace-falls/.
Terrain here is the USGS 1/3 arc-second DEM (~10 m): the 2016 lidar tiles for this area are empty
(fetch_lidar_area.py 13 ...), so elevations along the canyon are good to ~10 m, not 1 m.
Outputs: routes/wallace-falls/*
"""
import json, os, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routekit import roundtrip, encode, at_km, summit_idx, map_pts, photo, timed, write

RID = 'wallace-falls'
SRC, OUT, CAND = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f'{OUT}/photos', exist_ok=True)
frame = json.load(open(f'{SRC}/frame.json'))
pts, cd = roundtrip(f'{SRC}/wal_oneway.json', smooth_m=40)
S = summit_idx(pts)
back = lambda k: len(pts) - 1 - k
ph = lambda *a: photo(CAND, OUT, RID, *a)
C = 'https://commons.wikimedia.org/wiki/File:'

P = dict(
    wires=ph('038', 'under-the-wires', 'The first stretch, under the power lines near the parking lot', 'PinchyCC', 'CC BY 4.0', C + 'Leaving_Wallace_Falls_State_Park_under_the_wires.jpg'),
    river=ph('013', 'wallace-river', 'The Wallace River from the Woody Trail', 'Joe Mabel', 'CC BY-SA 3.0', C + 'Wallace_Falls_State_Park_05.jpg'),
    lower=ph('022', 'lower-falls', 'Lower Wallace Falls, by the picnic shelter', 'Steven Pavlov', 'CC BY-SA 4.0',
             C + 'Wallace_Falls_State_Park_%E2%80%94_Lower_Wallace_Falls,_part_1.jpg'),
    middle=ph('024', 'middle-falls', 'Middle Wallace Falls, the tallest of the three, from the viewpoint', 'Steven Pavlov', 'CC BY-SA 3.0',
              C + 'Wallace_Falls_State_Park_%E2%80%94_Middle_Wallace_Falls.jpg'),
    rainbow=ph('008', 'middle-falls-rainbow', 'A double rainbow in the spray of the Middle Falls on a sunny afternoon', 'Abhinaba Basu', 'CC BY 2.0',
               C + 'Double_Rainbow_at_Wallace_middle_falls.jpg'),
    upper=ph('025', 'upper-falls', 'Upper Wallace Falls', 'Steven Pavlov', 'CC BY-SA 3.0', C + 'Wallace_Falls_State_Park_%E2%80%94_Upper_Wallace_Falls.jpg'),
    upper2=ph('004', 'upper-falls-close', 'The Upper Falls up close', 'Vineesh Devasia', 'CC BY 2.0', C + 'Wallace_Falls.jpg'),
    fog=ph('014', 'woody-trail-fog', 'The Woody Trail in fog, below the falls', 'Joe Mabel', 'CC BY-SA 3.0', C + 'Wallace_Falls_State_Park_06.jpg'),
)
COVER = ('032', 0.45)
if COVER:
    ImageOps.fit(Image.open(f'{CAND}/{COVER[0]}.jpg').convert('RGB'), (960, 540), Image.LANCZOS, centering=(0.5, COVER[1])).save(
        f'{OUT}/cover-photo.webp', quality=78, method=6)
Image.open(f'{SRC}/cover_wal.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(f'{OUT}/cover-3d.webp', quality=78, method=6)
Image.open(f'{SRC}/map.png').convert('RGB').save(f'{OUT}/map.webp', quality=82, method=6)

# on the OpenStreetMap track: Railroad Grade junction 0.63 km, Lower Falls 2.77 km,
# Middle Falls 3.57 km, top of the trail above the Upper Falls 4.14 km
RRG = at_km(cd, 0.63); LOWER = at_km(cd, 2.77); MIDDLE = at_km(cd, 3.57)
plan = [
 (0, dict(n='Wallace Falls trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
   note='State park: Discover Pass, or buy a day pass at the machine in the lot. From October the park opens at 8:00 and closes at dusk. '
        'Restrooms at the lot; carry 1–1.5 L each. About 100 spaces: full by late morning on weekends, quiet on weekdays.')),
 (RRG, dict(n='Railroad Grade junction', b=0,
   note='Under the power lines. Keep right on the Woody Trail, along the river. The Railroad Grade to the left is a gentler old logging grade, about 1.5 km longer, that rejoins before the falls.')),
 (LOWER, dict(n='Lower Falls picnic shelter', b=10, pace=True, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
   note='The first falls, with a shelter and benches. Eat now: the switchbacks above here are the steep part, about 250 m of climb in 1.4 km.')),
 (MIDDLE, dict(n='Middle Falls viewpoint', b=10, gate='turn',
   note='The big one: the tallest of the three falls, in full view. The Skykomish Valley overlook is a few switchbacks higher. '
        'Steep drop-offs at the viewpoints: stay on the trail, and keep children close.')),
 (S, dict(n='Upper Falls', b=15, take=[['gel', 'Lunch']],
   note='The top of the Woody Trail, beside the Upper Falls. The old road beyond goes on toward Wallace Lake; turn around here.')),
 (back(MIDDLE), dict(n='Middle Falls (down)', b=0,
   note='Steep, stepped trail down to the picnic shelter: slick when wet. Short steps; poles help.')),
 (back(LOWER), dict(n='Lower Falls shelter (down)', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
   note='The rest is gentle: along the river and back across the North Fork bridge.')),
 (back(RRG), dict(n='Railroad Grade junction (down)', b=0,
   note='Straight on under the power lines to the lot.')),
 (len(pts) - 1, dict(n='Wallace Falls trailhead', b=0, note='Finish. Back at the car.')),
]
si, stops, T = timed(pts, cd, plan)
print(RID, T, [s['mv'] for s in stops])

REVIEWS = dict(
    points=[
        'Three sets of falls for one moderate hike: the Lower, Middle and Upper Falls, with the Middle Falls the most impressive.',
        'Easy along the river at first; the switchbacks above the Lower Falls picnic shelter are where the work is.',
        'Best after rain, when the falls roar; in late summer they can be much thinner.',
        'Very popular: the lot fills early on weekends and Gold Bar tickets cars parked on its streets. Weekday mornings are quiet.',
        'Muddy and slick on the descent after rain; some hikers use poles. The Railroad Grade is a quieter, gentler alternative.',
        'Around 3 hours with stops for most groups; families and dogs on leash are common.',
    ],
    sources=[['WTA: Wallace Falls', 'https://www.wta.org/go-hiking/hikes/wallace-falls'],
             ['Washington State Parks', 'https://parks.wa.gov/find-parks/state-parks/wallace-falls-state-park'],
             ['Mountaineers trip report', 'https://www.mountaineers.org/activities/trip-reports/chs-2-hike-wallace-falls'],
             ['World of Waterfalls', 'https://www.world-of-waterfalls.com/pacific-northwest-wallace-falls.html']])

photos = {0: [['routes/wallace-falls/cover-3d.webp', 'The route from the southwest: along the Wallace River, then up the canyon past the three falls (terrain from USGS 3DEP 10 m, no trees drawn)']]}
for i, keys in {1: ['wires', 'river'], 2: ['lower'], 3: ['middle', 'rainbow'], 4: ['upper', 'upper2'], 6: ['fog']}.items(): photos.setdefault(i, []).extend(P[k] for k in keys)
route = dict(
    id=RID, title='Wallace Falls', variant='Woody Trail to the Upper Falls', size='medium',
    place='Wallace Falls State Park, Gold Bar, WA',
    summary=f"Wallace Falls trailhead to the Upper Falls and back. {T['km']:.1f} km, +{T['up']:,} m, −{T['dn']:,} m.",
    lat=round(pts[0][0], 5), lon=round(pts[0][1], 5), tz='America/Los_Angeles',
    date='2026-10-15', dep='09:00', climate=dict(ref=100, low=8, high=19),
    deadline=dict(kind='gate', label='park gate', dusk=0, open='08:00'),
    trk=encode(pts, cd), si=si, stops=stops,
    map=dict(src=f'routes/{RID}/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si, frame), route=True,
             credit='Map and 3D view: terrain from USGS 3DEP 1/3 arc-second (~10 m), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
    gpx=f'routes/{RID}/{RID}.gpx', cover=f'routes/{RID}/cover-photo.webp',
    photos=photos, reviews=REVIEWS,
    text={'turn': 'Turn around here if you are not here by {lim}: the Upper Falls and the whole descent still have to fit before the park closes at dusk. {rel}',
          'turnDone': ['Arrived after the {lim} cutoff. Head down now; the park closes at dusk.', 'Arrived {ahead} before the cutoff.'],
          'twilight': 'Headlamps out; the canyon gets dark first.',
          'gpsHint': '<b>GPS can stay off</b>: the trail is signed with mileposts every half mile. Turn it on only if you take the Railroad Grade.'},
)
write(OUT, RID, 'build_wallace_falls.py', 'Wallace Falls', route, pts, si, stops)
print(json.dumps(T))

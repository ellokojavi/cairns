"""Build Teneriffe Falls (Mount Teneriffe trailhead, the old Teneriffe road, then the Teneriffe Falls
Trail switchbacks; out and back).

Inputs, in a scratch folder (see tools/README.md): ten_oneway.json from route_track.py, frame.json
and map.png from render_map.py (map-config-teneriffe-falls.json), cover_ten.png from render_cover.py,
and the photo candidates in tools/photo-candidates/teneriffe-falls/.
Outputs: routes/teneriffe-falls/*
"""
import json, os, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routekit import roundtrip, encode, at_km, at_ele, summit_idx, map_pts, photo, timed, write

RID = 'teneriffe-falls'
SRC, OUT, CAND = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f'{OUT}/photos', exist_ok=True)
frame = json.load(open(f'{SRC}/frame.json'))
pts, cd = roundtrip(f'{SRC}/ten_oneway.json')
S = summit_idx(pts)
back = lambda k: len(pts) - 1 - k
ph = lambda *a: photo(CAND, OUT, RID, *a)
C = 'https://commons.wikimedia.org/wiki/File:'

P = dict(
    lake=ph('002', 'si-and-teneriffe', 'Mount Si (left) and Mount Teneriffe (right) from Rattlesnake Lake: the falls are in a gully on Teneriffe\'s southwest face', 'Ron Clausen', 'CC BY-SA 4.0',
            C + 'Rattlesnake_Lake_Mount_Si_Mount_Teneriffe.jpg'),
    summit=ph('016', 'teneriffe-from-trail', 'Mount Teneriffe\'s summit from the trail west of the falls', 'Buidhe', 'CC BY-SA 4.0', C + 'Mount_Teneriffe_summit_from_the_trail.jpg'),
)
COVER = ('005', 0.4)
if COVER:
    ImageOps.fit(Image.open(f'{CAND}/{COVER[0]}.jpg').convert('RGB'), (960, 540), Image.LANCZOS, centering=(0.5, COVER[1])).save(
        f'{OUT}/cover-photo.webp', quality=78, method=6)
Image.open(f'{SRC}/cover_ten.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(f'{OUT}/cover-3d.webp', quality=78, method=6)
Image.open(f'{SRC}/map.png').convert('RGB').save(f'{OUT}/map.webp', quality=82, method=6)

# on the OpenStreetMap track: the access trail meets the old road at 1.44 km, the switchbacks start
# above 500 m, the Teneriffe Falls Connector joins at 3.85 km, the falls are at 4.68 km
ROAD = at_km(cd, 1.44); SW = at_ele(pts, cd, 500, at_km(cd, 2.8), S); CONN = at_km(cd, 3.85)
plan = [
 (0, dict(n='Mount Teneriffe trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
   note='Discover Pass on the dashboard. Restrooms at the lot, no water: carry 1–1.5 L each. DNR gate: it opens about an hour after dawn and closes about an hour before dusk; '
        'the posted times on the sign win. The old bus turnaround is no parking.')),
 (ROAD, dict(n='Teneriffe road', b=5, pace=True,
   note='The access trail meets the old Teneriffe road. Follow the signs for Teneriffe Falls: a gentle old roadbed, about 8%, for the next 1.5 km.')),
 (SW, dict(n='Switchbacks start, 500 m', b=10, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
   note='The trail leaves the road grade and climbs: rocky switchbacks in and out of a talus field, about 240 m of climb in the last 1.2 km. Eat now. '
        'Watch your ankles on the talus.')),
 (CONN, dict(n='Connector junction, 590 m', b=5, gate='turn',
   note='The Teneriffe Falls Connector (an unsigned shortcut from the Mount Si side) joins here. Keep climbing: '
        'there is a lower viewpoint where many people stop by mistake; the falls are 3–4 switchbacks above it.')),
 (S, dict(n='Teneriffe Falls', b=20, take=[['gel', 'Lunch']],
   note='The falls drop in tiers down a steep rock gully. Thin after a dry summer, loud after rain. '
        'The rocks at the base are slick and drop off steeply: stay back from the edge. The boot path up beside the falls (the Kamikaze route to the summit) is unofficial and steep; DNR asks hikers to stay off it.')),
 (back(CONN), dict(n='Connector junction (down)', b=0,
   note='Keep on the switchbacks down. The connector branching off leads toward the Mount Si trailhead, not back to your car.')),
 (back(SW), dict(n='Bottom of the switchbacks', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
   note='Off the talus and back on the road grade. Easy walking from here.')),
 (back(ROAD), dict(n='Teneriffe road (down)', b=0,
   note='Leave the road here and take the access trail down to the lot (signed to the trailhead). The road carries on up toward Mount Teneriffe.')),
 (len(pts) - 1, dict(n='Mount Teneriffe trailhead', b=0, note='Finish. Back at the car, before the gate closes.')),
]
si, stops, T = timed(pts, cd, plan)
print(RID, T, [s['mv'] for s in stops])

REVIEWS = dict(
    points=[
        'Two parts: an easy old road through second-growth forest, then a short, steeper climb on rocky switchbacks and talus to the falls.',
        'Many people stop at a viewpoint a few switchbacks too low and miss the main falls: keep going until the trail ends at the water.',
        'Best after rain or during snowmelt, when the falls run full; they can be a trickle at the end of a dry summer.',
        'The talus is tiring on the ankles, and the rock near the falls is slick: poles help on the way down.',
        'Quieter than Mount Si next door, though the shared lot fills on sunny weekends. Around 3 hours for most groups.',
    ],
    sources=[['WTA: Teneriffe Falls', 'https://www.wta.org/go-hiking/hikes/teneriffe-falls'],
             ['Mountaineers route', 'https://www.mountaineers.org/activities/routes-places/teneriffe-falls'],
             ['Mountaineers trip report', 'https://www.mountaineers.org/activities/trip-reports/day-hike-teneriffe-falls-from-si-th'],
             ['The Outbound', 'https://api.theoutbound.com/washington/hiking/hike-to-teneriffe-falls-kamikaze-falls']])

photos = {0: [['routes/teneriffe-falls/cover-3d.webp', 'The route from across the valley: the old road, then the switchbacks up the gully to the falls (terrain from USGS lidar, no trees drawn)']]}
for i, keys in {0: ['lake'], 3: ['summit']}.items(): photos.setdefault(i, []).extend(P[k] for k in keys)
route = dict(
    id=RID, title='Teneriffe Falls', variant='Mount Teneriffe trailhead', size='medium',
    place='Mount Si NRCA, North Bend, WA',
    summary=f"Mount Teneriffe trailhead to Teneriffe Falls and back. {T['km']:.1f} km, +{T['up']:,} m, −{T['dn']:,} m.",
    lat=round(pts[0][0], 5), lon=round(pts[0][1], 5), tz='America/Los_Angeles',
    date='2026-10-15', dep='09:00', climate=dict(ref=250, low=8, high=19),
    deadline=dict(kind='gate', label='parking gate', dusk=-60),
    trk=encode(pts, cd), si=si, stops=stops,
    map=dict(src=f'routes/{RID}/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si, frame), route=True,
             credit='Map and 3D view: terrain from USGS 3DEP 1 m lidar (King County 2021), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
    gpx=f'routes/{RID}/{RID}.gpx', cover=f'routes/{RID}/cover-photo.webp',
    photos=photos, reviews=REVIEWS,
    text={'turn': 'Turn around here if you are not here by {lim}: the falls and the whole descent still have to fit before the parking gate closes. {rel}',
          'turnDone': ['Arrived after the {lim} cutoff. Head down now, or the car may be locked in.', 'Arrived {ahead} before the cutoff.'],
          'twilight': 'Headlamps out; the gate may already be closed.',
          'gpsHint': '<b>Keep GPS on</b> on the switchbacks, where the connector and old boot paths split off, and in fog.'},
)
write(OUT, RID, 'build_teneriffe_falls.py', 'Teneriffe Falls', route, pts, si, stops)
print(json.dumps(T))

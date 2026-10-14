"""Build West Tiger 3 (West Tiger 3 Trail from the High Point trailhead; out and back).

Inputs, in a scratch folder (see tools/README.md): wt3_oneway.json from route_track.py
(trailhead to the summit, OpenStreetMap via Overture, USGS 3DEP 1 m lidar elevations),
frame.json and map.png from render_map.py (map-config-west-tiger-3.json), cover_wt3.png from
render_cover.py, and the photo candidates in tools/photo-candidates/west-tiger-3/.
Outputs: routes/west-tiger-3/*
"""
import json, os, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routekit import roundtrip, encode, at_km, summit_idx, map_pts, photo, timed, write

RID = 'west-tiger-3'
SRC, OUT, CAND = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f'{OUT}/photos', exist_ok=True)
frame = json.load(open(f'{SRC}/frame.json'))
pts, cd = roundtrip(f'{SRC}/wt3_oneway.json')
S = summit_idx(pts)
back = lambda k: len(pts) - 1 - k
ph = lambda *a: photo(CAND, OUT, RID, *a)
C = 'https://commons.wikimedia.org/wiki/File:'

P = dict(
    talus=ph('049', 'talus-rocks', 'Talus Rocks, the side trail straight on from this junction: house-sized boulders and small caves under the moss', 'Dennis Bratland', 'CC BY-SA 4.0',
             C + 'Talus_Rocks,_Tiger_Mountain,_Washington_-_large_bouldrer.JPG'),
    squak=ph('029', 'squak-from-trail', 'Squak Mountain to the west, from the upper trail about 3 km from the trailhead', 'Atomic Taco', 'CC BY-SA 2.0',
             C + 'View_from_near_West_Tiger_2_(12607838003).jpg'),
    mist=ph('031', 'tiger-in-mist', 'Tiger Mountain in mist: the summits are often in cloud when the valley is clear', 'Chris Light', 'CC BY-SA 4.0', C + 'Rain_on_the_Mtn_148.jpg'),
    view=ph('024', 'view-from-summit', 'From the summit of West Tiger 3: Lake Sammamish, Bellevue and Seattle to the northwest, the Olympics on the horizon', 'Atomic Taco', 'CC BY-SA 2.0',
            C + 'View_from_West_Tiger_3_(12607872533).jpg'),
    rainier=ph('079', 'rainier-from-tiger', 'Mount Rainier from Tiger Mountain, to the south on a clear day', 'Thales', 'CC BY 2.0', C + 'View_of_Mt_Rainier_from_Tiger_Mt.jpg'),
)
COVER = ('079', 0.45)
if COVER:
    ImageOps.fit(Image.open(f'{CAND}/{COVER[0]}.jpg').convert('RGB'), (960, 540), Image.LANCZOS, centering=(0.5, COVER[1])).save(
        f'{OUT}/cover-photo.webp', quality=78, method=6)
Image.open(f'{SRC}/cover_wt3.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(f'{OUT}/cover-3d.webp', quality=78, method=6)
Image.open(f'{SRC}/map.png').convert('RGB').save(f'{OUT}/map.webp', quality=82, method=6)

# junctions measured on the OpenStreetMap track (route_track.py): Talus Rocks 1.52 km,
# West Tiger RR Grade 3.44 km, Cable Line 3.93 km, summit 4.40 km
TALUS = at_km(cd, 1.52); RR = at_km(cd, 3.44); CABLE = at_km(cd, 3.93)
plan = [
 (0, dict(n='High Point trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
   note='Discover Pass on the dashboard. Toilet at the trailhead, no water: carry 1–1.5 L each. The road gate is open dawn to dusk; '
        'if the lot is full, park outside the gate. Walk past the kiosk and take the West Tiger 3 Trail: the Bus Road and Tiger Mountain Trail cross it in the first 300 m.')),
 (TALUS, dict(n='Talus Rocks junction', b=5, pace=True,
   note='The Talus Rocks trail goes straight (a side trip to boulder caves); turn left and keep climbing on the West Tiger 3 Trail. '
        'From here it is steady, wide and rocky, about 15%, switchback after switchback.')),
 (RR, dict(n='West Tiger Railroad Grade', b=10, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
   note='The old railroad grade crosses here, 600 m up. Eat now: the last 170 m of climb are the steepest of the hike.')),
 (CABLE, dict(n='Cable Line junction', b=5, gate='turn', wind=True,
   note='The Cable Line Trail joins here: it runs straight down the fall line to the north, steep and muddy. Remember this junction for the way down. '
        'The trees thin out above here; put a layer on before the top.')),
 (S, dict(n='West Tiger 3 summit', b=20, wind=True, take=[['gel', 'Lunch']],
   note='An open, logged summit with benches of rock: Issaquah, Lake Sammamish, Seattle and the Olympics to the west, Rainier to the south on a clear day. '
        'Often in the clouds when the valley is clear, and busy even midweek.')),
 (back(CABLE), dict(n='Cable Line junction (down)', b=0,
   note='Stay on the wide West Tiger 3 Trail. The Cable Line branching off here looks like a shortcut: it is a steep, muddy fall-line trail that comes out on the access road about 600 m east of the lot.')),
 (back(RR), dict(n='Railroad Grade (down)', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
   note='Straight across the railroad grade and on down. Loose rock on the steeper pitches: short steps, poles if you have them.')),
 (back(TALUS), dict(n='Talus Rocks junction (down)', b=0,
   note='Keep right (downhill) on the West Tiger 3 Trail. The last 1.5 km is gentler forest, crossing the Tiger Mountain Trail and the Bus Road just before the lot.')),
 (len(pts) - 1, dict(n='High Point trailhead', b=0, note='Finish. Back at the car.')),
]
si, stops, T = timed(pts, cd, plan)
print(RID, T, [s['mv'] for s in stops])

REVIEWS = dict(
    points=[
        'The closest real climb to Seattle: a wide, well-graded trail that climbs steadily the whole way. Many use it as a training hike; it feels like a leg workout more than a scenic walk.',
        'About two hours up for most people, and most of a morning for the round trip.',
        'On a clear day the summit view is big: Seattle, the Sound, the Olympics and Rainier. It also sits in the clouds often, when the valley below is clear.',
        'Busy: the lot fills on weekends, and even midweek there are usually a few groups at the top.',
        'The Cable Line Trail is the steep, muddy alternative up; most take the main trail, especially down.',
        'Rocky, rooty and muddy in places after rain, with some blowdowns in winter and spring; poles help on the descent.',
    ],
    sources=[['WTA: West Tiger 3', 'https://www.wta.org/go-hiking/hikes/west-tiger-3'],
             ['Mountaineers trip reports', 'https://www.mountaineers.org/activities/trip-reports/day-hike-west-tiger-no-3-trail'],
             ['Hiking Project', 'https://hikingproject.com/trail/7037162/west-tiger-3-trail'],
             ['Mountaineers route', 'https://mountaineers.org/activities/routes-places/tiger-mountain-area-review/west-tiger-mountain-no-3']])

photos = {0: [['routes/west-tiger-3/cover-3d.webp', 'The route from the north, above I-90: the trail climbs the north ridge of West Tiger 3 (terrain from USGS lidar, no trees drawn)']]}
for i, keys in {1: ['talus'], 2: ['squak'], 3: ['mist'], 4: ['view', 'rainier']}.items(): photos.setdefault(i, []).extend(P[k] for k in keys)
route = dict(
    id=RID, title='West Tiger 3', variant='West Tiger 3 Trail', size='medium',
    place='Tiger Mountain State Forest, Issaquah, WA',
    summary=f"High Point trailhead to the West Tiger 3 summit and back. {T['km']:.1f} km, +{T['up']:,} m, −{T['dn']:,} m.",
    lat=round(pts[0][0], 5), lon=round(pts[0][1], 5), tz='America/Los_Angeles',
    date='2026-10-15', dep='09:00', climate=dict(ref=160, low=8, high=19),
    deadline=dict(kind='gate', label='road gate', dusk=0, open=0),
    trk=encode(pts, cd), si=si, stops=stops,
    map=dict(src=f'routes/{RID}/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si, frame), route=True,
             credit='Map and 3D view: terrain from USGS 3DEP 1 m lidar (King County 2021), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
    gpx=f'routes/{RID}/{RID}.gpx', cover=f'routes/{RID}/cover-photo.webp',
    photos=photos, reviews=REVIEWS,
    text={'turn': 'Turn around here if you are not here by {lim}: the top and the whole descent still have to fit before the road gate closes at dusk. {rel}',
          'turnDone': ['Arrived after the {lim} cutoff. Head down now; the gate closes at dusk.', 'Arrived {ahead} before the cutoff.'],
          'twilight': 'Headlamps out; it gets dark under the trees first, and the road gate closes at dusk.',
          'gpsHint': '<b>Keep GPS on</b> only near the junctions: Tiger Mountain has dozens of trails, and the Cable Line junction is easy to miss on the way down.'},
)
write(OUT, RID, 'build_west_tiger_3.py', 'West Tiger 3', route, pts, si, stops)
print(json.dumps(T))

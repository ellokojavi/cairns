"""Build Mount Si (main trail, out and back to the base of the Haystack).

Inputs, in a scratch folder (see tools/README.md): si_oneway.json (trailhead to the
top of the trail, OpenStreetMap via Overture, USGS 3DEP 1 m lidar elevations), frame.json
and map.png from render_map.py, cover_si.png from render_cover.py, and the photo
candidates in tools/photo-candidates/mount-si/.
Outputs: routes/mount-si/*
"""
import json, os, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routekit import roundtrip, encode, gain, leg_minutes, at_km, at_ele, summit_idx, map_pts, gpx

SRC, OUT, CAND = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f'{OUT}/photos', exist_ok=True)
frame = json.load(open(f'{SRC}/frame.json'))

# the trail proper ends in the boulder basin under the Haystack (~1,190 m); the Haystack
# itself is an exposed scramble, offered as an option at the top stop, not part of the route
j = json.load(open(f'{SRC}/si_oneway.json'))
cut = next(i for i, d in enumerate(j['d']) if d >= 6100)
json.dump({k: v[:cut + 1] for k, v in j.items()}, open(f'{SRC}/si_trail.json', 'w'))
pts, cd = roundtrip(f'{SRC}/si_trail.json')
S = summit_idx(pts)
back = lambda k: len(pts) - 1 - k

LIC = {'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0', 'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0',
       'CC BY-SA 2.0': 'https://creativecommons.org/licenses/by-sa/2.0', 'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0'}
def ph(n, f, caption, author, lic, commons):
    im = Image.open(f'{CAND}/{n}.jpg').convert('RGB'); im.thumbnail((1024, 1024), Image.LANCZOS)
    im.save(f'{OUT}/photos/{f}.webp', quality=78, method=6)
    return [f'routes/mount-si/photos/{f}.webp', f"{caption}<br><span class='cred'>Photo: {author} &middot; "
            f"<a href='{LIC[lic]}' target='_blank' rel='noopener'>{lic}</a> &middot; "
            f"<a href='https://commons.wikimedia.org/wiki/File:{commons}' target='_blank' rel='noopener'>source</a></span>"]
P = dict(
    valley=ph('071', 'from-the-valley', 'Mount Si from the Snoqualmie Valley Trail: the climb is the whole south face', 'Ron Clausen', 'CC BY-SA 4.0',
              'Mount_Si_seen_from_Snoqualmie_Valley_Trail.jpg'),
    goats=ph('085', 'haystack-cliffs', 'The cliffs below the Haystack. Mountain goats live up here: give them 50 m and never feed them', 'brewbooks', 'CC BY-SA 2.0',
             'Mountain_Goats_on_Mount_Si_-_Flickr_-_brewbooks.jpg'),
    basin=ph('086', 'summit-boulders', 'The boulder basin at the top of the trail, here in winter. This is the summit for most hikers', 'brewbooks', 'CC BY-SA 2.0',
             'Fellow_Mount_Si_hikers_-_Flickr_-_brewbooks.jpg'),
    rainier=ph('087', 'rainier-from-si', 'Mount Rainier to the south, from the rocks near the top', 'brewbooks', 'CC BY-SA 2.0',
               'Mount_Rainier_from_Mount_Si_-_Flickr_-_brewbooks.jpg'),
    rays=ph('082', 'valley-view', 'Looking out over the Snoqualmie Valley from an outcrop near the top', 'brewbooks', 'CC BY-SA 2.0',
            'Mount_Si_with_rays_of_sunlight_-_Flickr_-_brewbooks.jpg'),
    i90=ph('003', 'i90-from-si', 'I-90 winding up the valley toward Snoqualmie Pass, from the top', 'Steven Pavlov', 'CC BY-SA 3.0', 'I-90_as_seen_from_Mount_Si.jpg'),
    river=ph('058', 'si-and-river', 'Looking back: Mount Si over the Snoqualmie River', 'loggedout (Panoramio)', 'CC BY 3.0', 'Mt._Si_and_Snoqualmie_River_-_panoramio.jpg'),
)
cov = ImageOps.fit(Image.open(f'{CAND}/072.jpg').convert('RGB'), (960, 540), Image.LANCZOS, centering=(0.5, 0.4))
cov.save(f'{OUT}/cover-photo.webp', quality=78, method=6)
Image.open(f'{SRC}/cover_si.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(f'{OUT}/cover-3d.webp', quality=78, method=6)
Image.open(f'{SRC}/map.png').convert('RGB').save(f'{OUT}/map.webp', quality=82, method=6)

FLATS = at_km(cd, 2.85); UPPER = at_ele(pts, cd, 900, 0, S); JCT = at_km(cd, 5.75)
plan = [
 (0, dict(n='Trailhead', b=0, take=[['salt', 'Electrolyte: 1 serving + 500 ml, 30 min before']],
   note='Discover Pass on the dashboard. Water and toilets at the trailhead; none on the trail, so carry 1.5–2 L each. The lot holds about 200 cars and fills on sunny weekends.')),
 (FLATS, dict(n='Snag Flats', b=5, pace=True,
   note='The one flat stretch: a boardwalk through big old trees and fire-scarred snags. Almost half the distance, but only a third of the climb.')),
 (UPPER, dict(n='Upper switchbacks, 900 m', b=10, take=[['salt', 'Electrolyte: 1 serving + 500 ml'], ['gel', 'Gel or snack']],
   note='Steady 15–18% grade, switchback after switchback. Eat now; the last 300 m of climb are the steepest.')),
 (JCT, dict(n='Old Si Trail junction', b=5, gate='turn', wind=True,
   note='The Old Si Trail comes in from the left. Trees thin out and the trail turns rocky. Layer up before the top: it is usually colder and windier than the forest.')),
 (S, dict(n='Top of the trail, Haystack basin', b=20, wind=True, take=[['gel', 'Lunch']],
   note='The summit for most hikers: views over North Bend, Mailbox Peak to the east, Rainier to the south. The Haystack above is an exposed scramble (+85 m, steep rock, real drop-offs). Skip it when wet or icy, or without scrambling experience.')),
 (back(JCT), dict(n='Old Si Trail junction (down)', b=0,
   note='Stay on the main Mount Si Trail. The Old Si Trail is steeper and rougher; easy to take by mistake on the way down.')),
 (back(FLATS), dict(n='Snag Flats (down)', b=5, take=[['salt', 'Electrolyte: 1 serving + 500 ml']],
   note='Flat ground for a few minutes; the rest of the descent is steady. Shorten poles and keep the steps small.')),
 (len(pts) - 1, dict(n='Trailhead', b=0, note='Finish. Back at the car.')),
]
si = [k for k, _ in plan]
assert si == sorted(si) and len(set(si)) == len(si), si
stops = []
for i, (k, s) in enumerate(plan):
    s = dict(s); s['mv'] = 0 if i == 0 else leg_minutes(pts, cd, si[i - 1], k); stops.append(s)
up, dn = gain([p[2] for p in pts]); km = cd[-1] / 1000; hi = max(p[2] for p in pts)
mv = sum(s['mv'] for s in stops); br = sum(s['b'] for s in stops[:-1])
print(f'mount-si {km:.2f} km +{up} -{dn} hi {hi:.0f}, {len(pts)} pts, moving {mv//60}:{mv%60:02d} breaks {br}', [s['mv'] for s in stops])

REVIEWS = dict(
    points=[
        'A steady, sustained climb rather than a technical one: about 15% for most of the way, the same grade switchback after switchback. Some call it ideal conditioning, others call it monotonous.',
        'Busy. The lot fills by mid-morning on sunny weekends; weekday mornings are much quieter. Start early.',
        'The Haystack is the real risk: an exposed scramble with drop-offs and no protection. Most hikers treat the boulder basin below it as the summit, and skip the Haystack when it is wet or icy.',
        'From late autumn to spring the upper trail can be snowy or icy; microspikes are often recommended for that stretch. Poles help on the long descent.',
        'The reward is the view: the Snoqualmie Valley straight below, and Rainier on a clear day.',
    ],
    sources=[['WTA', 'https://www.wta.org/go-hiking/hikes/mount-si'], ['AllTrails reviews', 'https://www.alltrails.com/trail/us/washington/mount-si-trail'],
             ['Tripadvisor', 'https://www.tripadvisor.com/Attraction_Review-g58640-d8727585-Reviews-Mt_Si-North_Bend_Washington.html'],
             ['SummitPost', 'https://www.summitpost.org/page/150709'], ['Outdoor Project', 'https://www.outdoorproject.com/united-states/washington/mount-si-hike']])

route = dict(
    id='mount-si', title='Mount Si', variant='Main trail', size='long',
    place='Mount Si NRCA, North Bend, WA',
    summary=f'Mount Si trailhead to the Haystack basin and back. {km:.1f} km, +{up:,} m, −{dn:,} m.',
    lat=round(pts[0][0], 5), lon=round(pts[0][1], 5), tz='America/Los_Angeles',
    dep='07:00', climate=dict(ref=200, low=8, high=18), deadline=dict(kind='dark'),
    trk=encode(pts, cd), si=si, stops=stops,
    map=dict(src='routes/mount-si/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si, frame), route=True,
             credit='Map and 3D view: terrain from USGS 3DEP 1 m lidar (King County 2021), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
    gpx='routes/mount-si/mount-si.gpx', cover='routes/mount-si/cover-photo.webp',
    photos={0: [P['valley'], ['routes/mount-si/cover-3d.webp', 'The route on the south face, seen from above North Bend (terrain from USGS lidar, no trees drawn)']],
            3: [P['goats']], 4: [P['basin'], P['rainier'], P['rays'], P['i90']], 7: [P['river']]},
    reviews=REVIEWS,
    text={'turn': 'Turn around here if you are not here by {lim}: the top and the whole descent still have to fit before dark. {rel}',
          'turnDone': ['Arrived after the {lim} cutoff. Head down now; it gets dark under the trees first.', 'Arrived {ahead} before the cutoff.'],
          'twilight': 'Headlamps out for the lower forest; it gets dark under the trees first.',
          'gpsHint': '<b>Keep GPS on</b> only around the top, where boot paths split among the boulders, and in fog.'},
)
with open(f'{OUT}/route.js', 'w') as f:
    f.write('// generated by tools/build_mount_si.py — edit the generator, not this file\n')
    f.write('window.ROUTE=' + json.dumps(route, ensure_ascii=False, separators=(',', ':')) + ';\n')
with open(f'{OUT}/mount-si.gpx', 'w') as f:
    f.write(gpx('Mount Si', route['summary'], pts, si, stops))
print(json.dumps(dict(km=round(km, 1), up=up, hi=round(hi), moving=mv, breaks=br)))

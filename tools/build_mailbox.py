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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from routekit import roundtrip, encode, gain, leg_minutes, at_km, at_ele, summit_idx, map_pts, gpx

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
frame = json.load(open(f'{SRC}/frame.json'))

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
  photos=lambda nm: {0: [P['road'], RENDER(nm)], 3: [P['boulders'], P['academy']], 4: [P['mailbox'], P['rainier'], P['sunset']], 7: [P['salal']]},
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
  photos=lambda nm: {0: [P['road'], RENDER(nm)], 3: [P['boulders'], P['academy']], 4: [P['mailbox'], P['rainier'], P['sunset']], 8: [P['salal']]},
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


# Creative Commons photos (Wikimedia Commons), chosen from tools/photo-candidates by quality
# and by where on the route they were taken. Credit line as the licences require.
LIC = {'CC0': 'https://creativecommons.org/publicdomain/zero/1.0', 'CC BY 2.0': 'https://creativecommons.org/licenses/by/2.0',
       'CC BY-SA 2.0': 'https://creativecommons.org/licenses/by-sa/2.0', 'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0'}
def ph(f, caption, author, lic, commons):
    return [f'routes/mailbox/photos/{f}.webp', f"{caption}<br><span class='cred'>Photo: {author} &middot; "
            f"<a href='{LIC[lic]}' target='_blank' rel='noopener'>{lic}</a> &middot; "
            f"<a href='https://commons.wikimedia.org/wiki/File:{commons}' target='_blank' rel='noopener'>source</a></span>"]
P = dict(
    road=ph('from-the-road', 'Mailbox Peak from the Middle Fork road, on the drive in: the whole climb in one view', 'Ron Clausen', 'CC BY-SA 4.0',
            'Mailbox_Peak_seen_from_Middle_Fork_Snoqualmie_River_Road._Washington_state.jpg'),
    boulders=ph('boulder-field-snow', 'The boulder field above the trees, after an early snow. Late October can look like this', 'MarshyBoardwalk', 'CC0',
                'Snow_covered_rocks_on_Mailbox_Peak.jpg'),
    academy=ph('fire-academy-below', 'From the open upper slopes: the Fire Training Academy straight below, to the south', 'Peter Stevens', 'CC BY 2.0',
               'Washington_State_Fire_Training_Center.jpg'),
    mailbox=ph('summit-mailbox', 'The mailbox and its plaque on the summit rocks', 'Wilderness trespasser', 'CC BY-SA 4.0', 'Mailbox_Peak_summit_views_01.jpg'),
    rainier=ph('rainier-from-summit', 'Mount Rainier on the southern horizon, from the summit', 'Wilderness trespasser', 'CC BY-SA 4.0', 'Mailbox_Peak_summit_views_11.jpg'),
    sunset=ph('mailbox-sunset', 'The mailbox at sunset. Leave well before this: the parking gate closes first', 'Michael Cline', 'CC BY-SA 2.0', 'Mailbox_Peak_mailbox.jpg'),
    salal=ph('from-salal-point', 'Looking back at what you climbed: Mailbox Peak from Salal Point, south of the trailhead', 'Peter Stevens', 'CC BY 2.0',
             'Mailbox_Peak,_from_Salal_Point.jpg'),
)
RENDER = lambda nm: [f'routes/mailbox/cover-{nm}.webp', 'The route on the mountain, seen from the northwest (terrain from USGS lidar, no trees drawn)']


REVIEWS = dict(
    points=[
        'Hikers agree the Old Trail is the brutal one: no switchbacks, root steps up to knee height, loose rock. Many go up the Old Trail and come down the New Trail to spare their knees.',
        'The New Trail is long but steadily graded and well built; reports call it much easier on the descent.',
        'The Old Trail has not been maintained since the New Trail opened in 2014. Hiker traffic has made false paths, so it is easy to follow going up but easy to lose coming down.',
        'The last stretch is a steep boulder field, the same for both trails. Poles help; from late autumn, traction (microspikes) is recommended on the Old Trail.',
        'Bring more water and food than you think: there is no reliable water, and the climb is about 1,200 m either way.',
        'The parking gate closes around dusk and cars do get locked in; check the posted time.',
    ],
    sources=[['WTA, Mailbox Peak', 'https://www.wta.org/go-hiking/hikes/mailbox-peak'], ['WTA, Old Trail', 'https://www.wta.org/go-hiking/hikes/mailbox-peak-old-trail'],
             ['WTA trip report, Nov 2025', 'https://www.wta.org/go-hiking/trip-reports/trip_report-2025-11-28.201614457999'],
             ['WTA trip report, Jul 2025', 'https://www.wta.org/go-hiking/trip-reports/trip_report-2025-07-29.152448122962'],
             ['Tripadvisor', 'https://www.tripadvisor.com/Attraction_Review-g58748-d10895175-Reviews-Mailbox_Peak-Snoqualmie_Washington.html'],
             ['Moore Misadventures', 'https://www.mooremisadventures.com/blog/mailbox-peak']])

catalog = []
for nm, R in ROUTES.items():
    pts, cd = roundtrip(f'{SRC}/{nm}_oneway.json')
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
        map=dict(src='routes/mailbox/map.webp', w=frame['W'], h=frame['H'], pts=map_pts(pts, si, frame), route=True,
                 credit='Map and cover: terrain from USGS 3DEP 1 m lidar (King County 2021), public domain. Trails © OpenStreetMap contributors, via Overture Maps (ODbL).'),
        gpx=f'routes/mailbox/{R["id"]}.gpx', cover=f'routes/mailbox/cover-{nm}-photo.webp',
        photos=R['photos'](nm),
        reviews=REVIEWS,
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

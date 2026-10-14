// Every route the planner knows. Shared by the picker, the planner and the service worker
// (which precaches every file listed here so each route works in airplane mode).
const MAILBOX_PHOTOS=['from-the-road','boulder-field-snow','fire-academy-below','summit-mailbox','rainier-from-summit','mailbox-sunset','from-salal-point']
  .map(n=>'routes/mailbox/photos/'+n+'.webp');
// go / goEnd: [lat, lon, label] of the parking, for one-tap directions in Google Maps
// at: the hike's AllTrails page (path after alltrails.com/), for reading reviews and conditions before going
// pass: the parking pass ('discover' Discover Pass, 'nwfp' Northwest Forest Pass); hl: highlights, for the picker's filters
// the picker's overview map: relief image from tools/render_overview.py and its lon/lat bounds
self.OVERVIEW={src:'routes/overview.webp',w:-122.50,e:-120.55,s:47.33,n:47.99,W:3600,H:1809,
  // [name, lon, lat, 1 = only on the enlarged map]
  places:[['Seattle',-122.335,47.608],['Bellevue',-122.20,47.61,1],['Issaquah',-122.035,47.53,1],['North Bend',-121.787,47.495],
    ['Gold Bar',-121.697,47.857,1],['Snoqualmie Pass',-121.413,47.424],['Skykomish',-121.36,47.71,1],['Stevens Pass',-121.089,47.746],['Leavenworth',-120.661,47.596]]};
self.HIKES=[
 {id:'mailbox-new', at:'trail/us/washington/mailbox-peak-new-trail--2', pass:'discover', hl:['summit'], go:[47.4668,-121.6731,'Mailbox Peak trailhead'], file:'routes/mailbox/new.js', peak:'Mailbox Peak', title:'Mailbox Peak', variant:'New Trail',
  place:'Middle Fork Snoqualmie, near North Bend, WA', type:'Out and back',
  km:15.9, up:1219, hi:1474, moving:345, breaks:50, cover:'routes/mailbox/cover-new-photo.webp',
  coverCredit:['Summit view west at dawn. Sergei Akulich, CC0','https://commons.wikimedia.org/wiki/File:Mailbox_Peak,_United_States_(Unsplash).jpg'],
  blurb:'The graded trail: long, steady switchbacks through forest, then one steep, rocky kilometre to the mailbox.',
  assets:['routes/mailbox/new.js','routes/mailbox/map.webp','routes/mailbox/cover-new.webp','routes/mailbox/cover-new-photo.webp','routes/mailbox/mailbox-new.gpx'].concat(MAILBOX_PHOTOS)},
 {id:'mailbox-old', at:'trail/us/washington/mailbox-peak-old-trail', pass:'discover', hl:['summit'], go:[47.4668,-121.6731,'Mailbox Peak trailhead'], file:'routes/mailbox/old.js', peak:'Mailbox Peak', title:'Mailbox Peak', variant:'Old Trail',
  place:'Middle Fork Snoqualmie, near North Bend, WA', type:'Out and back',
  km:7.5, up:1207, hi:1474, moving:270, breaks:45, cover:'routes/mailbox/cover-old-photo.webp',
  coverCredit:['Mailbox Peak from Mt. Washington. Peter Stevens, CC BY 2.0','https://commons.wikimedia.org/wiki/File:Mailbox_Peak,_sw.jpg'],
  blurb:'The original route straight up the ridge: half the distance, the same climb. Roots, mud and 40% grades.',
  assets:['routes/mailbox/old.js','routes/mailbox/map.webp','routes/mailbox/cover-old.webp','routes/mailbox/cover-old-photo.webp','routes/mailbox/mailbox-old.gpx'].concat(MAILBOX_PHOTOS)},
 {id:'mount-si', at:'trail/us/washington/mount-si-trail', pass:'discover', hl:['summit'], go:[47.4876,-121.7226,'Mount Si trailhead'], file:'routes/mount-si/route.js', peak:'Mount Si', title:'Mount Si', variant:'Main trail',
  place:'Mount Si NRCA, North Bend, WA', type:'Out and back',
  km:12.2, up:989, hi:1193, moving:270, breaks:45, cover:'routes/mount-si/cover-photo.webp',
  coverCredit:['Mount Si from Mill Pond Road. Ron Clausen, CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Mount_Si_seen_from_Mill_Pond_Road,_Washington_state.jpg'],
  blurb:'The classic North Bend climb: steady switchbacks through big forest to the boulders under the Haystack, with the whole valley below.',
  assets:['routes/mount-si/route.js','routes/mount-si/map.webp','routes/mount-si/cover-photo.webp','routes/mount-si/cover-3d.webp','routes/mount-si/mount-si.gpx']
    .concat(['from-the-valley','haystack-cliffs','summit-boulders','rainier-from-si','valley-view','i90-from-si','si-and-river'].map(n=>'routes/mount-si/photos/'+n+'.webp'))},
 {id:'little-bandera', at:'poi/us/washington/little-bandera-mountain', pass:'nwfp', hl:['summit','lakes'], go:[47.4247,-121.5835,'Ira Spring trailhead'], file:'routes/little-bandera/route.js', peak:'Little Bandera', title:'Little Bandera Mountain', variant:'Ira Spring Trail',
  place:'Alpine Lakes Wilderness, I-90 exit 45, WA', type:'Out and back',
  km:10.6, up:919, hi:1575, moving:245, breaks:45, cover:'routes/little-bandera/cover-photo.webp',
  coverCredit:['Bandera Mountain (left) and Mount Defiance from Mount Catherine. Ron Clausen, CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Bandera_and_Defiance.jpg'],
  blurb:'A long, easy-graded climb out of the I-90 valley, then a steep, rocky kilometre up the ridge to Rainier and the lakes basin.',
  assets:['routes/little-bandera/route.js','routes/little-bandera/map.webp','routes/little-bandera/cover-photo.webp','routes/little-bandera/cover-3d.webp','routes/little-bandera/little-bandera.gpx']
    .concat(['bandera-from-pratt','kaleetan-from-trail','from-little-bandera','chair-peak','lakes-below','bandera-winter'].map(n=>'routes/little-bandera/photos/'+n+'.webp'))},
 {id:'west-tiger-3', at:'trail/us/washington/west-tiger-3', pass:'discover', hl:['summit'], go:[47.5296,-121.9956,'High Point trailhead (West Tiger 3)'], file:'routes/west-tiger-3/route.js', peak:'West Tiger 3', title:'West Tiger 3', variant:'West Tiger 3 Trail',
  place:'Tiger Mountain State Forest, Issaquah, WA', type:'Out and back',
  km:8.8, up:607, hi:769, moving:185, breaks:45, cover:'routes/west-tiger-3/cover-photo.webp',
  coverCredit:['Mount Rainier from Tiger Mountain. Thales, CC BY 2.0','https://commons.wikimedia.org/wiki/File:View_of_Mt_Rainier_from_Tiger_Mt.jpg'],
  blurb:'The closest real climb to Seattle: a wide, steady trail up from I-90 to an open summit over Issaquah, the Sound and Rainier.',
  assets:['routes/west-tiger-3/route.js','routes/west-tiger-3/map.webp','routes/west-tiger-3/cover-photo.webp','routes/west-tiger-3/cover-3d.webp','routes/west-tiger-3/west-tiger-3.gpx']
    .concat(['talus-rocks','squak-from-trail','tiger-in-mist','view-from-summit','rainier-from-tiger'].map(n=>'routes/west-tiger-3/photos/'+n+'.webp'))},
 {id:'teneriffe-falls', at:'trail/us/washington/teneriffe-falls', pass:'discover', hl:['waterfall'], go:[47.4867,-121.7099,'Mount Teneriffe trailhead'], file:'routes/teneriffe-falls/route.js', peak:'Teneriffe Falls', title:'Teneriffe Falls', variant:'Mount Teneriffe trailhead',
  place:'Mount Si NRCA, North Bend, WA', type:'Out and back',
  km:9.3, up:521, hi:740, moving:170, breaks:45, cover:'routes/teneriffe-falls/cover-photo.webp',
  coverCredit:['Mount Teneriffe from Rattlesnake Lake. Ron Clausen, CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Mount_Teneriffe_Rattlesnake_Lake_tree_stumps.jpg'],
  blurb:'An old road through the forest, then rocky switchbacks up a talus gully to a tall, tiered waterfall under Mount Teneriffe.',
  assets:['routes/teneriffe-falls/route.js','routes/teneriffe-falls/map.webp','routes/teneriffe-falls/cover-photo.webp','routes/teneriffe-falls/cover-3d.webp','routes/teneriffe-falls/teneriffe-falls.gpx']
    .concat(['si-and-teneriffe','teneriffe-from-trail'].map(n=>'routes/teneriffe-falls/photos/'+n+'.webp'))},
 {id:'wallace-falls', at:'trail/us/washington/wallace-falls-via-woody-trail', pass:'discover', hl:['waterfall'], go:[47.8670,-121.6781,'Wallace Falls State Park trailhead'], file:'routes/wallace-falls/route.js', peak:'Wallace Falls', title:'Wallace Falls', variant:'Woody Trail to the Upper Falls',
  place:'Wallace Falls State Park, Gold Bar, WA', type:'Out and back',
  km:8.2, up:445, hi:507, moving:155, breaks:40, cover:'routes/wallace-falls/cover-photo.webp',
  coverCredit:['Middle Wallace Falls. Kash Goudarzi, CC0','https://commons.wikimedia.org/wiki/File:Frothy_waterfall_in_the_woods_(Unsplash).jpg'],
  blurb:'Along the Wallace River, then up the canyon past the Lower, Middle and Upper Falls. The park opens at 8:00 from October.',
  assets:['routes/wallace-falls/route.js','routes/wallace-falls/map.webp','routes/wallace-falls/cover-photo.webp','routes/wallace-falls/cover-3d.webp','routes/wallace-falls/wallace-falls.gpx']
    .concat(['under-the-wires','wallace-river','lower-falls','middle-falls','middle-falls-rainbow','upper-falls','upper-falls-close','woody-trail-fog'].map(n=>'routes/wallace-falls/photos/'+n+'.webp'))},
 {id:'enchantments', at:'trail/us/washington/the-enchantments-trail', pass:'nwfp', hl:['lakes'], go:[47.52777,-120.82083,'Stuart Lake trailhead (start)'], goEnd:[47.54415,-120.70969,'Snow Lakes trailhead (finish)'], file:'routes/enchantments/route.js', peak:'Enchantments', title:'Enchantments traverse', variant:'Stuart Lake to Snow Lakes',
  place:'Alpine Lakes Wilderness, near Leavenworth, WA', type:'Point to point', done:'Walked Sept 22, 2026',
  km:29.8, up:1957, hi:2387, moving:645, breaks:110, cover:'routes/enchantments/photos/05.webp',
  coverCredit:['Prusik Peak and the Temple. Buidhe, CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Prusik_Peak_and_the_Temple_from_near_Perfection_Lake_(11_October_2024).jpg'],
  blurb:'Colchuck Lake, Aasgard Pass and the Core lakes, then the long way down past Snow and Nada Lakes.',
  assets:['routes/enchantments/route.js','routes/enchantments/map.webp','routes/enchantments/enchantments-sep22-milestones.gpx']
    .concat(['01','02','03','04','05','06','07','08'].map(n=>'routes/enchantments/photos/'+n+'.webp'))}
];

// Every route the planner knows. Shared by the picker, the planner and the service worker
// (which precaches every file listed here so each route works in airplane mode).
const MAILBOX_PHOTOS=['from-the-road','boulder-field-snow','fire-academy-below','summit-mailbox','rainier-from-summit','mailbox-sunset','from-salal-point']
  .map(n=>'routes/mailbox/photos/'+n+'.webp');
// go / goEnd: [lat, lon, label] of the parking, for one-tap directions in Google Maps
self.HIKES=[
 {id:'mailbox-new', go:[47.4668,-121.6731,'Mailbox Peak trailhead'], file:'routes/mailbox/new.js', peak:'Mailbox Peak', title:'Mailbox Peak', variant:'New Trail', size:'Long',
  place:'Middle Fork Snoqualmie, near North Bend, WA', type:'Out and back',
  km:15.9, up:1219, hi:1474, moving:345, breaks:50, cover:'routes/mailbox/cover-new-photo.webp',
  coverCredit:['Summit view west at dawn. Sergei Akulich, CC0','https://commons.wikimedia.org/wiki/File:Mailbox_Peak,_United_States_(Unsplash).jpg'],
  blurb:'The graded trail: long, steady switchbacks through forest, then one steep, rocky kilometre to the mailbox.',
  assets:['routes/mailbox/new.js','routes/mailbox/map.webp','routes/mailbox/cover-new.webp','routes/mailbox/cover-new-photo.webp','routes/mailbox/mailbox-new.gpx'].concat(MAILBOX_PHOTOS)},
 {id:'mailbox-old', go:[47.4668,-121.6731,'Mailbox Peak trailhead'], file:'routes/mailbox/old.js', peak:'Mailbox Peak', title:'Mailbox Peak', variant:'Old Trail', size:'Short',
  place:'Middle Fork Snoqualmie, near North Bend, WA', type:'Out and back',
  km:7.5, up:1207, hi:1474, moving:270, breaks:45, cover:'routes/mailbox/cover-old-photo.webp',
  coverCredit:['Mailbox Peak from Mt. Washington. Peter Stevens, CC BY 2.0','https://commons.wikimedia.org/wiki/File:Mailbox_Peak,_sw.jpg'],
  blurb:'The original route straight up the ridge: half the distance, the same climb. Roots, mud and 40% grades.',
  assets:['routes/mailbox/old.js','routes/mailbox/map.webp','routes/mailbox/cover-old.webp','routes/mailbox/cover-old-photo.webp','routes/mailbox/mailbox-old.gpx'].concat(MAILBOX_PHOTOS)},
 {id:'mount-si', go:[47.4876,-121.7226,'Mount Si trailhead'], file:'routes/mount-si/route.js', peak:'Mount Si', title:'Mount Si', variant:'Main trail', size:'Long',
  place:'Mount Si NRCA, North Bend, WA', type:'Out and back',
  km:12.2, up:989, hi:1193, moving:270, breaks:45, cover:'routes/mount-si/cover-photo.webp',
  coverCredit:['Mount Si from Mill Pond Road. Ron Clausen, CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Mount_Si_seen_from_Mill_Pond_Road,_Washington_state.jpg'],
  blurb:'The classic North Bend climb: steady switchbacks through big forest to the boulders under the Haystack, with the whole valley below.',
  assets:['routes/mount-si/route.js','routes/mount-si/map.webp','routes/mount-si/cover-photo.webp','routes/mount-si/cover-3d.webp','routes/mount-si/mount-si.gpx']
    .concat(['from-the-valley','haystack-cliffs','summit-boulders','rainier-from-si','valley-view','i90-from-si','si-and-river'].map(n=>'routes/mount-si/photos/'+n+'.webp'))},
 {id:'enchantments', go:[47.52777,-120.82083,'Stuart Lake trailhead (start)'], goEnd:[47.54415,-120.70969,'Snow Lakes trailhead (finish)'], file:'routes/enchantments/route.js', peak:'Enchantments', title:'Enchantments traverse', variant:'Stuart Lake to Snow Lakes', size:'Long',
  place:'Alpine Lakes Wilderness, near Leavenworth, WA', type:'Point to point', done:'Walked Sept 22, 2026',
  km:29.8, up:1957, hi:2387, moving:645, breaks:110, cover:'routes/enchantments/photos/05.webp',
  coverCredit:['Prusik Peak and the Temple. Buidhe, CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Prusik_Peak_and_the_Temple_from_near_Perfection_Lake_(11_October_2024).jpg'],
  blurb:'Colchuck Lake, Aasgard Pass and the Core lakes, then the long way down past Snow and Nada Lakes.',
  assets:['routes/enchantments/route.js','routes/enchantments/map.webp','routes/enchantments/enchantments-sep22-milestones.gpx']
    .concat(['01','02','03','04','05','06','07','08'].map(n=>'routes/enchantments/photos/'+n+'.webp'))}
];

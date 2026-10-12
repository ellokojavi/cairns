# Cairns

An installable, offline day-hike planner. Cairns are the piles of stones that mark the way.

Live at **https://ellokojavi.github.io/cairns/**

Pick a route, set the date, start time and forecast, and Cairns times every stop, the
turnaround cutoffs and the finish against sunset (or a parking gate that closes before
dark). On the trail it checks you in from GPS and re-times the rest from your real pace.
It works with no signal: the pages, maps and photos are stored on the phone, and GPS
keeps working because position comes from satellites, not the network.

## Routes

| Route | Type | Distance | Climb | Moving time* |
|---|---|---|---|---|
| Mailbox Peak: New Trail | Out and back | 15.9 km | +1,219 m | 5:45 |
| Mailbox Peak: Old Trail | Out and back | 7.5 km | +1,207 m | 4:30 |
| Mount Si (main trail) | Out and back | 12.2 km | +989 m | 4:30 |
| Enchantments traverse | Point to point | 29.8 km | +1,957 m | 10:45 |

\* At the pace the group walked the Enchantments; on the day it re-times from your real pace.

## What it does

**Before the hike**
- Route picker with a photo cover, key numbers, one-tap Google Maps directions to the
  parking, and a link to rehearse the route in test mode.
- Plan by date: sunrise, sunset and dusk computed for the trailhead on that day.
- **Your day:** with a connection, an hourly forecast (Open-Meteo) for the trailhead and
  the high point at their own heights; every stop's temperature at the time you pass it;
  what to bring and what to leave at home, each with its reason (water, food, headlamp,
  layers, rain gear, microspikes by freezing level, sun, wind, poles). Saved for offline.
- **What hikers say:** a short summary of trip reports and reviews, with links.
- Download the route's GPX for a watch or a map app.

**On the trail**
- Schedule for every stop, re-timed from check-ins and GPS; turnaround cutoffs that move
  earlier if you slow down; finish time against sunset or the parking gate.
- GPS does the check-ins: one cheap fix when you open the phone, or continuous tracking
  where an off-route warning is worth the battery. Manual check-in stays as a fallback.
- Map with every milestone named and timed; each stop's close-up frames the whole leg
  into it, with your position; elevation profiles for the route and each leg.
- Out-and-back routes draw the way up and the way down apart (map, profile, stop list),
  and tell them apart on GPS even though the trail is the same.
- Milestone photos (Creative Commons, credited), intake reminders, notes per stop.

**Test mode**
- `planner.html?r=<route>&sim=1` (linked from each card): a simulated GPS walker and a
  clock that runs up to 300×. Jump to any stop, change the pace, step off the trail.
  Its check-ins are kept apart from real ones.

## Install on a phone

- **Android (Chrome):** open the link → menu (⋮) → *Add to Home screen* / *Install app*.
- **iPhone (Safari, it must be Safari):** open the link → Share → *Add to Home Screen*.

Wait until the strip at the top reads **"Every route works in Airplane mode"** before
leaving signal. Open the route once with signal the night before, so the day's forecast
is saved.

## Files

| File | Purpose |
|---|---|
| `index.html` | Route picker: covers, key numbers, directions, test-mode links, offline status |
| `planner.html` | The planner: schedule, map, profiles, day brief, cutoffs, GPS check-ins |
| `sim.js` | Test mode: simulated clock and GPS |
| `routes/catalog.js` | The list of routes, parking coordinates, and every file each needs offline |
| `routes/<area>/` | Each route's data file, map, covers, photos and milestone GPX |
| `sw.js` | Service worker: stores every route for offline use |
| `manifest.webmanifest`, `cairns-*.png`, `logo.png`, `logo-dark.png` (same-size stones with a wide, diffuse sage-green glow for dark mode), `favicon.png` | App name, home-screen icons (regular, Android adaptive, iPhone) and logo |
| `tools/` | Scripts that build a route from OpenStreetMap trails and USGS lidar |
| `.github/workflows/photo-search.yml` | Creative Commons photo search, run on GitHub Actions |

## Adding a route

See `tools/README.md` for the steps and what every route must include, and `CLAUDE.md`
for the data sources that work from the build environment. In short: trails from
OpenStreetMap (Overture Maps), elevation from USGS 3DEP 1 m lidar, a rendered topo map
and 3D view, Creative Commons photos, hikers' comments, and the GPS walk tests.

## Publishing

GitHub Pages serves `main` from the repository root (Settings → Pages). `.nojekyll`
stops GitHub from processing the files. When publishing a change, bump `BUILD` in both
`planner.html` and `sw.js` (same value): installed copies then show "A newer version is
ready".

Keep this README current: update it with every significant change.

## Credits

Terrain: USGS 3DEP (public domain). Trails: © OpenStreetMap contributors, via Overture
Maps (ODbL). Weather: Open-Meteo (CC BY 4.0). Photos: Wikimedia Commons, credited on each
photo.

© 2026 · by El Loko Javi

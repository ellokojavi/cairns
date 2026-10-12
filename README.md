# Cairns

Installable, offline hike planner: piles of stones that mark the way. Pick a route, set the date, start time and forecast,
and it times every stop, the turnaround cutoffs and the finish against sunset (or a
parking gate). On the trail it checks you in from GPS and re-times the rest from your
real pace. Works with no signal; GPS keeps working because position comes from
satellites, not the network.

Routes:

- **Mailbox Peak, New Trail** (long): 15.9 km out and back, +1,219 m.
- **Mailbox Peak, Old Trail** (short): 7.5 km out and back, +1,207 m.
- **Enchantments traverse**: 29.8 km, Stuart Lake to Snow Lakes. Walked Sept 22, 2026.

## Publish

Repository **Settings → Pages** → Source: **Deploy from a branch**, Branch: **main**,
Folder: **/ (root)**. The site appears at `https://ellokojavi.github.io/cairns/`.
`.nojekyll` stops GitHub Pages from processing the files.

## Install on a phone

**Android (Chrome):** open the link → menu (⋮) → *Add to Home screen* / *Install app*.
**iOS (Safari — must be Safari):** open the link → Share → *Add to Home Screen*.

Wait until the strip at the top reads **"Every route works in Airplane mode"** before
leaving signal.

## Files

| File | Purpose |
|---|---|
| `index.html` | Route picker, with a cover and the key numbers for each route |
| `planner.html` | The planner: schedule, map, elevation, intake, cutoffs, GPS check-ins |
| `routes/catalog.js` | The list of routes, and every file each one needs offline |
| `routes/<area>/` | Each route's data file, map, cover, photos and milestone GPX |
| `sw.js` | Service worker: stores every route for offline use |
| `manifest.webmanifest`, `icon-*.png` | Makes it installable as an app |
| `tools/` | Scripts that build a route from OpenStreetMap trails and USGS lidar |

Adding a route: see `tools/README.md`. Data sources that work from the build environment: `CLAUDE.md`.

When publishing a change, bump `BUILD` in both `planner.html` and `sw.js` (same value):
installed copies then show "A newer version is ready".

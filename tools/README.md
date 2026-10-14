# Building a new route

Each route is one data file, `routes/<area>/<name>.js`, that sets `window.ROUTE`,
plus its map image, cover and milestone GPX. List it in `routes/catalog.js` and the
picker, the planner and the offline cache all pick it up.

Every new route must have, before it ships:
- `go` in its catalog entry: `[lat, lon, label]` of the **parking**, for one-tap Google
  Maps directions (point-to-point routes also get `goEnd` for the finish).
- `at`: the hike's AllTrails page (the path after `alltrails.com/`; find it with WebSearch
  limited to alltrails.com), linked as "Open in AllTrails" under its card. Also `pass` and `hl`
  for the picker's filters.
- `reviews` in its route data: 4–6 points summarised (paraphrased, never copied) from
  WTA trip reports and review sites, plus their links in `sources`.
- Photos and a photo cover with credits (see CLAUDE.md), and a 3D view at the trailhead.
- A pass of test mode (`?sim=1`) and the scripted checks: the dot inside the next stop's
  close-up along the whole track, and the noisy GPS walk.
The day brief (forecast, what to bring) needs nothing per route: it uses the trailhead,
the high point and the schedule.

Shared helpers live in `tools/routekit.py` (track, timing, photos with credits, writing the
route and GPX); `build_west_tiger_3.py` is the shortest worked example. `render_map.py` takes a JSON config (bounds, parking, labels):
see `map-config-mount-si.json`.

The Mailbox Peak routes were made with these scripts (Python 3; `pip install pyarrow
rasterio shapely pyproj networkx scipy matplotlib pillow`). They run in a scratch
folder; only `build_mailbox.py` writes into the repo.

| Step | Script | Source |
|---|---|---|
| Trails, streams, peaks in a bounding box | `fetch_overture.py transportation segment seg.parquet` (also `base water`, `base land`) | Overture Maps on AWS S3 (OpenStreetMap data, ODbL) |
| 1 m lidar terrain for a lon/lat box, resampled to 2 m | `fetch_lidar_area.py <project> <lon0> <lat0> <lon1> <lat1>` (project `13` = the ~10 m DEM, where there is no lidar) | USGS 3DEP (public domain) |
| Trailhead → goal track, with elevation | `route_track.py <name> <start lon> <lat> <end lon> <lat> "<Trail A>,<Trail B>"` (prefers the named trails; prints the junctions' names) | `seg.parquet` + `dem2m.tif` |
| Older, route-specific versions of the two steps above | `trail_graph.py`, `route_tracks.py`, `fetch_lidar.py` (Mailbox), `route_track_mount_si.py`, `fetch_lidar_mount_si.py` | |
| Wider 10 m terrain for the cover's horizon | `fetch_dem_wide.py [<tiles, e.g. n48w122,n48w123> <west E> <north N>]` | USGS 3DEP 1/3 arc-second |
| Topo map: relief, contours, trails, labels | `render_map.py` | the above |
| Cover: perspective view with the route on it | `render_cover.py <name> <cam lon> <cam lat> <cam m> <aim offset m> <pitch°> [<goal lon> <goal lat>]` (positive pitch tilts the view down) | the above |
| Route files, GPX, leg times | `build_mailbox.py <scratch dir> routes/mailbox`, `build_mount_si.py <scratch dir> routes/mount-si <photo candidates>`, `build_little_bandera.py`, `build_west_tiger_3.py`, `build_teneriffe_falls.py`, `build_wallace_falls.py` (all `<scratch dir> routes/<id> <photo candidates>`) | the above |

The picker's overview map (`routes/overview.webp`) comes from `render_overview.py`: USGS 10 m
relief at ~40 m per pixel (3600 px wide, so it holds up when zoomed in), Overture water and highways
for the box in `OVERVIEW` (`routes/catalog.js`). Each route's catalog entry also needs `pass`
(`discover` or `nwfp`) and `hl` (highlights: `summit`, `waterfall`, `lakes`) for the picker's filters. A route
inside that box needs nothing; one outside it means widening the box in both places and re-rendering.

Leg times use the model the group's Enchantments plan fits: 5 km/h on the flat,
+700 m/h climbing, and descents at 3000 / 1500 / 900 m/h for grades under 15%,
15–30% and over 30%.

What a route file holds: `trk` (track, delta-encoded lat/lon ×1e5, elevation, distance),
`si` (track index of each stop), `stops` (name, moving minutes `mv` and break `b` for the
leg into it, `note`, `take` tags, optional `gate:'turn'|'commit'`, `pace`, `wind`),
`map` (`src`, `w`, `h`, pixel trace `pts` with the stop number as a third value, and
`route:true` when the image has no line printed on it), `lat`/`lon`/`tz` for sun times,
`dep`, `climate` (forecast defaults), `deadline` (`dark`, or a parking `gate` that closes
before dusk), optional `photos`, `text` and an `intake()` hook.

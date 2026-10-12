# Building a new route

Each route is one data file, `routes/<area>/<name>.js`, that sets `window.ROUTE`,
plus its map image, cover and milestone GPX. List it in `routes/catalog.js` and the
picker, the planner and the offline cache all pick it up.

Every new route must have, before it ships:
- `go` in its catalog entry: `[lat, lon, label]` of the **parking**, for one-tap Google
  Maps directions (point-to-point routes also get `goEnd` for the finish).
- `reviews` in its route data: 4–6 points summarised (paraphrased, never copied) from
  WTA trip reports and review sites, plus their links in `sources`.
- Photos and a photo cover with credits (see CLAUDE.md), and a 3D view at the trailhead.
- A pass of test mode (`?sim=1`) and the scripted checks: the dot inside the next stop's
  close-up along the whole track, and the noisy GPS walk.
The day brief (forecast, what to bring) needs nothing per route: it uses the trailhead,
the high point and the schedule.

Shared helpers live in `tools/routekit.py`; `build_mailbox.py` and `build_mount_si.py`
are worked examples. `render_map.py` takes a JSON config (bounds, parking, labels):
see `map-config-mount-si.json`.

The Mailbox Peak routes were made with these scripts (Python 3; `pip install pyarrow
rasterio shapely pyproj networkx scipy matplotlib pillow`). They run in a scratch
folder; only `build_mailbox.py` writes into the repo.

| Step | Script | Source |
|---|---|---|
| Trails, streams, peaks in a bounding box | `fetch_overture.py transportation segment seg.parquet` (also `base water`, `base land`) | Overture Maps on AWS S3 (OpenStreetMap data, ODbL) |
| Trail network graph | `trail_graph.py` | the segments above |
| Trailhead → summit tracks, with elevation | `route_tracks.py` | graph + `dem2m.tif` |
| 1 m lidar terrain, resampled to 2 m | `fetch_lidar.py` | USGS 3DEP, King County 2021 (public domain) |
| Wider 10 m terrain for the cover's horizon | `fetch_dem_wide.py` | USGS 3DEP 1/3 arc-second |
| Topo map: relief, contours, trails, labels | `render_map.py` | the above |
| Cover: perspective view with the route on it | `render_cover.py <new\|old> <cam lon> <cam lat> <cam m> <aim offset m> <pitch°>` | the above |
| Route files, GPX, leg times | `build_mailbox.py <scratch dir> routes/mailbox`, `build_mount_si.py <scratch dir> routes/mount-si <photo candidates>` | the above |

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

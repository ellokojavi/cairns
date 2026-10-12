# Notes for Claude: building new routes

Read this before researching a new route. It records which data sources actually work
from the cloud container, so the next route starts with them instead of re-probing.
Add to it whenever a new source proves useful (or stops working). How a route is built,
step by step: `tools/README.md`.

## Network reality (Claude Code cloud container, last checked 2026-10-12)

Blocked (proxy 403, or DNS fails for WebFetch too): alltrails.com, openverse.org, flickr, openstreetmap.org,
overpass-api.de, tile servers (OSM, OpenTopoMap, CyclOSM, Stadia, ArcGIS), wikimedia /
commons / upload.wikimedia.org, wta.org, caltopo.com, flickr, imgur, unsplash, mapillary,
unpkg, jsdelivr, epqs / basemap.nationalmap.gov, opentopodata, geofabrik.
WebFetch does not get around it (same DNS failure). Don't spend time retrying these;
ask the user for AllTrails GPX or photos only if the sources below can't cover it.

Open, and enough to build a route:
- **AWS S3** (anonymous): Overture Maps, USGS 3DEP, Mapzen terrain tiles, Sentinel-2.
- **PyPI** (pip) and **npm**: tooling.
- **raw.githubusercontent.com**, **api.github.com**: files in public repos.
- **WebSearch**: text facts only (distances, gate hours, permits, hazards). It returns
  summaries, not files.
- **GitHub Actions** in this repo: open internet. Use a workflow (push-triggered, it
  commits its results back to the branch) for anything the container can't reach.
- Not useful: YFCC100M (`multimedia-commons` on S3) has the images but no public
  metadata with coordinates; iNaturalist open data (S3) is wildlife close-ups.

## First-choice sources

| Need | Source | How |
|---|---|---|
| Trail geometry, names, roads, streams, peaks | **Overture Maps** (OpenStreetMap data, ODbL), bucket `overturemaps-us-west-2`, region us-west-2. Releases listed at `https://overturemaps-us-west-2.s3.amazonaws.com/?list-type=2&prefix=release/&delimiter=/` (use the newest) | `tools/fetch_overture.py <theme> <type> out.parquet` with pyarrow S3FileSystem (anonymous, `proxy_options` from `$HTTPS_PROXY`), bbox filter on `bbox.xmin/xmax/ymin/ymax`. Themes: `transportation/segment` (trails: class path/footway/track, `names.primary`), `base/water` (streams), `base/land` (class `peak` with names). ~10 s per query. DuckDB does NOT work (its httpfs extension download is blocked) |
| Elevation, US, best | **USGS 3DEP 1 m lidar**, bucket `prd-tnm` (`https://prd-tnm.s3.amazonaws.com`). Projects under `StagedProducts/Elevation/1m/Projects/`, e.g. `WA_KingCounty_2021_B21`, `WA_EasternCascades_2019_B19`, `WA_CentralWildfire_D22`. Tiles `USGS_1M_<utmzone>_x<E/10000>y<N/10000>_<project>.tif` (the name is the tile's top-left corner) | rasterio over `/vsicurl/` with `GDAL_HTTP_PROXY=$HTTPS_PROXY`, `CURL_CA_BUNDLE=/root/.ccr/ca-bundle.crt`, `GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR`. COGs with overviews: windowed reads take seconds. See `tools/fetch_lidar.py` |
| Elevation, US, everywhere (~10 m) | **USGS 3DEP 1/3 arc-second**: `StagedProducts/Elevation/13/TIFF/current/n<lat>w<lon>/USGS_13_n<lat>w<lon>.tif` (named by the NW corner, e.g. n48w122 covers 47–48 N, 121–122 W) | WarpedVRT to UTM. See `tools/fetch_dem_wide.py`. Also used for the far terrain in covers |
| Elevation, worldwide fallback | Mapzen/Tilezen terrarium tiles: `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png` (height = R*256 + G + B/256 − 32768) | Not used yet |
| Satellite imagery (10 m) | Sentinel-2 COGs, bucket `sentinel-cogs` (us-west-2) | Not used yet: could add a true-colour backdrop. NAIP (`naip-visualization`) is 403 |
| Facts: length, gain, junctions, water, gates, permits, hazards | WebSearch on WTA, Hiking Project, 10Adventures, Wikipedia, SummitPost | Cross-check numbers. OSM tracks read ~10% shorter than GPS-recorded totals, which is normal |
| Map and cover images | Render them, don't download: `tools/render_map.py` (relief, contours, trails, labels, from lidar + Overture) and `tools/render_cover.py` (perspective view with the route drawn on it) | Label fonts around 20 px on a ~1700 px map, or they are unreadable on a phone |
| Photos for milestones and covers | **Creative Commons search on GitHub Actions** (the runner has open internet): Wikimedia Commons by category, text search and geosearch around the route, plus Openverse | Do this yourself, without asking first. Write `tools/photo-requests/<route>.json` (queries, Commons categories, `[lat, lon, radius_m]` points) and push: `.github/workflows/photo-search.yml` runs `tools/fetch_photos.py` and commits 1024 px candidates with author and licence to `tools/photo-candidates/<route>/`. Pull, drop off-topic hits (same-name places elsewhere, DPLA scans), then build a gallery artifact with the photos inlined and a "Use for" picker per photo. Do not leave the choice to the user: they often do not know where on the route a photo was taken. Look at every candidate yourself, choose by sharpness, light and how clearly it shows the place (titles, descriptions and geotags say where), wire your picks into the app with credits, and preselect them in the gallery so the user only adjusts. Covers need a visible credit too (`coverCredit` in `routes/catalog.js`). After wiring, delete `tools/photo-candidates/<route>/` (it is ~40 MB). Openverse returned nothing new for Mailbox; Commons had 50 usable photos |

## Gotchas found the hard way

- Out-and-back routes: the same spot is on the track twice. `snap()` in `planner.html`
  already handles it; re-run the GPS walk test (Playwright, mocked geolocation, ±25 m
  noise) for any new out-and-back or loop route.
- Place stops by elevation or distance along the track (`at_ele`, `at_km` in
  `tools/build_mailbox.py`), not by hand-typed coordinates.
- Parking with a gate (common on WA DNR land): use `deadline:{kind:'gate'}` so the
  cutoffs count back from the gate, not from dark.
- Python reading downloaded data: run with `python3 -I`, from a scratch folder.

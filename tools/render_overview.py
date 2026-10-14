"""Overview map for the route picker: shaded relief of the region every route sits in, with water and
the main highways. Labels and trailhead dots are drawn by index.html on top, so they stay sharp and
follow the theme.

  python3 render_overview.py <out.webp>
Bounds are the OV constant below; index.html carries the same numbers (OVERVIEW in routes/catalog.js).
Reads the USGS 3DEP 1/3 arc-second tiles (their overviews, ~80 m) and Overture Maps (water, motorways
and trunk roads) straight from S3; takes a few minutes.
"""
import os, sys, math, json, numpy as np, rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from affine import Affine
from urllib.parse import urlparse
import pyarrow.fs as pfs, pyarrow.dataset as ds, pyarrow.compute as pc, shapely.wkb as wkb
from PIL import Image, ImageDraw
os.environ.update(GDAL_HTTP_PROXY=os.environ['HTTPS_PROXY'], CURL_CA_BUNDLE='/root/.ccr/ca-bundle.crt', GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR')
OV = dict(w=-122.50, e=-120.55, s=47.33, n=47.99)
W = int(os.environ.get("OV_W", 3600)); H = round(W * (OV['n'] - OV['s']) / ((OV['e'] - OV['w']) * math.cos(math.radians((OV['n'] + OV['s']) / 2))))
T = Affine((OV['e'] - OV['w']) / W, 0, OV['w'], 0, -(OV['n'] - OV['s']) / H, OV['n'])
z = np.full((H, W), np.nan, 'f4')
for t in ['n48w123', 'n48w122', 'n48w121']:
    src = rasterio.open(f'/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/{t}/USGS_13_{t}.tif')
    with WarpedVRT(src, crs='EPSG:4326', transform=T, width=W, height=H, resampling=Resampling.average, src_nodata=src.nodata, nodata=np.nan) as v:
        b = v.read(1); z = np.where(np.isnan(z) & ~np.isnan(b), b, z)
z = np.nan_to_num(z, nan=0)
print('dem', z.shape, z.min(), z.max())
mx = (OV['e'] - OV['w']) / W * 111320 * math.cos(math.radians(47.66)); my = (OV['n'] - OV['s']) / H * 110540
gy, gx = np.gradient(z, my, mx); slope = np.arctan(np.hypot(gx, gy) * 1.6); asp = np.arctan2(-gx, gy)
az, alt = math.radians(315), math.radians(42)
hs = np.clip(math.sin(alt) * np.cos(slope) + math.cos(alt) * np.sin(slope) * np.cos(az - asp), 0, 1)
stops = [(0, (205, 222, 196)), (300, (190, 212, 180)), (900, (200, 210, 178)), (1500, (222, 218, 196)), (2100, (240, 238, 232))]
rgb = np.stack([np.interp(z, [s[0] for s in stops], [s[1][c] for s in stops]) for c in range(3)], -1)
img = np.clip(rgb * (0.5 + 0.6 * hs)[..., None], 0, 255)
sea = z <= 0.5
img[sea] = (168, 200, 222)
im = Image.fromarray(img.astype('uint8'))
dr = ImageDraw.Draw(im)
px = lambda lo, la: ((lo - OV['w']) / (OV['e'] - OV['w']) * W, (OV['n'] - la) / (OV['n'] - OV['s']) * H)
p = urlparse(os.environ['HTTPS_PROXY'])
fs = pfs.S3FileSystem(anonymous=True, region='us-west-2', proxy_options=f'{p.scheme}://{p.hostname}:{p.port}')
REL = 'overturemaps-us-west-2/release/2026-09-23.1'
box = (pc.field('bbox', 'xmin') > OV['w']) & (pc.field('bbox', 'xmax') < OV['e']) & (pc.field('bbox', 'ymin') > OV['s']) & (pc.field('bbox', 'ymax') < OV['n'])
def lines(g):
    return [g] if g.geom_type in ('LineString', 'Polygon') else list(getattr(g, 'geoms', []))
wt = ds.dataset(f'{REL}/theme=base/type=water/', filesystem=fs, format='parquet').to_table(
    filter=box & pc.field('class').isin(['lake', 'reservoir', 'river', 'ocean', 'bay', 'sound']), columns=['class', 'geometry', 'subtype'])
print('water', wt.num_rows)
for r in wt.to_pylist():
    g = wkb.loads(r['geometry'])
    for gg in lines(g):
        if gg.geom_type == 'Polygon':
            if gg.area < 2e-6: continue
            dr.polygon([px(*c) for c in gg.exterior.coords], fill=(168, 200, 222))
        elif r['class'] == 'river':
            dr.line([px(*c) for c in gg.coords], fill=(120, 168, 205), width=round(2 * W / 1800))
rd = ds.dataset(f'{REL}/theme=transportation/type=segment/', filesystem=fs, format='parquet').to_table(
    filter=box & pc.field('class').isin(['motorway', 'trunk']), columns=['class', 'geometry'])
print('roads', rd.num_rows)
segs = [(r['class'], [px(*c) for c in wkb.loads(r['geometry']).coords]) for r in rd.to_pylist()]
f = W / 1800   # line widths were tuned on an 1800 px map
for wdt, col in [(6, (150, 120, 96)), (3, (250, 236, 200))]:
    for c, pts in segs: dr.line(pts, fill=col, width=round((wdt if c == 'motorway' else wdt - 1) * f), joint='curve')
im.save(sys.argv[1], quality=80, method=6)
print(json.dumps(dict(OV, W=W, H=H)))

"""USGS 3DEP 1 m lidar for a lon/lat box, resampled to 2 m: dem2m.tif in the current folder.

  python3 fetch_lidar_area.py <project> <lon0> <lat0> <lon1> <lat1>
Projects and their tile naming: see CLAUDE.md (King County: WA_KingCounty_2021_B21;
Snohomish foothills: WA_Western_North_2016, but its tiles around Wallace Falls are empty).
Tiles are 10 km, named by their top-left corner. Project '13' uses the 1/3 arc-second (~10 m)
DEM instead, warped to the same 2 m UTM grid, for places without lidar.
"""
import os, sys, math, rasterio
from rasterio.merge import merge
from pyproj import Transformer
os.environ.update(GDAL_HTTP_PROXY=os.environ['HTTPS_PROXY'], CURL_CA_BUNDLE='/root/.ccr/ca-bundle.crt',
                  GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif')
proj = sys.argv[1]; lo0, la0, lo1, la1 = map(float, sys.argv[2:6])
fw = Transformer.from_crs(4326, 26910, always_xy=True)
E0, N0 = fw.transform(lo0, la0); E1, N1 = fw.transform(lo1, la1)
E0, N0, E1, N1 = [round(v, -1) for v in (E0 - 200, N0 - 200, E1 + 200, N1 + 200)]
if proj == '13':
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    from affine import Affine
    tile = f'n{math.ceil(max(la0, la1))}w{math.ceil(-min(lo0, lo1))}'
    src = rasterio.open(f'/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/{tile}/USGS_13_{tile}.tif')
    W, H = int((E1 - E0) / 2), int((N1 - N0) / 2)
    with WarpedVRT(src, crs='EPSG:26910', transform=Affine(2, 0, E0, 0, -2, N1), width=W, height=H, resampling=Resampling.cubic) as v:
        a = v.read(1).astype('float32')
    print(tile, a.shape, a.min(), a.max())
    with rasterio.open('dem2m.tif', 'w', driver='GTiff', height=H, width=W, count=1, dtype='float32', crs='EPSG:26910',
                       transform=Affine(2, 0, E0, 0, -2, N1), compress='deflate', nodata=-9999) as d: d.write(a, 1)
    sys.exit()
stem = 'USGS_one_meter' if proj.endswith('2016') or proj.endswith('2017') or proj.endswith('2014') or proj.endswith('2015') else 'USGS_1M_10'
tiles = [f'x{x}y{y}' for x in range(int(E0 // 1e4), int(E1 // 1e4) + 1) for y in range(int(N0 // 1e4) + 1, int(N1 // 1e4) + 2)]
base = f'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/{proj}/TIFF'
srcs = [rasterio.open(f'/vsicurl/{base}/{stem}_{t}_{proj}.tif') for t in tiles]
arr, tr = merge(srcs, bounds=(E0, N0, E1, N1), res=2); a = arr[0]
print(tiles, a.shape, (a < -1000).sum(), a[a > -1000].min(), a.max())
with rasterio.open('dem2m.tif', 'w', driver='GTiff', height=a.shape[0], width=a.shape[1], count=1, dtype='float32',
                   crs=srcs[0].crs, transform=tr, compress='deflate', nodata=srcs[0].nodata) as d: d.write(a, 1)

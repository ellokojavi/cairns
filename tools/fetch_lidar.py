import os, rasterio, numpy as np
from rasterio.windows import from_bounds
from rasterio.merge import merge
os.environ.update(GDAL_HTTP_PROXY=os.environ['HTTPS_PROXY'],CURL_CA_BUNDLE='/root/.ccr/ca-bundle.crt',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif')
# UTM10 bounds of the map area (route + margin)
E0,N0,E1,N1=597200,5255600,604600,5260400
srcs=[rasterio.open(f'/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/WA_KingCounty_2021_B21/TIFF/USGS_1M_10_{t}_WA_KingCounty_2021_B21.tif') for t in ['x59y526','x60y526']]
for s in srcs: print(s.bounds,s.crs.to_epsg(),s.res,s.overviews(1))
arr,tr=merge(srcs,bounds=(E0,N0,E1,N1),res=2)
a=arr[0]; print(a.shape,np.nanmin(a),np.nanmax(a), (a<-1000).sum())
with rasterio.open('dem2m.tif','w',driver='GTiff',height=a.shape[0],width=a.shape[1],count=1,dtype='float32',crs=srcs[0].crs,transform=tr,compress='deflate',nodata=srcs[0].nodata) as d: d.write(a,1)

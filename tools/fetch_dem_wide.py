import os,rasterio,numpy as np
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from affine import Affine
os.environ.update(GDAL_HTTP_PROXY=os.environ['HTTPS_PROXY'],CURL_CA_BUNDLE='/root/.ccr/ca-bundle.crt',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR')
src=rasterio.open('/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/n48w122/USGS_13_n48w122.tif')
R=15; E0,N1=582000,5274000; W=H=int(36000/R)
T=Affine(R,0,E0,0,-R,N1)
with WarpedVRT(src,crs='EPSG:26910',transform=T,width=W,height=H,resampling=Resampling.bilinear) as v:
  a=v.read(1)
print(a.shape,a.min(),a.max())
with rasterio.open('wide15.tif','w',driver='GTiff',height=H,width=W,count=1,dtype='float32',crs='EPSG:26910',transform=T,compress='deflate') as d: d.write(a.astype('float32'),1)

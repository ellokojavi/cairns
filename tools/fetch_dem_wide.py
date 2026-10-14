import os,sys,rasterio,numpy as np
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from affine import Affine
os.environ.update(GDAL_HTTP_PROXY=os.environ['HTTPS_PROXY'],CURL_CA_BUNDLE='/root/.ccr/ca-bundle.crt',GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR')
# optional: <tiles, e.g. n48w122,n48w123> <west E> <north N> (UTM 10N); defaults are the Mailbox/Si area
T13,E0,N1=(sys.argv[1].split(','),float(sys.argv[2]),float(sys.argv[3])) if len(sys.argv)>3 else (['n48w122'],582000,5274000)
R=15; W=H=int(36000/R)
T=Affine(R,0,E0,0,-R,N1)
a=np.full((H,W),np.nan,'f4')
for t in T13:
  src=rasterio.open(f'/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/{t}/USGS_13_{t}.tif')
  with WarpedVRT(src,crs='EPSG:26910',transform=T,width=W,height=H,resampling=Resampling.bilinear,src_nodata=src.nodata,nodata=np.nan) as v:
    b=v.read(1); a=np.where(np.isnan(a)&~np.isnan(b),b,a)
a=np.nan_to_num(a,nan=0)
print(a.shape,a.min(),a.max())
with rasterio.open('wide15.tif','w',driver='GTiff',height=H,width=W,count=1,dtype='float32',crs='EPSG:26910',transform=T,compress='deflate') as d: d.write(a.astype('float32'),1)

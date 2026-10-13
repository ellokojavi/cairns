import json, numpy as np, rasterio, pyarrow.parquet as pq, shapely.wkb as w
from rasterio.windows import from_bounds
from pyproj import Transformer
from scipy import ndimage
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
import os,sys
CFG=json.load(open(sys.argv[1])) if len(sys.argv)>1 else {}
fw=Transformer.from_crs(4326,26910,always_xy=True)
# map frame in UTM 10N metres
B=CFG.get('bounds',[-121.6790,47.4568,-121.6325,47.4718])
X0,Y0=fw.transform(B[0],B[1]); X1,Y1=fw.transform(B[2],B[3])
X0,Y0,X1,Y1=[round(v,-1) for v in (X0,Y0,X1,Y1)]
MPP=2.0; W=int((X1-X0)/MPP); H=int((Y1-Y0)/MPP)
print('frame',X0,Y0,X1,Y1,W,H)
dem=rasterio.open('dem2m.tif')
win=from_bounds(X0,Y0,X1,Y1,dem.transform)
z=dem.read(1,window=win,out_shape=(H,W),resampling=rasterio.enums.Resampling.bilinear).astype('f8')
z[z<-100]=np.nan
if np.isnan(z).any(): z=np.where(np.isnan(z),ndimage.generic_filter(np.nan_to_num(z,nan=np.nanmean(z)),np.mean,3),z)
# hillshade
gy,gx=np.gradient(z,MPP); slope=np.arctan(np.hypot(gx,gy)); asp=np.arctan2(-gx,gy)
az,alt=np.radians(315),np.radians(45)
hs=np.sin(alt)*np.cos(slope)+np.cos(alt)*np.sin(slope)*np.cos(az-asp); hs=np.clip(hs,0,1)
# tint: low forest green -> sub-alpine -> rock
stops=[(250,(196,219,186)),(600,(178,207,166)),(1000,(196,214,170)),(1250,(222,220,190)),(1500,(236,232,222))]
def tint(e):
  out=np.zeros(e.shape+(3,))
  for c in range(3):
    out[...,c]=np.interp(e,[s[0] for s in stops],[s[1][c] for s in stops])
  return out
rgb=tint(z)/255
shade=0.55+0.55*hs
img=np.clip(rgb*shade[...,None],0,1)
fig=plt.figure(figsize=(W/100,H/100),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off')
ax.imshow(img,extent=(0,W,H,0),interpolation='bilinear')
xs=np.arange(W)+.5; ys=np.arange(H)+.5
zs=ndimage.gaussian_filter(z,2)
ax.contour(xs,ys,zs,levels=np.arange(200,2000,20),colors='#8a6a45',linewidths=.6,alpha=.55)
cs=ax.contour(xs,ys,zs,levels=np.arange(300,2000,100),colors='#7a5530',linewidths=1.5,alpha=.75)
ax.clabel(cs,fmt=lambda v:f'{int(v)}',fontsize=15,inline=True,inline_spacing=2,colors='#6b4a28')
def px(lon,lat):
  x,y=fw.transform(lon,lat); return (x-X0)/MPP,(Y1-y)/MPP
def line(g,**kw):
  gs=[g] if g.geom_type=='LineString' else list(getattr(g,'geoms',[]))
  for gg in gs:
    if gg.geom_type!='LineString': continue
    p=[px(*c) for c in gg.coords]; ax.plot([a for a,b in p],[b for a,b in p],**kw)
halo=[pe.withStroke(linewidth=5,foreground=(1,1,1,.85))]
for r in pq.read_table('water.parquet').to_pylist():
  g=w.loads(r['geometry'])
  if g.geom_type in ('Polygon','MultiPolygon'):
    for poly in ([g] if g.geom_type=='Polygon' else g.geoms):
      p=[px(*c) for c in poly.exterior.coords]; ax.fill([a for a,b in p],[b for a,b in p],color='#9cc7e6',lw=0)
  else: line(g,color='#4f93c8',lw=2.6 if r['class'] in ('river',) else 1.6,alpha=.9)
for r in pq.read_table('seg.parquet').to_pylist():
  g=w.loads(r['geometry']); c=r['class']
  if c in ('path','footway','track','steps','bridleway','cycleway'):
    line(g,color='#5b3a1e',lw=2.0,ls=(0,(4,2.5)),alpha=.85)
  elif c in ('unclassified','residential','tertiary','secondary','primary'):
    line(g,color='#8c8c8c',lw=6,solid_capstyle='round'); line(g,color='#fbfbf5',lw=4,solid_capstyle='round')
  elif c=='service':
    line(g,color='#9a9a9a',lw=3.6); line(g,color='#f4f4ee',lw=2)
for r in pq.read_table('land.parquet').to_pylist():
  if r['class']=='peak' and r['names']:
    g=w.loads(r['geometry']); x,y=px(g.x,g.y)
    if 0<x<W and 0<y<H:
      ha="center" if 90<x<W-90 else ("right" if x>=W-90 else "left")
      ax.plot(x,y,marker='^',color='#3d2b1f',ms=16,mec='white',mew=2)
      n=r['names']['primary']
      if n in CFG.get('skip_peaks',['Mailbox Peak']): continue          # the planner labels the summit itself
      e=z[int(min(H-1,y)),int(min(W-1,x))]
      ax.text(x+(8 if ha=="left" else -8 if ha=="right" else 0),y-22,f"{n}\n{e:,.0f} m",ha=ha,multialignment=ha,va='bottom',fontsize=22,weight='bold',color='#2b1d12',path_effects=halo)
# trail labels and trailhead
x,y=px(*CFG.get('parking',[-121.6731,47.4668])); ax.text(x-30,y+2,'P',fontsize=24,weight='bold',color='white',ha='center',va='center',bbox=dict(boxstyle='round,pad=0.2',fc='#1f5fa8',ec='white'))
pass #ax.text(x-30,y+40,'Trailhead\n267 m',fontsize=20,weight='bold',ha='center',va='top',color='#1f2a30',path_effects=halo)
for txt,lon,lat,rot in CFG.get('trail_labels',[('New Trail',-121.6585,47.4665,28),('Old Trail',-121.6615,47.4628,-4)]):
  x,y=px(lon,lat); ax.text(x,y,txt,fontsize=20,style='italic',weight='bold',color='#5b3a1e',rotation=rot,ha='center',path_effects=halo)
for txt,lon,lat,rot in CFG.get('water_labels',[('Middle Fork Snoqualmie River',-121.6650,47.4735,17)]):
  x,y=px(lon,lat); ax.text(x,y,txt,fontsize=19,style='italic',color='#2d6ea3',rotation=rot,ha='center',path_effects=halo)
# scale bar
sx,sy=W-40-500/MPP,H-30
ax.plot([sx,sx+500/MPP],[sy,sy],color='#222',lw=5); ax.text(sx+250/MPP,sy-12,'500 m',ha='center',fontsize=19,weight='bold',path_effects=halo)
ax.text(10,H-10,'Terrain: USGS 3DEP 1 m lidar · Trails: © OpenStreetMap contributors (Overture Maps)',fontsize=13,color='#333',path_effects=halo)
ax.annotate('N',xy=(W-40,22),xytext=(W-40,90),ha='center',fontsize=22,weight='bold',arrowprops=dict(arrowstyle='-|>',color='#222',lw=2),path_effects=halo)
fig.savefig('map.png',dpi=100)
json.dump({'X0':X0,'Y0':Y0,'X1':X1,'Y1':Y1,'MPP':MPP,'W':W,'H':H},open('frame.json','w'))

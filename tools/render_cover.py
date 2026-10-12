"""Perspective terrain render (voxel-space) from LiDAR + 3DEP, with the route drawn on it."""
import json,sys,math,numpy as np,rasterio
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFilter
from pyproj import Transformer
fw=Transformer.from_crs(4326,26910,always_xy=True)
def load(p,step=1):
  d=rasterio.open(p);a=d.read(1).astype('f4');T=d.transform
  if step>1: a=a[::step,::step];T=T*T.scale(step)
  a[a<-100]=np.nan
  return a,T
near,TN=load('dem2m.tif',2)            # 4 m
wide,TW=load('wide15.tif')
def prep(a,res):
  m=np.isnan(a); a2=np.where(m,np.nanmedian(a),a)
  gy,gx=np.gradient(a2,res); slope=np.arctan(np.hypot(gx,gy)); asp=np.arctan2(-gx,gy)
  return a2,m,slope,asp
NA,NM,NS,NAsp=prep(near,4.0); WA,WM,WS,WAsp=prep(wide,15.0)
def sample(x,y):
  out=np.zeros(x.shape+(3,),'f4')   # h, slope, aspect
  h=np.full(x.shape,np.nan,'f4'); s=np.zeros(x.shape,'f4'); a=np.zeros(x.shape,'f4')
  for A,M,S,AS,T in [(WA,WM,WS,WAsp,TW),(NA,NM,NS,NAsp,TN)]:
    inv=~T; c,r=inv*(x,y)
    ok=(c>=0)&(r>=0)&(c<A.shape[1]-1)&(r<A.shape[0]-1)
    ci=np.clip(c,0,A.shape[1]-1.001); ri=np.clip(r,0,A.shape[0]-1.001)
    c0=ci.astype(int); r0=ri.astype(int); fx=ci-c0; fy=ri-r0
    hv=(A[r0,c0]*(1-fx)*(1-fy)+A[r0,c0+1]*fx*(1-fy)+A[r0+1,c0]*(1-fx)*fy+A[r0+1,c0+1]*fx*fy)
    ok&=~M[r0,c0]
    h=np.where(ok,hv,h); s=np.where(ok,S[r0,c0],s); a=np.where(ok,AS[r0,c0],a)
  return np.nan_to_num(h,nan=0),s,a
def render(cam,target,camz,W=1200,H=675,fov=55,pitch=0.0,sun=(240,28),route=None,out='pano.png',mark=None):
  cx,cy=cam; tx,ty=target
  yaw=math.atan2(ty-cy,tx-cx)
  f=(W/2)/math.tan(math.radians(fov/2))
  cols=np.arange(W)+.5-W/2; ang=np.arctan(cols/f)
  ds=np.concatenate([np.arange(15,400,2.0),400*np.power(1.0035,np.arange(0,1200))]); ds=ds[ds<28000]
  th=yaw+ang
  X=cx+np.cos(th)[:,None]*ds[None,:]; Y=cy+np.sin(th)[:,None]*ds[None,:]
  h,s,a=sample(X,Y)
  dp=ds[None,:]*np.cos(ang)[:,None]                      # perpendicular depth
  curv=ds[None,:]**2/(2*6371000)*0.87                     # earth curvature + refraction
  yproj=H/2 - f*((h-curv-camz)/dp) - f*math.tan(pitch)
  cm=np.minimum.accumulate(yproj,axis=1)
  # colour per sample
  az,alt=math.radians(sun[0]),math.radians(sun[1])
  shade=np.clip(np.sin(alt)*np.cos(s)+np.cos(alt)*np.sin(s)*np.cos(az-(math.pi/2-a)),0,1)
  stops=[(0,(70,105,70)),(400,(62,98,60)),(900,(70,104,62)),(1250,(110,118,88)),(1450,(150,145,128)),(1800,(205,205,205))]
  e=h; base=np.stack([np.interp(e,[q[0] for q in stops],[q[1][k] for q in stops]) for k in range(3)],-1)
  rock=np.clip((s-0.75)/0.35,0,1)[...,None]
  base=base*(1-rock)+np.array([128,124,116])*rock
  col=base*(0.35+0.95*shade[...,None])
  haze=1-np.exp(-ds/9000.0); hazec=np.array([178,198,214])
  col=col*(1-haze[None,:,None])+hazec*haze[None,:,None]
  img=np.zeros((H,W,3),'f4'); depth=np.full((H,W),1e9,'f4')
  rows=np.arange(H)+.5
  for c in range(W):
    idx=np.searchsorted(-cm[c],-rows,side='left')     # first sample whose cumulative-min y <= row
    vis=idx<len(ds)
    ii=np.minimum(idx,len(ds)-1)
    img[vis,c]=col[c,ii[vis]]; depth[vis,c]=ds[ii[vis]]
  # sky
  t=(rows/H)[:,None]; sky=np.array([108,150,196])*(1-t)+np.array([214,226,234])*t
  skym=depth>=1e9
  img[skym]=np.broadcast_to(sky[:,None,:],(H,W,3))[skym]
  im=Image.fromarray(np.clip(img,0,255).astype('uint8'))
  if route:
    pts=[]
    for lo,la,el in route:
      x,y=fw.transform(lo,la); dx,dy=x-cx,y-cy
      fwd=dx*math.cos(yaw)+dy*math.sin(yaw); side=-dx*math.sin(yaw)+dy*math.cos(yaw)
      if fwd<20: pts.append(None);continue
      u=W/2+f*side/fwd; v=H/2-f*((el+3-camz)/fwd)-f*math.tan(pitch)
      ok=0<=u<W and 0<=v<H and depth[int(v),int(u)]>=math.hypot(dx,dy)-60
      pts.append((u,v) if ok else None)
    dr=ImageDraw.Draw(im)
    for wdt,colr in [(7,(255,255,255)),(4,(214,52,30))]:
      for p,q in zip(pts,pts[1:]):
        if p and q and abs(p[0]-q[0])<40: dr.line([p,q],fill=colr,width=wdt)
  if mark:
    dr=ImageDraw.Draw(im)
    for lo,la,el in mark:
      x,y=fw.transform(lo,la); dx,dy=x-cx,y-cy
      fwd=dx*math.cos(yaw)+dy*math.sin(yaw); side=-dx*math.sin(yaw)+dy*math.cos(yaw)
      if fwd<=0: continue
      u=W/2+f*side/fwd; v=H/2-f*((el-camz)/fwd)-f*math.tan(pitch)
      dr.ellipse([u-7,v-7,u+7,v+7],fill=(255,255,255),outline=(30,30,30),width=3)
  im.save(out); return im
if __name__=='__main__':
  nm=sys.argv[1]
  j=json.load(open(f'{nm}_oneway.json'))
  route=[(a,b,e) for (a,b),e in zip(j['ll'],j['el'])]
  S=fw.transform(-121.6392795,47.4624091)
  cam=fw.transform(*map(float,sys.argv[2:4])); camz=float(sys.argv[4])
  render(cam,(S[0]+float(sys.argv[5]),S[1]),camz,pitch=math.radians(float(sys.argv[6])),route=route,out=f'cover_{nm}.png')

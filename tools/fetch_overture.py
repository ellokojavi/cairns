import os,sys,json,time, pyarrow.fs as pfs, pyarrow.dataset as ds, pyarrow.compute as pc
from urllib.parse import urlparse
p=urlparse(os.environ['HTTPS_PROXY'])
fs=pfs.S3FileSystem(anonymous=True,region='us-west-2',proxy_options=f"{p.scheme}://{p.hostname}:{p.port}")
theme,typ,out=sys.argv[1],sys.argv[2],sys.argv[3]
X0,Y0,X1,Y1=[float(v) for v in os.environ.get("BBOX","-121.74,47.44,-121.61,47.52").split(",")]
d=ds.dataset(f'overturemaps-us-west-2/release/2026-09-23.1/theme={theme}/type={typ}/',filesystem=fs,format='parquet')
f=(pc.field('bbox','xmin')>X0)&(pc.field('bbox','xmax')<X1)&(pc.field('bbox','ymin')>Y0)&(pc.field('bbox','ymax')<Y1)
cols=[c for c in ['id','names','class','subtype','geometry','bbox'] if c in d.schema.names]
t=time.time()
tb=d.to_table(filter=f,columns=cols)
print(tb.num_rows,time.time()-t)
import pyarrow.parquet as pq; pq.write_table(tb,out)

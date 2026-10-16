import sys, json, math, pickle
sys.path.insert(0,'.')
import numpy as np
import generate as G
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from scipy import ndimage
from PIL import Image, ImageDraw
from plug.testcase import params as P
import trimesh

G.FAST=True
models=G.source_models("laserscan", 1.0)   # 1 mm = 1 m (1:1000)
d=P.dims(); k_=P.kass_dims()
KW=k_["cw"]+2*P.KASS_CLR_T; KL=(d["y_kass1"]-d["y_kass0"])+2*P.KASS_CLR_T
HNEED=d["box_top"]+0.8
print("Schacht %.2f x %.2f, Hmin %.2f"%(KW,KL,HNEED))
RES=0.2
def polys_of(g):
    if g.is_empty: return []
    return list(g.geoms) if hasattr(g,'geoms') else [g]
def usable(slug,k):
    solid,fp,_=models[slug]
    z=HNEED/k
    cs=solid.slice(z)
    pg=cs.to_polygons()
    if not pg: return Polygon()
    g=None
    for ring in pg:
        r=Polygon(ring)
        g=r if g is None else g.symmetric_difference(r)
    return g.buffer(0).intersection(fp.buffer(0.01))
def raster(poly,bounds):
    minx,miny,maxx,maxy=bounds
    W=int((maxx-minx)/RES)+2; H=int((maxy-miny)/RES)+2
    im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
    for p in polys_of(poly):
        dr.polygon([((x-minx)/RES,(y-miny)/RES) for x,y in p.exterior.coords],fill=1)
        for r in p.interiors:
            dr.polygon([((x-minx)/RES,(y-miny)/RES) for x,y in r.coords],fill=0)
    return np.array(im,float)
def fits(poly,w,l,angles=range(0,180,5)):
    """gibt (ok, angle, cx, cy) in Modellmetern"""
    if poly.is_empty: return None
    b=poly.bounds; pad=max(w,l)
    bounds=(b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad)
    m=raster(poly,bounds)
    best=None
    for a in angles:
        r=ndimage.rotate(m,a,reshape=True,order=0)
        sx=max(1,int(round(w/RES))); sy=max(1,int(round(l/RES)))
        e=ndimage.uniform_filter(r,size=(sy,sx),mode='constant')>0.9999
        if e.any():
            iy,ix=np.argwhere(e)[len(np.argwhere(e))//2]
            # zurückrechnen
            h,wd=r.shape; ch,cw=h/2,wd/2
            dx,dy=(ix-cw),(iy-ch)
            th=math.radians(a)
            H0,W0=m.shape
            # ndimage.rotate dreht um die Bildmitte; Rückdrehung
            ox=dx*math.cos(th)-dy*math.sin(th)  # Näherung, nur für Zeichnung geprüft über shapely
            oy=dx*math.sin(th)+dy*math.cos(th)
            return True,a,(ix,iy,a,r.shape,m.shape,bounds)
    return False,None,None
res={}
ks={'1000':1.0,'1176':1000/1176.47,'1500':1000/1500}
rows={}
for slug in models:
    if slug.startswith('08'): continue
    solid,fp,_=models[slug]
    rows[slug]={}
    for kn,k in ks.items():
        u=usable(slug,k)
        # maximale Wand d, bei der der Schacht (KW+2d, KL+2d) noch hineinpasst
        dmax=None
        for dd in np.arange(0,6.01,0.2):
            ok=fits(u,(KW+2*dd)/k,(KL+2*dd)/k)
            if ok and ok[0]: dmax=float(dd)
            else: break
        rows[slug][kn]=dict(dmax=dmax, hmax=float(G.to_trimesh(solid).bounds[1][2]*k), area=float(fp.area*k*k))
    # kleinster Maßstabsfaktor mit d>=0.8
    lo,hi=0.5,1.3
    for _ in range(9):
        mid=(lo+hi)/2
        u=usable(slug,mid)
        ok=fits(u,(KW+1.6)/mid,(KL+1.6)/mid)
        if ok and ok[0]: hi=mid
        else: lo=mid
    rows[slug]['kmin']=hi
    print(slug,{kk:v for kk,v in rows[slug].items()})
json.dump(rows,open('/tmp/claude-0/-home-user-neues-augusteum-print/ddc1b5eb-0a61-5e7e-b4ef-e882b2c60d66/scratchpad/fit.json','w'),indent=1)

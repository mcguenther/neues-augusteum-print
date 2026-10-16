import sys, json, math
sys.path.insert(0,'.')
exec(open('/tmp/claude-0/-home-user-neues-augusteum-print/ddc1b5eb-0a61-5e7e-b4ef-e882b2c60d66/scratchpad/fit.py').read().split("res={}")[0])
from shapely.prepared import prep
from shapely import affinity
from shapely.geometry import box, Point
import innenhof
K=1000/1176.47
out={}
def rect_poly(cx,cy,w,l,a):
    r=box(-w/2,-l/2,w/2,l/2)
    return affinity.translate(affinity.rotate(r,a,origin=(0,0)),cx,cy)
for slug in models:
    if slug.startswith('08'): continue
    solid,fp,_=models[slug]
    u=usable(slug,K)
    best=None
    for dd in (1.2,0.8,0.4,0.0):
        w=(KW+2*dd)/K; l=(KL+2*dd)/K
        # Mittelpunkte: Raster 0,5 m
        pu=prep(u.buffer(1e-6))
        c0=fp.representative_point()
        cands=[]
        minx,miny,maxx,maxy=u.bounds
        for a in range(0,180,5):
            for x in np.arange(minx,maxx,0.5):
                for y in np.arange(miny,maxy,0.5):
                    if not u.contains(Point(x,y)): continue
                    if pu.contains(rect_poly(x,y,w,l,a)):
                        cands.append((math.hypot(x-fp.centroid.x,y-fp.centroid.y),a,x,y))
        if cands:
            cands.sort(); best=(dd,)+cands[0][1:]; break
    if best is None:
        out[slug]=None; print(slug,'keine Lage'); continue
    dd,a,x,y=best
    shaft=rect_poly(x,y,KW/K,KL/K,a)
    out[slug]=dict(d=dd,angle=a,cx=x,cy=y)
    print(slug,out[slug])
    pickle.dump(out,open('/tmp/claude-0/-home-user-neues-augusteum-print/ddc1b5eb-0a61-5e7e-b4ef-e882b2c60d66/scratchpad/place.pkl','wb'))
# Uniriese: größte Kassettenlänge bei Breite KW+1.6, Wand 0.8
slug='06_city_hochhaus'; u=usable(slug,K)
for L in np.arange(KL,10,-1.0):
    ok=fits(u,(KW+1.6)/K,(L+1.6)/K)
    if ok and ok[0]:
        print('Uniriese passt mit Schachtlänge',L); break

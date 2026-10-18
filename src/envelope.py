import math,json
from pathlib import Path
# Coordinates read from the vector geometry of ASGG Fig.8, CTBUH2013 p17.
# Coordinates are PDF-page points; these are outer envelope control points,
# excluding the colored unit partition lines and tiny entrance notches.
S=.255207423
ZREF=268.0 # source typical4m x67; early publication and final schedules differ
ang=[270,30,150];slopes=[3.0,3.6,3.3]
dirs=[(math.cos(math.radians(a)),math.sin(math.radians(a))) for a in ang]
tans=[math.tan(math.radians(a)) for a in slopes]
ends=[[(371.13,529.48),(449.09,529.48)],[(521.79,262.82),(561.04,330.27)],[(251.20,324.19),(289.32,258.36)]]
raw=[(sum(p[0] for p in e)/2*S,-sum(p[1] for p in e)/2*S) for e in ends]
rs=[p[0]*d[0]+p[1]*d[1]+ZREF*t for p,d,t in zip(raw,dirs,tans)]
R=sum(rs)/3
# Solve d_i dot center = r_i - R; angular normals sum to zero.
cx=sum(2/3*(r-R)*d[0] for r,d in zip(rs,dirs));cy=sum(2/3*(r-R)*d[1] for r,d in zip(rs,dirs))
def w(p):return (p[0]*S-cx,-p[1]*S-cy)
def bez(p0,p1,p2,p3,n=20):
 return [tuple((1-t)**3*p0[k]+3*(1-t)**2*t*p1[k]+3*(1-t)*t*t*p2[k]+t**3*p3[k] for k in (0,1)) for t in [j/n for j in range(n+1)]]
def sample(commands):
 pts=[]
 for cmd in commands:
  if len(cmd)==2:pts.append(cmd)
  else:pts.extend(bez(pts[-1],*cmd)[1:])
 return [w(p) for p in pts]
# Order in SVG clockwise: outer flat-ended wing, bowed side, next wing.
sides=[
 [(289.32,258.36),(366.55,294.19),[(380.38,300.67),(396.08,303.16),(409.50,303.69)],[(424.38,303.64),(440.21,301.14),(454.22,294.58)],(521.79,262.82)],
 [(561.04,330.27),(502.74,370.91),[(481.84,385.38),(470.70,404.75),(470.02,405.96)],[(457.32,428.69),(455.50,451.48),(455.40,452.91)],(449.09,529.48)],
 [(371.13,529.48),(365.36,452.87),[(363.06,425.0),(351.0,406.8),(350.27,406.47)],[(337.0,383.0),(319.0,371.8),(318.19,370.75)],(251.20,324.19)]]
curves=[sample(s) for s in sides]
def extend(p,q,i):
 d=dirs[i];vx,vy=p[0]-q[0],p[1]-q[1]
 u=(R-d[0]*p[0]-d[1]*p[1])/(d[0]*vx+d[1]*vy)
 return (p[0]+u*vx,p[1]+u*vy)
# side0 C->B; side1 B->A; side2 A->C
for c,(i,j) in zip(curves,[(2,1),(1,0),(0,2)]):
 c[0]=extend(c[0],c[1],i);c[-1]=extend(c[-1],c[-2],j)
base=[p for c in curves for p in c]
area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(base,base[1:]+base[:1]))/2
if area<0:base.reverse()
def clip(poly,d,lim):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa=a[0]*d[0]+a[1]*d[1]-lim;fb=b[0]*d[0]+b[1]*d[1]-lim
  if fa<=1e-9:out.append(a)
  if (fa<0)!=(fb<0):
   t=fa/(fa-fb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 clean=[]
 for p in out:
  if not clean or math.dist(p,clean[-1])>1e-7:clean.append(p)
 if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-7:clean.pop()
 return clean
def outline(z):
 p=base
 for d,t in zip(dirs,tans):p=clip(p,d,R-z*t)
 return p
def end_edges(z):
 p=outline(z);out={}
 for i,(d,t) in enumerate(zip(dirs,tans)):
  lim=R-z*t
  for k,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
   if abs(a[0]*d[0]+a[1]*d[1]-lim)<1e-6 and abs(b[0]*d[0]+b[1]*d[1]-lim)<1e-6:
    if i not in out or math.dist(a,b)>math.dist(*out[i][1]):out[i]=(k,(a,b))
 return p,out

# Source Fig.8 contour with planar end cuts. The previous local transverse
# deformation is removed: it changed the central facade near each wing end.
fixed_base=base[:]

def resampled_outline(z,N=240):
 p=outline(z);out=[]
 for j in range(N):
  d=(math.cos(2*math.pi*j/N),math.sin(2*math.pi*j/N));hits=[]
  for a,b in zip(p,p[1:]+p[:1]):
   vx,vy=b[0]-a[0],b[1]-a[1];det=d[1]*vx-d[0]*vy
   if abs(det)<1e-10:continue
   r=(a[1]*vx-a[0]*vy)/det;u=(d[0]*a[1]-d[1]*a[0])/det
   if r>=0 and -1e-7<=u<=1+1e-7:hits.append(r)
  if not hits:raise RuntimeError('Invalid footprint ray')
  r=min(hits);out.append((r*d[0],r*d[1]))
 return out

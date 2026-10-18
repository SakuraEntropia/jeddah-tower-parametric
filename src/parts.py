import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
import envelope as G
import common as C
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'parameters/model.json').read_text())
def mesh(name,v,f,mat,col,source,status='DERIVED'):
 # Explicitly triangulate every authored surface. Do not leave saddle quads
 # to the renderer's hidden tessellation (the v2 crown defect).
 ob=C.mesh(name,v,f,mat,col,source=source,status=status)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-10];bmesh.ops.delete(bm,geom=bad,context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 ob['scope']='V5 public-reference reconstruction; source and photo-fit dimensions distinguished';return ob

def sample_path(ps,N):
 ls=[0]
 for a,b in zip(ps,ps[1:]):ls.append(ls[-1]+math.dist(a,b))
 out=[];k=0
 for j in range(N+1):
  s=ls[-1]*j/N
  while k<len(ps)-2 and ls[k+1]<s:k+=1
  u=(s-ls[k])/max(1e-10,ls[k+1]-ls[k]);out.append(tuple(a+(b-a)*u for a,b in zip(ps[k],ps[k+1])))
 return out
cache={}
def sections(z,N=64):
 key=(z,N)
 if key in cache:return cache[key]
 p,es=G.end_edges(z);sides=[]
 for i in range(3):
  k,(a,b)=es[i];j=(k+1)%len(p);chain=[p[j]]
  while j not in [e[0] for e in es.values()]:
   j=(j+1)%len(p);chain.append(p[j])
   if len(chain)>len(p):raise RuntimeError('Bad contour chain')
  other=next(w for w,e in es.items() if e[0]==j)
  sides.append((i,other,sample_path(chain,N)))
 cache[key]=(sides,es);return sides,es

def norm_out(poly,j):
 a=poly[max(0,j-1)];b=poly[min(len(poly)-1,j+1)];dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy);return (dy/l,-dx/l)
def strip(name,lo,hi,mat,col,source,status='DERIVED',smooth=False):
 n=len(lo);ob=mesh(name,lo+hi,[(j,j+1,n+j+1,n+j) for j in range(n-1)],mat,col,source,status)
 if smooth:
  for f in ob.data.polygons:f.use_smooth=True
 return ob

def inside(p,poly):
 x,y=p;c=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:c=not c
 return c

def cdt_shell(name,outer,holes,mapper,thickness,mat,col,source):
 verts=[];edges=[]
 def loop(ps):
  k=len(verts);verts.extend(Vector(p) for p in ps);edges.extend((k+j,k+(j+1)%len(ps)) for j in range(len(ps)))
 # Mapping a four-corner UV loop left the curved boundaries as long
 # straight chords in V3. Sample every outer edge before triangulation.
 if len(outer)<=8:
  outer=[(a[0]+(b[0]-a[0])*j/40,a[1]+(b[1]-a[1])*j/40) for a,b in zip(outer,outer[1:]+outer[:1]) for j in range(40)]
 loop(outer)
 for h in holes:loop(h)
 # Interior samples control curvature, while boundaries preserve real holes.
 for u in range(1,40):
  for v in range(1,22):
   p=(u/40,v/22)
   if inside(p,outer) and not any(inside(p,h) for h in holes):verts.append(Vector(p))
 pts,_,fs,*_=delaunay_2d_cdt(verts,edges,[],0,1e-7,False)
 fs=[f for f in fs if inside(tuple(sum(pts[i][k] for i in f)/len(f) for k in [0,1]),outer) and not any(inside(tuple(sum(pts[i][k] for i in f)/len(f) for k in [0,1]),h) for h in holes)]
 used=sorted({i for f in fs for i in f});idx={a:b for b,a in enumerate(used)}
 vv=[mapper(*pts[i]) for i in used];ff=[tuple(idx[j] for j in f) for f in fs];N=len(vv)
 vv+= [(x,y,z-thickness) for x,y,z in vv];out=ff+[tuple(N+j for j in reversed(f)) for f in ff]
 counts={}
 for f in ff:
  for a,b in zip(f,f[1:]+f[:1]):counts.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 for es in counts.values():
  if len(es)==1:
   a,b=es[0];out.append((b,a,a+N,b+N))
 ob=mesh(name,vv,out,mat,col,source,'IMAGE_RECONSTRUCTED_CONTROL_SURFACE')
 for p in ob.data.polygons:p.use_smooth=True
 return ob

def beam(name,a,b,r,mat,col):return C.curves(name,[[a,b]],r,mat,col)
def closed_path(name,p,z0,z1,mat,col):return C.prism(name,p,z0,z1,mat,col,source='ASGG base reference',status='IMAGE_RECONSTRUCTED')

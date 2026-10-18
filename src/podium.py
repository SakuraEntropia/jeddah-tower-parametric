from parts import *
def triangle(R):
 points=[(R*math.cos(math.radians(a)),R*math.sin(math.radians(a))) for a in [270,30,150]];out=[]
 for j,b in enumerate(points):
  a=points[j-1];c=points[(j+1)%3];p=(b[0]+.15*(a[0]-b[0]),b[1]+.15*(a[1]-b[1]));q=(b[0]+.15*(c[0]-b[0]),b[1]+.15*(c[1]-b[1]))
  for k in range(17):
   t=k/16;out.append(((1-t)**2*p[0]+2*(1-t)*t*b[0]+t*t*q[0],(1-t)**2*p[1]+2*(1-t)*t*b[1]+t*t*q[1]))
 return out

def build():
 base=C.collection('07_Layered_podium');roofs=C.collection('08_Three_separate_lobby_canopies');lobby=C.collection('09_Sloped_lobby_glazing');land=C.collection('10_Landscape_and_ramps')
 # Distinct terraces and exposed concourse levels below the L1 arrival deck.
 for j,(R,z0,z1) in enumerate([(123,-11.5,-7.5),(117,-7.5,-3.5),(110,-3.5,2.5),(99,2.5,6)]):
  p=triangle(R);closed_path(f'Podium_slab_{j}',p,z1-.5,z1,'Stone',base)
  v=[];f=[];N=len(p)
  for k,(a,b) in enumerate(zip(p,p[1:]+p[:1])):
   zbot=z0+.5;ztop=z1-.65
   mesh(f'Concourse_glazing_{j}_{k}',[(*a,zbot),(*b,zbot),(*b,ztop),(*a,ztop)],[(0,1,2,3)],'Lobby_glass',base,'ASGG podium level/glazing image','IMAGE_RECONSTRUCTED')
   if k%4==0:C.box(f'Podium_stone_pier_{j}_{k}',(a[0],a[1],(z0+z1)/2),(.6,.6,z1-z0),'Stone',base)
 # Open paved arrival floor. The three roofs are independent swept patches.
 for i,other,inner in sections(20)[0]:
  n=(G.dirs[i][0]+G.dirs[other][0],G.dirs[i][1]+G.dirs[other][1]);ln=math.hypot(*n);n=(n[0]/ln,n[1]/ln)
  pi=(-G.dirs[i][1],G.dirs[i][0]);pj=(-G.dirs[other][1],G.dirs[other][0]);si=1 if sum(x*y for x,y in zip(pi,n))>0 else -1;sj=1 if sum(x*y for x,y in zip(pj,n))>0 else -1
  A=tuple(G.dirs[i][k]*75+pi[k]*si*8 for k in (0,1));B=tuple(G.dirs[other][k]*75+pj[k]*sj*8 for k in (0,1));control=(n[0]*64,n[1]*64)
  def innerp(u):
   s=u*(len(inner)-1);j=min(len(inner)-2,int(s));t=s-j;return tuple(a+(b-a)*t for a,b in zip(inner[j],inner[j+1]))
  def point(u,v):
   p=innerp(u);o=((1-u)**2*A[0]+2*u*(1-u)*control[0]+u*u*B[0],(1-u)**2*A[1]+2*u*(1-u)*control[1]+u*u*B[1]);rise=math.sin(math.pi*u)**2;zi=13+12*rise;zo=10.5+5*rise
   return((1-v)*p[0]+v*o[0],(1-v)*p[1]+v*o[1],(1-v)*zi+v*zo-2.5*math.sin(math.pi*v)*math.sin(math.pi*u))
  hole=[(.5+.14*math.cos(2*math.pi*j/96),.66+.145*math.sin(2*math.pi*j/96)) for j in range(96)]
  o=cdt_shell(f'Lobby_canopy_{i}_{other}',[(0,0),(1,0),(1,1),(0,1)],[hole],point,.55,'Roof',roofs,'ASGG drop_off, near_stairs and aerial images')
  o['roof_role']='independent lobby canopy; not a continuous radial cap'
  # Transparent oculus and clearly separated cross-ribs under its opening.
  hp=[point(*p) for p in hole];mesh(f'Canopy_{i}_{other}_oculus_glazing',[(x,y,z-.12) for x,y,z in hp],[tuple(range(len(hp)))],'Rail_glass',roofs,'ASGG grouped canopy rooflights','PHOTO_RECONSTRUCTED')
  for u in [.35,.40,.45,.50,.55,.60,.65]:
   f=math.sqrt(max(0,1-((u-.5)/.14)**2));v0=.66-.145*f;v1=.66+.145*f
   ps=[point(u,v0+(v1-v0)*j/12) for j in range(13)];C.curves(f'Rooflight_cross_rib_{i}_{u}',[[(x,y,z+.07) for x,y,z in ps]],.20,'Roof',roofs)
  # Sloped clear lobby facade sits below the canopy, leaving outer drop-off open.
  bottom=[];top=[]
  for j in range(65):
   u=j/64;b=point(u,.16);t=point(u,.23);bottom.append((b[0],b[1],6));top.append((t[0],t[1],t[2]-.7))
  strip(f'Sloped_lobby_cable_glass_{i}_{other}',bottom,top,'Lobby_glass',lobby,'ASGG drop_off image sloped lobby wall','PHOTO_RECONSTRUCTED',smooth=True)
  bars=[[a,b] for j,(a,b) in enumerate(zip(bottom,top)) if j%2==0];C.curves(f'Lobby_cable_mullions_{i}_{other}',bars,.035,'Frame',lobby)
  # V supports correspond to the exposed columns in the lobby photographs.
  for u in [.24,.76]:
   toppt=point(u,.87);foot=point(u,.70);foot=(foot[0],foot[1],6)
   beam(f'Canopy_oblique_support_{i}_{u}',foot,(toppt[0],toppt[1],toppt[2]-.65),.65,'Roof',lobby)
  outer=[point(j/96,1) for j in range(97)];C.curves(f'Thin_canopy_edge_{i}_{other}',[outer],.15,'Frame',roofs)
 # Rounded wing-end noses join the neighbouring canopy patches.
 for i in range(3):
  d=G.dirs[i];t=(-d[1],d[0]);a,b=G.end_edges(20)[1][i][1]
  if sum(a[k]*t[k] for k in (0,1))<sum(b[k]*t[k] for k in (0,1)):a,b=b,a
  def nose(u,v):
   inner=tuple(a[k]+u*(b[k]-a[k]) for k in (0,1));q=75+15*math.sin(math.pi*u);w=8*math.cos(math.pi*u);outer=tuple(d[k]*q+t[k]*w for k in (0,1))
   return tuple(inner[k]*(1-v)+outer[k]*v for k in (0,1))+(13*(1-v)+10.5*v,)
  cdt_shell(f'Rounded_wing_entry_nose_{i}',[(0,0),(1,0),(1,1),(0,1)],[],nose,.55,'Roof',roofs,'ASGG rounded connected wing-end canopy')
 # Curved vehicle ramp linking L1 arrival and B1/concourse. Image-derived path.
 path=[]
 for j in range(65):
  u=j/64;a=math.radians(175+86*u);r=102-9*u;path.append((r*math.cos(a),r*math.sin(a),6-9.5*(u*u*(3-2*u))))
 v=[];f=[];rails=[[],[]]
 for j,p in enumerate(path):
  a=Vector(path[max(0,j-1)]);b=Vector(path[min(len(path)-1,j+1)]);d=(b-a).normalized();n=Vector((-d.y,d.x,0)).normalized()
  for side in [-1,1]:v.append(tuple(Vector(p)+n*side*3.8));rails[(side+1)//2].append(tuple(Vector(p)+n*side*3.8+Vector((0,0,.85))))
 for j in range(len(path)-1):f.append((2*j,2*j+1,2*j+3,2*j+2))
 mesh('Descending_open_vehicle_ramp',v,f,'Paving',land,'ASGG near_stairs exposed ramp','PHOTO_RECONSTRUCTED');C.curves('Ramp_stone_guardrails',rails,.24,'Stone',land)
 # Small planting beds stay separate from the architectural surfaces.
 for k,p in enumerate(triangle(119)[::3]):
  x,y=p
  C.disk(f'Palm_bed_{k}',x,y,2.7,2.2,.35,'Planting',land,segments=12)
  C.curves(f'Palm_trunk_{k}',[[(x,y,2.8),(x+.5,y,9)]],.16,'Bark',land)
  fronds=[]
  for j in range(7):
   a=2*math.pi*j/7;fronds.append([(x+.5,y,9),(x+2*math.cos(a),y+2*math.sin(a),10.1),(x+3.8*math.cos(a),y+3.8*math.sin(a),8.8)])
  C.curves(f'Palm_fronds_{k}',fronds,.12,'Planting',land)
 return base,roofs,lobby,land

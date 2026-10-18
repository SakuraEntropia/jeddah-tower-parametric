from parts import *

ROWS=P['main_levels'];LEVELS=sorted({0,*[r['z_m'] for r in ROWS]})
N=96

def group_at(z,key):
 for lo,hi in P.get('balcony_groups_m',{}).get(key,[]):
  if lo<=z<hi:return lo,hi
 return None

def deck_at(z,key):
 g=group_at(z,key)
 if not g:return False
 # Author's alternate-floor cantilever balconies. Eight metre duplexes
 # have one actual slab, with no invented intermediate full floor.
 heights=[r['z_m'] for r in ROWS if g[0]<=r['z_m']<g[1]]
 j=min(range(len(heights)),key=lambda j:abs(heights[j]-z))
 return ROWS[next(i for i,r in enumerate(ROWS) if r['z_m']==heights[j])]['height']>=8 or j%2==0

def mask(u):
 def smooth(t):
  t=max(0,min(1,t));return t*t*(3-2*t)
 # Asymmetric withdrawal in XY: a broad flat bottom between two ramps.
 # This is neither a circle in plan nor an arch cut in elevation.
 return smooth((u-.08)/.42)*smooth((1-u)/.17)

def side(z,i,other,ps,kind):
 out=[];info=[]
 for j,p in enumerate(ps):
  wing,neighbor=(i,other) if j<=N//2 else (other,i)
  key=f'{"ABC"[wing]}_{"ABC"[neighbor]}';u=(j if j<=N//2 else N-j)/(N/2)
  active=group_at(z,key) is not None
  d=3.5*mask(u) if active else 0
  if kind=='slab' and deck_at(z,key):d*=.08
  n=norm_out(ps,j);out.append((p[0]-d*n[0],p[1]-d*n[1]))
  info.append((key,d,n,active,deck_at(z,key)))
 return out,info

def floor_plan(z):
 sides,ends=sections(z,N);out=[]
 for i,other,ps in sides:out.extend(side(z,i,other,ps,'slab')[0])
 return out

def build():
 facade=C.collection('01_Unitized_curtain_wall');bal=C.collection('02_Horizontal_slab_edge_balconies');floors=C.collection('03_Source_floor_stack');framing=C.collection('04_Facade_frames')
 horiz=[];vert=[];brec=[];slabrec=[]
 nterr=(math.cos(math.radians(330)),math.sin(math.radians(330)));tterr=(-nterr[1],nterr[0]);root=G.resampled_outline(630,360)[330]
 def portal(p,z):
  return 630<=z<638 and abs((p[0]-root[0])*tterr[0]+(p[1]-root[1])*tterr[1])<5.0 and abs((p[0]-root[0])*nterr[0]+(p[1]-root[1])*nterr[1])<5
 for r in ROWS:
  z=r['z_m'];poly=floor_plan(z)
  if r['level']==158:
   # Source matrix gives463m2, not a full floor. Its outline is absent.
   # Do not fill the observation entrance with the former invented full slab.
   slabrec.append({'level':158,'z':z,'area_source_m2':463,'xy_contour':None,'status':'PARTIAL_FLOOR_OMITTED_PENDING_PLAN'});continue
  o=C.prism(f'L{r["level"]:03d}_{z:.2f}m',poly,z-(4 if z==670 else .25),z,'Concrete',floors,source='AE-000A/B levels; CTBUH2013 slab-edge rule',status='SOURCE_LEVEL_PHOTO_FIT_NOTCHED_PLAN');o['source_level']=r['level'];o['slab_edge_is_notched_in_XY']=True
  slabrec.append({'level':r['level'],'z':z,'xy_contour':poly})
 for r in P['mezzanines']:
  z=r['z_m'];area=r['area_m2'];poly=G.outline(max(z,0));A=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2);sc=min(.92,math.sqrt(area/A))
  o=C.prism('PARTIAL_'+r['label'],[(x*sc,y*sc) for x,y in poly],z-.25,z,'Concrete',floors,source='AE matrix mezzanine area',status='SOURCE_AREA_FIT_PARTIAL_PLAN');o['source_label']=r['label']
 for k,(z0,z1) in enumerate(zip(LEVELS,LEVELS[1:])):
  low,es0=sections(z0,N);high,es1=sections(z1,N)
  for (i,other,ps0),(_,_,ps1) in zip(low,high):
   # A recessed glazing line runs behind projecting horizontal balcony slabs.
   a,inf=side(z0,i,other,ps0,'glass')
   # Use the same bay state at the top of this storey, preserving vertical
   # recessed glazing. The next storey may have a different slab edge.
   b=[]
   for j,p in enumerate(ps1):
    d=inf[j][1];n=norm_out(ps1,j);b.append((p[0]-d*n[0],p[1]-d*n[1]))
   lo=[(*p,z0+.04) for p in a];hi=[(*p,z1-.02) for p in b]
   # Group adjacent panels into a surface, breaking at the actual entrance.
   start=0
   for j in range(N):
    mid=tuple((a[j][h]+a[j+1][h])/2 for h in (0,1));skip=portal(mid,z0)
    if skip or j==N-1:
     end=j if skip else j+1
     if end>start:strip(f'Glass_{k}_{i}_{start}',lo[start:end+1],hi[start:end+1],'Glass',facade,'ASGG notched slab edge / Jangho panel principles')
     start=j+1
   # Geometry sampling is independent of the real 1.5m panel module.
   L=sum(math.dist(p,q) for p,q in zip(a,a[1:]));count=max(2,round(L/P['facade_nominal_horizontal_module_m']))
   aa=sample_path(a,count);bb=sample_path(b,count)
   for pa,pb in zip(aa,bb):
    if not portal(pa,z0):vert.append([(*pa,z0+.04),(*pb,z1-.02)])
   for j in range(N):
    if not portal(a[j],z0) and not portal(a[j+1],z0):horiz.append([lo[j],lo[j+1]])
   if z1-z0>4.5:
    for dz in range(4,int(z1-z0),4):
     u=dz/(z1-z0)
     horiz.append([tuple(x+(y-x)*u for x,y in zip(p,q)) for p,q in zip(lo,hi)])
   # The thin exposed floor surface is horizontal. No Z-varying arch caps.
   slab,si=side(z0,i,other,ps0,'slab');activeids=[]
   for j in range(N):
    if si[j][3] and si[j][4] and max(inf[j][1],inf[j+1][1])>.08:activeids.append(j)
   if activeids:
    vv=[];ff=[];rail_lo=[];rail_hi=[]
    for j in activeids:
     q=len(vv);vv.extend([(*slab[j],z0+.015),(*slab[j+1],z0+.015),(*a[j+1],z0+.015),(*a[j],z0+.015)]);ff.append((q,q+1,q+2,q+3))
     if inf[j][1]>.4:
      rail_lo.append((*slab[j],z0+.08));rail_hi.append((*slab[j],z0+1.16))
    mesh(f'Horizontal_balcony_paving_{k}_{i}',vv,ff,'Stone',bal,'CTBUH2013 dropping slab-edge cantilevers','HORIZONTAL_XY_NOTCH')
    if len(rail_lo)>1:
     strip(f'Balcony_glass_guard_{k}_{i}',rail_lo,rail_hi,'Rail_glass',bal,'ASGG balcony view')
     C.curves(f'Balcony_coping_{k}_{i}',[rail_hi],.025,'Frame',bal)
    brec.append({'z0':z0,'z1':z1,'side':[i,other],'construction':'horizontal slab contour; full-height setback glazing','depth_m':3.5,'alternating_floor':True})
  for i in range(3):
   a,b=es0[i][1];A,B=es1[i][1];lo=[(*a,z0),(*b,z0)];hi=[(*A,z1),(*B,z1)]
   strip(f'Inclined_planar_end_{i}_{k}',lo,hi,'Glass',facade,'Sinn/Weismantle constant end-wall inclinations');horiz.append(lo)
   count=max(2,round(math.dist(a,b)/1.5))
   for j in range(count+1):
    u=j/count;vert.append([(a[0]+u*(b[0]-a[0]),a[1]+u*(b[1]-a[1]),z0),(A[0]+u*(B[0]-A[0]),A[1]+u*(B[1]-A[1]),z1)])
 C.curves('Horizontal_40mm_joint_lines',horiz,.019,'Frame',framing);C.curves('Vertical_unitized_profiles',vert,.026,'Frame',framing)
 (ROOT/'reports/balcony_register.json').write_text(json.dumps(brec,indent=2));(ROOT/'reports/floor_contours.json').write_text(json.dumps(slabrec))
 return facade,bal,floors,framing

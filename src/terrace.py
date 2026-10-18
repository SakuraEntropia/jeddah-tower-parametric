from parts import *

def build():
 col=C.collection('06_Sky_terrace_L157');steel=C.collection('06b_Embedded_terrace_steel');a=math.radians(330);n=(math.cos(a),math.sin(a));t=(-n[1],n[0]);root=G.resampled_outline(630,360)[330];offset=18.;center=(root[0]+n[0]*offset,root[1]+n[1]*offset)
 def world(q,w,z):return(root[0]+n[0]*q+t[0]*w,root[1]+n[1]*q+t[1]*w,z)
 def polar(r,u,z):return(center[0]+r*math.cos(u+a),center[1]+r*math.sin(u+a),z)
 def round_loop(p):
  for k in range(2):
   p=[q for x,y in zip(p,p[1:]+p[:1]) for q in [(x[0]*.75+y[0]*.25,x[1]*.75+y[1]*.25),(x[0]*.25+y[0]*.75,x[1]*.25+y[1]*.75)]]
  return p
 # Twelve rounded annular trapezoids: real openings through the box deck.
 holes=[]
 for mid in [-1.24,0,1.24]:
  for shift in [-.36,-.12,.12,.36]:
   u=mid+shift;ps=[]
   for r,angles in [(8.2,[u-.094+(j/10)*.188 for j in range(11)]),(12.1,[u+.094-(j/10)*.188 for j in range(11)])]:
    ps.extend([polar(r,v,630)[:2] for v in angles])
   holes.append(round_loop(ps))
 outer=[polar(15,2*math.pi*j/240,630)[:2] for j in range(240)]
 deck=cdt_shell('L157_deck_with_ring_rooflights',outer,holes,lambda x,y:(x,y,630),1.15,'Roof',col,'ASGG sky_terrace_looking_up, aerial; JEC L157')
 for face in deck.data.polygons:face.use_smooth=False
 for h,p in enumerate(holes):
  mesh(f'Rounded_rooflight_glass_{h:02d}',[(x,y,629.86) for x,y in p],[tuple(range(len(p)))],'Rail_glass',col,'ASGG rounded annular rooflights','PHOTO_FIT_APERTURES')
  C.curves(f'Rooflight_recess_frame_{h:02d}',[[(x,y,629.9) for x,y in p+[p[0]]]],.055,'Frame',col)
 # A neck reaches six metres into the building. Its outer corners meet the
 # rear chord of the disk, rather than forcing half the disk through glass.
 neck=[world(-6,-5.3,630),world(9,-6.0,630),world(11,-4.5,630),world(11,4.5,630),world(9,6,630),world(-6,5.3,630)]
 C.prism('Embedded_entry_neck',[p[:2] for p in neck],628.85,630,'Roof',col,source='ASGG entrance / 33m max cantilever',status='PHOTO_FIT_EMBEDDED_NECK')
 # Solid triangular box haunch: the whole side profile is filled back to
 # the tower frame. V3 merely extruded a narrow curved ribbon at its edge.
 def bez2(ps,N=40):
  out=[]
  for j in range(N+1):
   u=j/N;out.append(tuple((1-u)**3*ps[0][k]+3*(1-u)**2*u*ps[1][k]+3*(1-u)*u*u*ps[2][k]+u**3*ps[3][k] for k in (0,1)))
  return out
 profile=bez2([(-5,594),(-2,601),(4,614),(8.5,620)])+bez2([(8.5,620),(11,625),(13.5,627.8),(24,629.08)])[1:]
 vv=[];ff=[]
 for q,z in profile:
  u=(z-594)/35.08;w=.22+2.6*u
  vv.extend([world(q,-w,z),world(q,w,z),world(-5.15,-w,z),world(-5.15,w,z)])
 for k in range(len(profile)-1):
  i=4*k;j=i+4;ff.extend([(i,i+1,j+1,j),(i+3,i+2,j+2,j+3),(i+2,i,j,j+2),(i+1,i+3,j+3,j+1)])
 k=4*(len(profile)-1);ff.extend([(0,2,3,1),(k,k+1,k+3,k+2)])
 haunch=mesh('Broad_closed_flared_haunch',vv,ff,'Roof',col,'ASGG terrace side and underside; Sinn central box-truss support','PHOTO_FIT_SOLID_SIDE_PROFILE')
 # Architectural metal cladding panels, with seams following the side face.
 for q,z in profile[8:-3:8]:
  u=(z-594)/35.08;w=.22+2.6*u
  C.curves('Haunch_cladding_joint',[[world(-5.1,-w-.018,z),world(q,-w-.018,z)],[world(-5.1,w+.018,z),world(q,w+.018,z)]],.012,'Frame',col)
 # Internal load path is separate and editable; cladding conceals it.
 for w in [-1.45,1.45]:
  pts=[world(-8,w,607),world(0,w,614),world(10,w,624),world(22,w,628.94)]
  C.curves('Embedded_box_truss_chord',[pts,[world(-8,w,629.1),world(22,w,629.1)]],.24,'Frame',steel)
  for k in range(3):beam('Spine_diagonal',pts[k],world([-8,0,10,22][k+1],w,629.1),.14,'Frame',steel)
 for q in [4,10,16,22]:
  half=min(13.5,math.sqrt(max(0,14.2**2-(q-18)**2))) if q>5 else 2.5
  beam('Transverse_plate_girder',world(q,-half,629.35),world(q,half,629.35),.19,'Frame',steel)
 # A smooth metal rim surrounds the dark soffit, with a recessed top coping.
 vv=[];ff=[];N=240
 for r,z in [(15,628.78),(15,630.02),(14.75,630.02),(14.75,628.78)]:
  vv.extend([polar(r,2*math.pi*j/N,z) for j in range(N)])
 for k in range(4):
  for j in range(N):ff.append((k*N+j,k*N+(j+1)%N,((k+1)%4)*N+(j+1)%N,((k+1)%4)*N+j))
 rim=mesh('Continuous_metal_disc_rim',vv,ff,'Frame',col,'ASGG silver terrace rim');
 for p in rim.data.polygons:p.use_smooth=True
 # Flat top stone, three curved paving joints, and a complete glass guard.
 for r in [7.6,12.9,14.45]:C.curves('Circular_paving_joint',[[polar(r,2*math.pi*j/240,630.012) for j in range(241)]],.009,'Soffit',col)
 for j in range(48):
  u=2*math.pi*j/48;lo=polar(14.65,u,630.08);hi=polar(14.65,u,631.14);beam('Guardrail_stanchion',lo,hi,.027,'Frame',col)
 points=[polar(14.65,2*math.pi*j/240,630.08) for j in range(241)];strip('Curved_clear_glass_guard',points,[(x,y,631.14) for x,y,z in points],'Rail_glass',col,'ASGG glass guard')
 C.curves('Thin_guardrail_coping',[[polar(14.65,2*math.pi*j/240,631.16) for j in range(241)]],.037,'Frame',col)
 # Portal stands at the real concave facade; tower.py suppresses all panels
 # and framing in this opening, including the formerly crossing mullions.
 C.curves('Entry_portal_frame',[[world(-.2,-5,630),world(-.2,-5,637.6),world(-.2,5,637.6),world(-.2,5,630)]],.085,'Frame',col)
 for w in [-2.4,0,2.4]:beam('Entry_door_stile',world(-.3,w,630),world(-.3,w,633.2),.04,'Frame',col)
 beam('Entry_door_header',world(-.3,-5,633.2),world(-.3,5,633.2),.05,'Frame',col)
 for w0,w1 in [(-5,-2.4),(-2.4,0),(0,2.4),(2.4,5)]:
  mesh('Observatory_clear_door',[world(-.33,w0,630),world(-.33,w1,630),world(-.33,w1,633.2),world(-.33,w0,633.2)],[(0,1,2,3)],'Rail_glass',col,'ASGG terrace entrance','PHOTO_FIT_ENTRY')
 # Low planted rear arc seen in the official aerial, kept clear of the neck.
 for j in range(27):
  u=1.82+j*2.64/26;p=polar(13.4,u,630.22);q=18+13.4*math.cos(u);w=13.4*math.sin(u)
  if q<10 and abs(w)<6.5:continue
  C.box('Low_planter_box',p,(1.1,.55,.40),'Stone',col,angle=u+a+math.pi/2)
  for dw in [-.30,0,.30]:
   pt=polar(13.4,u+dw/13.4,630.55);C.disk('Terrace_shrub',pt[0],pt[1],630.76,.32,.38,'Planting',col,segments=10)
 metadata={'root_xyz':[*root,630],'center_xyz':[*center,630],'side':'A/B concave facade','local_outward_azimuth_degrees':330,'diameter_m':30,'max_projection_m':33,'embedded_neck_back_m':6,'height_reference':'L157 630m source matrix','position_basis':'ASGG top / underside / side; JEC approximately33m projection','fit_limits':'support and aperture profiles fitted to public renderings, not fabrication CAD'}
 (ROOT/'reports/terrace_placement.json').write_text(json.dumps(metadata,indent=2));return col,metadata

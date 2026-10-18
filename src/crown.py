from parts import *

# Original RWDI1011301 SVG coordinates, pp119/125/131. Printed scale1:600:
# .12pt * 25.4/72 * 600/1000 = .0254m. No render-pixel estimation.
S=.0254;Z0=740.6-3980*S;TOP=1008.
SOURCE='RWDI1011301 original vector elevations1/3/5, Figures4d/6d/8d'
def lx(x0,y0,x1,y1,y):return x0+(x1-x0)*(y-y0)/(y1-y0)
def profiles():
 out=[]
 for v in range(3):
  delta=[0,9332-9219,9332-9226][v]
  def q(x,y):return (x,Z0+(y+delta)*S)
  dx=[2294,2290.5,2258.5][v]
  def u(x,y):return (x-dx,Z0+(9332+y-756)*S)
  y=(670-Z0)/S-delta
  if v==0:
   a=[q(lx(1143,3392,1218,9332,y),y),q(lx(2174,781,1669,9332,y),y),q(1669,9332),u(3969.987,756),u(3656.999,6059.993),u(3626.986,6059.993),u(3595.996,5958.008),u(3569.987,5804.004),u(3505.990,756),q(1218,9332)]
   c=[q(630,781),q(1143,781),q(1143,3392),q(1175,5894),q(833,6940),q(833,2110),q(662,1402)]
   branches=[a,c]
  elif v==1:
   a=[q(lx(633,737,1133,9219,y),y),q(lx(1645,5057,1593,9219,y),y),q(1645,5057),q(1593,9219),u(3884.993,756),u(3820.996,5804.004),u(3795.996,5958.008),u(3763.997,6059.993),u(3734.993,6059.993),u(3422.005,756),q(1133,9219)]
   c=[q(1485,737),q(2286,737),q(1991,6931),q(1987,6933),q(1976,6940),q(1485,3933)]
   branches=[a,c]
  else:
   a=[q(lx(1116,5701,1214,9226,y),y),q(lx(1736,3213,1569,9226,y),y),q(1736,3213),q(1569,9226),u(3830.013,756),u(3684.993,5958.008),u(3615.007,5958.008),u(3469.987,756),q(1214,9226),q(1116,5701)]
   c=[q(591,737),q(1391,737),q(1391,6940),q(1379,6934),q(1375,6931),q(743,3933)]
   b=[q(1391,737),q(2088,737),q(1922,3959),q(1882,3980),q(1391,1402)]
   branches=[a,c,b]
  out.append(branches)
 return out

def build():
 col=C.collection('05_Crown_from_three_original_elevations');ps=profiles();foot=G.outline(670);offsets=[];axes=[]
 for v,ang in enumerate([0,120,240]):
  t=(math.cos(math.radians(ang)),math.sin(math.radians(ang)));axes.append(t);xs=[]
  for p in ps[v]:
   for a,b in zip(p,p[1:]+p[:1]):
    if min(a[1],b[1])<=670<max(a[1],b[1]):xs.append(a[0]+(b[0]-a[0])*(670-a[1])/(b[1]-a[1]))
  vals=[x*t[0]+y*t[1] for x,y in foot];offsets.append((min(xs)+max(xs))*S/2-(min(vals)+max(vals))/2)
 def prism(name,polys,v):
  # First union the drawing regions in 2D. A 3D union of extruded regions
  # with coincident caps creates redundant internal faces at a shared edge.
  vv2=[];edges=[]
  loops=[[(x*S-offsets[v],z) for x,z in p] for p in polys]
  for p in loops:
   k=len(vv2);vv2.extend(Vector(q) for q in p);edges.extend((k+j,k+(j+1)%len(p)) for j in range(len(p)))
  points,_,faces,*_=delaunay_2d_cdt(vv2,edges,[],0,1e-8,False)
  faces=[f for f in faces if any(inside(tuple(sum(points[j][i] for j in f)/len(f) for i in (0,1)),p) for p in loops)]
  used=sorted({j for f in faces for j in f});ix={j:k for k,j in enumerate(used)};p=[points[j] for j in used];faces=[tuple(ix[j] for j in f) for f in faces]
  t=axes[v];n=(-t[1],t[0]);vv=[]
  for d in [-100,100]:vv.extend([(t[0]*x+n[0]*d,t[1]*x+n[1]*d,z) for x,z in p])
  N=len(p);ff=[tuple(reversed(f)) for f in faces]+[tuple(j+N for j in f) for f in faces];boundary={}
  for f in faces:
   for i,j in zip(f,f[1:]+f[:1]):boundary.setdefault(tuple(sorted((i,j))),[]).append((i,j))
  for es in boundary.values():
   if len(es)==1:
    i,j=es[0];ff.append((i,j,j+N,i+N))
  ob=mesh(name,vv,ff,'Glass',col,SOURCE,'DRAWING_VISUAL_HULL_NOT_FABRICATION_GEOMETRY')
  bm=bmesh.new();bm.from_mesh(ob.data);print('MASK',v,len(bm.verts),len(bm.faces),sum(not e.is_manifold for e in bm.edges),flush=True);bm.free();return ob
 def boolean(a,b,op):
  mod=a.modifiers.new(op,'BOOLEAN');mod.operation=op;mod.solver='EXACT';mod.object=b;bpy.context.view_layer.objects.active=a;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(b,do_unlink=True)
  bm=bmesh.new();bm.from_mesh(a.data);print('BOOL',op,len(bm.verts),len(bm.faces),sum(not e.is_manifold for e in bm.edges),flush=True);bm.free()
 masks=[prism('Elevation_'+str(v),branches,v) for v,branches in enumerate(ps)]
 ob=masks[0]
 for m in masks[1:]:boolean(ob,m,'INTERSECT')
 limit=C.box('Architectural_height_limit',(0,0,(670+TOP)/2),(220,220,TOP-670),'Concrete',col);boolean(ob,limit,'INTERSECT');ob.name='Connected_notched_spire_silo_670_1008m'
 plan_limit=C.prism('Source_Y_plan_vertical_limit',G.outline(670),670,1020,'Concrete',col,source='CTBUH2013 Fig8 projected upper envelope limit',status='SOURCE_PLAN_LIMIT');boolean(ob,plan_limit,'INTERSECT')
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob.data.materials.clear();ob.data.materials.append(C.MATS['Glass']);ob.data.materials.append(C.MATS['Frame'])
 for f in ob.data.polygons:
  f.use_smooth=False;f.material_index=0
  if min(ob.data.vertices[i].co.z for i in f.vertices)>962:f.material_index=1
 ob['source_pages']='119,125,131 (1-based PDF)';ob['source_raw_unit_m']=S;ob['registration']='translation only; source Fig8 plan at670m';ob['limitation']='intersection of three silhouettes; hidden surfaces underdetermined';ob['height_m']=TOP
 joints=[]
 for z in range(674,963,4):
  for face in ob.data.polygons:
   vs=[ob.data.vertices[i].co for i in face.vertices];hits=[]
   for a,b in zip(vs,vs[1:]+vs[:1]):
    if min(a.z,b.z)<=z<max(a.z,b.z):hits.append(a+(b-a)*((z-a.z)/(b.z-a.z)))
   if len(hits)==2 and (hits[0]-hits[1]).length>.03:joints.append([tuple(p+face.normal*.008) for p in hits])
 C.curves('Spire_horizontal_4m_panel_joints',joints,.018,'Frame',col)
 vertical=[]
 for face in ob.data.polygons:
  vs=[ob.data.vertices[i].co for i in face.vertices]
  h=Vector((-face.normal.y,face.normal.x,0))
  if h.length<.1:continue
  h.normalize();ds=[p.dot(h) for p in vs]
  for k in range(math.ceil(min(ds)/1.5),math.floor(max(ds)/1.5)+1):
   d=k*1.5;hits=[]
   for a,b,da,db in zip(vs,vs[1:]+vs[:1],ds,ds[1:]+ds[:1]):
    if min(da,db)<=d<max(da,db):hits.append(a+(b-a)*((d-da)/(db-da)))
   if len(hits)==2 and (hits[0]-hits[1]).length>.05:vertical.append([tuple(p+face.normal*.012) for p in hits])
 C.curves('Spire_nominal_1500mm_vertical_panel_joints',vertical,.018,'Frame',col)
 (ROOT/'reports/crown_source_register.json').write_text(json.dumps({'source':SOURCE,'pdf_pages':[119,125,131],'svg_unit_m':S,'z_origin':Z0,'offsets_m':offsets,'profiles_xraw_zm':ps,'height_user':TOP,'method':'intersection of unions of vector elevation silhouettes, constrained inside source Y-plan at670m','limitations':['hidden concave facade surfaces underdetermined','2011 RWDI envelope; 2013 floor schedule separate source']},indent=2))
 return col

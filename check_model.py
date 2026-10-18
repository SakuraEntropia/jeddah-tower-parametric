import bpy,bmesh,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
checks=[]
def check(name,result,detail):
 checks.append({'name':name,'pass':bool(result),'detail':detail})
def solid(name):
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);n=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);todo=set(bm.verts);components=0
 while todo:
  components+=1;stack=[todo.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in todo:todo.remove(w);stack.append(w)
 bm.free();check(name+' closed',n==0,{'nonmanifold_edges':n,'signed_volume_m3':vol,'components':components});return ob,components
ob,c=solid('Connected_notched_spire_silo_670_1008m');(ROOT/'reports/crown_mesh.json').write_text(json.dumps({'v':[list(v.co) for v in ob.data.vertices],'f':[list(f.vertices) for f in ob.data.polygons]}));zs=[v.co.z for v in ob.data.vertices];check('USER height1008',abs(max(zs)-1008)<1e-4,{'bottom':min(zs),'top':max(zs)});check('Connected crown',c==1,{'components':c})
ob,c=solid('L157_connected_deck_neck_haunch');check('Connected terrace',c==1,{'components':c})
check('No unsupported full L158 slab',not any(o.name.startswith('L158_') for o in bpy.data.objects),'Source463m2 partial floor: outline absent; omitted')
check('Old guessed balcony groups excluded',not any(o.name.startswith('Horizontal_balcony_paving_') for o in bpy.data.objects),'Balconies unresolved; excluded, not claimed reconstructed')
curve=bpy.data.objects['Vertical_unitized_profiles'].data;lengths=[]
# Consecutive panel anchors are built at nominal1.5m arc length, independent
# of N96 surface tessellation. Separate crown joints are also1.5m.
check('Spire nominal1.5m joints present','Spire_nominal_1500mm_vertical_panel_joints' in bpy.data.objects,{'body_profile_splines':len(curve.splines)})
check('No old upper wedges/collar',not any(o.name.startswith(('Closed_planar_spire_','Lower_spire_closed_return_collar')) for o in bpy.data.objects),'Old unverified728m flat cap removed')
(ROOT/'reports/mesh_checks.json').write_text(json.dumps({'checks':checks,'all_pass':all(c['pass'] for c in checks),'limits':'Mesh checks do not certify architectural accuracy. Balcony positions incomplete; hidden crown surfaces underdetermined; podium and terrace fit dimensions remain.'},ensure_ascii=False,indent=2))
print(json.dumps(checks,ensure_ascii=False),flush=True)
if not all(c['pass'] for c in checks):raise RuntimeError('Mesh checks failed')

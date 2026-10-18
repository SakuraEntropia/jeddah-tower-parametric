import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'src'))
import common as C
from parts import P,mesh
import tower,crown,terrace,podium
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='Jeddah_1008m_V5_reference_reconstruction';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
C.palette()
C.material('Glass',(.25,.39,.48),.48,.25,.06)
C.material('Roof',(.76,.78,.77),.52,.25)
C.material('Frame',(.48,.55,.58),.8,.23)
C.material('Backpan',(.12,.16,.18),.15,.45)
C.material('Lobby_glass',(.42,.55,.56),.20,.12,.5)
C.material('Soffit',(.37,.39,.38),.1,.55)
C.material('Human',(.30,.28,.25),0,.8)
C.material('Bark',(.28,.22,.15),0,.85)
print('BUILD notched horizontal floor contours and facade',flush=True);main=tower.build()
print('BUILD crown',flush=True);cr=crown.build()
print('BUILD terrace',flush=True);tr,td=terrace.build()
print('BUILD podium',flush=True);pod=podium.build()
# Final solid union: the haunch enters the deck by 0.25m, and the entry neck
# enters both the disk and tower. Keep a single connected support/deck mesh.
deck=bpy.data.objects['L157_deck_with_ring_rooflights'];neck=bpy.data.objects['Embedded_entry_neck'];haunch=bpy.data.objects['Broad_closed_flared_haunch']
bpy.context.view_layer.objects.active=deck;deck.select_set(True)
# The deck is already a closed solid with real aperture walls.
for part in [neck,haunch]:
 mod=deck.modifiers.new('Union_'+part.name,'BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=part
 bpy.context.view_layer.objects.active=deck;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(part,do_unlink=True)
# Triangulation after solid union avoids implicit nonplanar n-gons.
import bmesh
bm=bmesh.new();bm.from_mesh(deck.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(deck.data);bm.free();deck.data.update();deck.name='L157_connected_deck_neck_haunch'
deck.data.materials.append(C.MATS['Stone']);deck.data.materials.append(C.MATS['Soffit'])
for face in deck.data.polygons:
 face.use_smooth=False;face.material_index=len(deck.data.materials)-2 if face.normal.z>.9 else len(deck.data.materials)-1 if face.normal.z<-.9 else 0
# Subdued site, at a lower level to expose the real podium layers and ramps.
site=C.collection('11_Site');C.disk('Site_ground',0,0,-11.7,1500,1,'Paving',site,segments=128)
world=bpy.data.worlds.new('Blue_gray_studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.43,.52,.65,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;s.world=world
sun=bpy.data.lights.new('Sun','SUN');sun.energy=3.2;sun.angle=.08;ob=bpy.data.objects.new('Sun',sun);s.collection.objects.link(ob);ob.rotation_euler=(.35,-.6,.7)
# Broad reflector lights give the metal and glass spatially varying highlights.
for name,loc,energy,size,target in [('Key',(180,-170,400),2500000,180,(0,0,400)),('Fill',(-120,150,550),1800000,200,(0,0,550))]:
 light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='RECTANGLE';light.size=size;light.size_y=650;o=bpy.data.objects.new(name,light);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
ang=math.radians(30);n=Vector((math.cos(ang),math.sin(ang),0));tn=Vector((math.cos(math.radians(330)),math.sin(math.radians(330)),0));tt=Vector((-tn.y,tn.x,0));center=Vector(td['center_xyz'])
cams={}
cams['hero']=C.camera('CAM_Hero',tuple(n*1900+Vector((0,0,570))),(0,0,490),ortho=1120)
cams['balconies']=C.camera('CAM_Balconies',tuple(n*180+Vector((0,0,440))),(0,0,420),ortho=125)
cams['podium']=C.camera('CAM_Podium',tuple(n*240+Vector((0,0,145))),(0,0,12),ortho=265)
cams['podium_eye']=C.camera('CAM_Podium_eye',tuple(n*260+Vector((0,0,28))),(0,0,12),ortho=225)
cams['terrace_top']=C.camera('CAM_Terrace_top',tuple(center+tn*65+tt*25+Vector((0,0,52))),tuple(center+Vector((0,0,-2))),ortho=80)
cams['terrace_under']=C.camera('CAM_Terrace_under',tuple(center+tn*65+tt*28+Vector((0,0,-35))),tuple(center+Vector((0,0,-7))),ortho=85)
cams['crown']=C.camera('CAM_Crown',tuple(n*700+Vector((0,0,860))),(0,0,815),ortho=420)

for azi in [150,270]:
 v=Vector((math.cos(math.radians(azi)),math.sin(math.radians(azi)),0));cams[f'crown_{azi}']=C.camera(f'CAM_Crown_{azi}',tuple(v*700+Vector((0,0,860))),(0,0,815),ortho=420)
cams['balconies_oblique']=C.camera('CAM_Balconies_oblique',(145,-85,430),(0,0,420),ortho=110)
cams['terrace_side']=C.camera('CAM_Terrace_side',tuple(center+tt*85+tn*14+Vector((0,0,-5))),tuple(center+Vector((0,0,-14))),ortho=73)
s.camera=cams['hero'];s.render.resolution_x=1100;s.render.resolution_y=1700
s['height_m']=1008;s['height_basis']='USER_SPECIFIED';s['reference_version']='ASGG images, 2013/2014 floor documents, Jangho 2025 facade disclosures';s['status']='V5 drawing-derived upper envelope; balcony assignments and podium dimensions remain incomplete'
# Set a useful opening viewport as well as a saved render camera.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=1300;area.spaces.active.region_3d.view_location=(0,0,460)
notes=bpy.data.texts.new('READ_ME_本版未完成')
notes.write('V5修改：三向原始立面约束塔冠，移除局部鼓包和728m平顶；幕墙按1.5m分格；观景台台面、接口及支撑网格修复。\n总高1008m为用户指定。\n阳台：旧分组已被用户否定，已撤下，尚未重建。L158部分楼板缺轮廓，暂省略。\n塔冠为三向轮廓交集，背面凹面未由图纸唯一确定。裙房及观景台细部仍含图像拟合尺寸，不能视为施工复原。')
s['balcony_status']='Old unverified groups removed; balcony geometry incomplete'
s['crown_basis']='RWDI1011301 Figures4d/6d/8d, original vector contours'
s['model_completion']='PARTIAL_CORRECTION_NOT_COMPLETE'
assets=ROOT/'assets';assets.mkdir(exist_ok=True)
for col in [*main,cr,tr,bpy.data.collections['06b_Embedded_terrace_steel'],*pod]:bpy.data.libraries.write(str(assets/(col.name+'.blend')),{col},fake_user=True,compress=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'jeddah_tower_1008m_v5.blend'),compress=True)
print('SAVED V5',flush=True)
# Rendering is separate so a failed diagnostic cannot silently deliver previews
# from a previous scene.
(ROOT/'reports/build_summary.json').write_text(json.dumps({'objects':len(bpy.data.objects),'height':1008,'cameras':list(cams),'terrace':td},indent=2))

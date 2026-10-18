"""Blender construction helpers; all geometry is authored locally."""
import bpy, math
from mathutils import Vector
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

MATS={}
def material(name, color, metal=0, rough=0.3, transmission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=transmission
    MATS[name]=m; return m

def palette():
    material('Blue_silver_glass',(0.26,0.44,0.51),0.67,0.19,0.10)
    material('Dark_recess_glass',(0.045,0.11,0.14),0.50,0.26,0.10)
    material('Brushed_aluminum',(0.63,0.70,0.72),0.80,0.27)
    material('Spandrel',(0.10,0.18,0.22),0.55,0.30)
    material('Concrete',(0.53,0.52,0.47),0,0.70)
    material('Stone',(0.68,0.64,0.54),0,0.55)
    material('Canopy_shell',(0.78,0.79,0.76),0.35,0.25)
    material('Rail_glass',(0.47,0.69,0.73),0.05,0.08,0.87)
    material('Water',(0.07,0.24,0.28),0.55,0.18)
    material('Paving',(0.49,0.48,0.43),0,0.8)
    material('Planting',(0.16,0.24,0.13),0,0.85)
    material('Road',(0.12,0.135,0.14),0,0.9)

def collection(name):
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c

def mesh(name,verts,faces,mat,col,source='S01',status='CANDIDATE'):
    m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces); m.update()
    o=bpy.data.objects.new(name,m); col.objects.link(o)
    if mat:o.data.materials.append(MATS[mat])
    o['evidence_status']=status; o['source_ids']=source
    o['scope']='ASGG 2016 design interpretation; not as-built'
    return o

def prism(name,poly,z0,z1,mat,col,**kw):
    # Floor contours include straight facade sample points. Remove redundant
    # collinear points so Blender does not tessellate an n-gon into zero-area
    # triangles after storing coordinates at single precision.
    clean=[]
    for j,p in enumerate(poly):
        a=poly[j-1];b=poly[(j+1)%len(poly)]
        ux,uy=p[0]-a[0],p[1]-a[1];vx,vy=b[0]-p[0],b[1]-p[1]
        if math.hypot(ux,uy)<1e-8:continue
        cross=ux*vy-uy*vx
        if abs(cross)<1e-8*max(1,math.hypot(ux,uy)*math.hypot(vx,vy)) and ux*vx+uy*vy>0:continue
        clean.append(p)
    poly=clean
    n=len(poly); v=[(p[0],p[1],z) for z in (z0,z1) for p in poly]
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    f += [(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    return mesh(name,v,f,mat,col,**kw)

def box(name,center,size,mat,col,angle=0,**kw):
    x,y,z=center; a,b,c=(s/2 for s in size); cs,sn=math.cos(angle),math.sin(angle)
    verts=[(x+u*cs-v*sn,y+u*sn+v*cs,z+w) for w in (-c,c) for u,v in [(-a,-b),(a,-b),(a,b),(-a,b)]]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,col,**kw)

def curves(name,paths,radius,mat,col):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=1
    c.bevel_depth=radius; c.bevel_resolution=0
    for pts in paths:
        s=c.splines.new('POLY'); s.points.add(len(pts)-1)
        for v,p in zip(s.points,pts):v.co=(*p,1)
    o=bpy.data.objects.new(name,c); col.objects.link(o); c.materials.append(MATS[mat])
    o['evidence_status']='CANDIDATE'; o['source_ids']='S01'; return o

def disk(name,cx,cy,z,r,t,mat,col,segments=96,**kw):
    poly=[(cx+r*math.cos(2*math.pi*j/segments),cy+r*math.sin(2*math.pi*j/segments)) for j in range(segments)]
    return prism(name,poly,z-t,z,mat,col,**kw)

def camera(name,location,target,ortho=None,lens=50):
    c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=location; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    c.clip_end=20000; c.lens=lens
    if ortho:c.type='ORTHO';c.ortho_scale=ortho
    return o

import bpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;s=bpy.context.scene
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['crown','balconies','terrace_under','terrace_top','terrace_side']
namesmap={'hero':'Hero','crown':'Crown','crown_150':'Crown_150','crown_270':'Crown_270','balconies':'Balconies','balconies_oblique':'Balconies_oblique','terrace_under':'Terrace_under','terrace_top':'Terrace_top','terrace_side':'Terrace_side','podium':'Podium','podium_eye':'Podium_eye'}
for name in names:
 s.camera=bpy.data.objects['CAM_'+namesmap[name]];s.cycles.samples=20
 s.render.resolution_x,s.render.resolution_y=(850,1300) if name in ['hero','crown','crown_150','crown_270','balconies','balconies_oblique'] else (1100,950)
 s.render.filepath=str(ROOT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True);print('CHECK',name,flush=True)

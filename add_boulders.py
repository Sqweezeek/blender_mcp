"""
Add natural limestone boulders right inside the apex pocket (left of the white/yellow lead cars),
exactly where they belong in the reference artwork.
"""
import bpy
import bmesh
import random
from mathutils import Vector

mat_rock = bpy.data.materials.get('Rock')
if not mat_rock:
    mat_rock = bpy.data.materials.new('Rock')
    mat_rock.use_nodes = True
mat_rock.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.64, 0.62, 0.58, 1.0)
mat_rock.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.88

def make_apex_boulder(name, loc, scale=(1, 1, 1)):
    x, y, z = loc
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, location=(x, y, z + scale[2]*0.5), subdivisions=1)
    b = bpy.context.active_object
    b.name = name
    b.scale = scale
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bm = bmesh.new()
    bm.from_mesh(b.data)
    rng = random.Random(hash((x, y)))
    for v in bm.verts:
        v.co.x += rng.uniform(-0.15, 0.15) * scale[0]
        v.co.y += rng.uniform(-0.15, 0.15) * scale[1]
        v.co.z += rng.uniform(-0.10, 0.10) * scale[2]
        if v.co.z < z + 0.1:
            v.co.z = z
    bm.to_mesh(b.data)
    bm.free()
    b.data.materials.append(mat_rock)
    for p in b.data.polygons:
        p.use_smooth = False
    return b

# Apex boulders placed inside the corner pocket
make_apex_boulder('Apex_Rock_01', (-5.8, 1.8, 0), scale=(2.2, 1.8, 2.2))
make_apex_boulder('Apex_Rock_02', (-4.4, 3.8, 0), scale=(1.8, 1.6, 2.0))
make_apex_boulder('Apex_Rock_03', (-7.2, 0.5, 0), scale=(1.5, 1.4, 1.6))

# Remove SkyCloud_01 if it's too close/low, keep clouds very high and subtle
for o in list(bpy.data.objects):
    if 'SkyCloud' in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

# Save blend
bpy.ops.wm.save_as_mainfile(filepath=r"c:\Users\yurab\OneDrive\Desktop\temp\race_track_scene.blend")
print("Apex boulders added cleanly.")

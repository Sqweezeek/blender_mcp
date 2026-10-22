"""
Final polish script for race_track_scene.blend:
- Fix lighting: Sunlight angled from upper-left (sun rotation: pitch=42 deg, yaw=55 deg), so shadows cast naturally towards lower-right across the grass, not blocking the road.
- Adjust boulder tone from stark white to natural warm limestone/granite grey.
- Add lush pine trees to fill the lower-left empty grass lawn.
- Add clouds properly positioned in the sky.
- Ensure camera frames the full-screen circuit seamlessly.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

# 1. Update Sun light
sun = bpy.data.objects.get('Sun')
if sun:
    sun.data.energy = 4.2
    sun.data.color = (1.0, 0.96, 0.91)
    # Sunlight angled from the top-left casting soft shadows downwards-right
    sun.rotation_euler = Euler((math.radians(48), math.radians(-12), math.radians(45)), 'XYZ')

sky = bpy.data.objects.get('SkyFill')
if sky:
    sky.data.energy = 1.8
    sky.data.color = (0.78, 0.86, 1.0)
    sky.rotation_euler = Euler((math.radians(65), math.radians(10), math.radians(-135)), 'XYZ')

# 2. Update Rock material (natural warm granite grey matching reference)
mat_rock = bpy.data.materials.get('Rock')
if mat_rock and mat_rock.node_tree:
    bsdf = mat_rock.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.58, 0.56, 0.53, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.88

# 3. Update Foliage materials (rich vibrant forest alpine green)
f1 = bpy.data.materials.get('Foliage1')
if f1 and f1.node_tree:
    b = f1.node_tree.nodes.get('Principled BSDF')
    if b: b.inputs['Base Color'].default_value = (0.10, 0.38, 0.22, 1.0)

f2 = bpy.data.materials.get('Foliage2')
if f2 and f2.node_tree:
    b = f2.node_tree.nodes.get('Principled BSDF')
    if b: b.inputs['Base Color'].default_value = (0.14, 0.46, 0.26, 1.0)

f3 = bpy.data.materials.get('Foliage3')
if f3 and f3.node_tree:
    b = f3.node_tree.nodes.get('Principled BSDF')
    if b: b.inputs['Base Color'].default_value = (0.18, 0.54, 0.30, 1.0)

# Grass material
mat_grass = bpy.data.materials.get('Grass')
if mat_grass and mat_grass.node_tree:
    b = mat_grass.node_tree.nodes.get('Principled BSDF')
    if b: b.inputs['Base Color'].default_value = (0.28, 0.56, 0.24, 1.0)

# Asphalt material
mat_asphalt = bpy.data.materials.get('Asphalt')
if mat_asphalt and mat_asphalt.node_tree:
    b = mat_asphalt.node_tree.nodes.get('Principled BSDF')
    if b: b.inputs['Base Color'].default_value = (0.24, 0.22, 0.28, 1.0)

# 4. Add Trees into lower-left field to make the scene richly lush
def make_pine(loc, scale=1.0):
    x, y, z = loc
    # trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18*scale, depth=2.2*scale,
                                       location=(x, y, z + 1.1*scale), vertices=7)
    tr = bpy.context.active_object
    tr.data.materials.append(bpy.data.materials.get('Trunk'))

    layers = [(1.6, 1.8, 1.4, f1), (2.5, 1.4, 1.3, f2), (3.3, 1.0, 1.2, f3), (4.0, 0.6, 1.0, f2)]
    for h_off, rad, h, fm in layers:
        bpy.ops.mesh.primitive_cone_add(radius1=rad*scale, radius2=0, depth=h*scale,
                                       location=(x, y, z + h_off*scale), vertices=8)
        c = bpy.context.active_object
        c.data.materials.append(fm)

extra_trees = [
    # Lower-left lush forest
    (-14.0, -18.0, 1.5), (-16.5, -15.0, 1.3), (-18.0, -12.0, 1.4),
    (-12.5, -22.0, 1.4), (-9.0, -20.0, 1.3), (-15.0, -21.0, 1.6),
    (-7.5, -24.0, 1.2), (-4.0, -22.0, 1.5), (-2.0, -25.0, 1.3),
    (-19.0, -17.0, 1.2), (-21.0, -13.0, 1.5),
    # Far left outer bend
    (-16.0, -7.0, 1.4), (-17.5, -3.0, 1.5), (-15.0, 0.5, 1.3),
    # Foreground bottom right edge
    (28.0, -14.0, 1.4), (32.0, -12.0, 1.5), (35.0, -14.0, 1.3),
]

for tx, ty, tscale in extra_trees:
    make_pine((tx, ty, 0), scale=tscale)

# 5. Add Low-Poly Clouds in the upper sky (no shadow on main road)
mat_cloud = bpy.data.materials.get('Cloud')
if not mat_cloud:
    mat_cloud = bpy.data.materials.new('Cloud')
    mat_cloud.use_nodes = True
    mat_cloud.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)

def make_cloud(name, loc, sc=(1, 1, 1)):
    parts = []
    cx, cy, cz = loc
    spheres = [
        (0.0, 0.0, 0.0, 3.2), (2.6, 0.6, -0.3, 2.4), (-2.4, -0.5, -0.2, 2.3),
        (0.8, 1.8, 0.4, 2.1), (-1.2, 1.5, 0.3, 2.0),
    ]
    for sx, sy, sz, r in spheres:
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=r, subdivisions=2,
            location=(cx + sx * sc[0], cy + sy * sc[1], cz + sz * sc[2])
        )
        sp = bpy.context.active_object
        sp.scale = (sc[0], sc[1], sc[2] * 0.60)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        sp.data.materials.append(mat_cloud)
        for p in sp.data.polygons: p.use_smooth = True
        parts.append(sp)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    cl = bpy.context.active_object
    cl.name = name
    # Disable casting shadows so they don't darken the road
    cl.visible_shadow = False
    return cl

# Place fluffy clouds high in the sky
make_cloud('SkyCloud_01', loc=(-12.0, 18.0, 38.0), sc=(2.8, 2.2, 2.0))
make_cloud('SkyCloud_02', loc=(22.0, 24.0, 42.0), sc=(3.2, 2.5, 2.2))
make_cloud('SkyCloud_03', loc=(35.0, 0.0, 36.0), sc=(2.6, 2.0, 1.8))

# 6. Perfect Camera Setup
cam = bpy.data.objects.get('RaceCam')
if cam:
    cam.location = (11.5, -23.0, 23.5)
    cam.rotation_euler = Euler((math.radians(48), 0, math.radians(26)), 'XYZ')
    cam.data.lens = 22
    cam.data.clip_end = 350

# Save blend
bpy.ops.wm.save_as_mainfile(filepath=r"c:\Users\yurab\OneDrive\Desktop\temp\race_track_scene.blend")
print("Scene final polish complete!")

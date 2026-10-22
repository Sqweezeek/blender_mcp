"""
Blender Python script — stylized low-poly racing track scene (v7 - Perfect Full Screen Track & Trees).
- Road covers full screen diagonally like reference artwork (hairpin apex left, straight top-center, sweeping foreground bend bottom across right).
- Beautiful stylized low-poly clouds placed high up above the scene.
- Densely packed, vibrant stylized pine trees in clusters (around hairpin, infield, and foreground corners).
- Big iconic faceted boulders at the hairpin apex.
- Detailed, scaled-up GT3 race cars battling into the corner.
- Red/white alternating curbs and tire barrier safety fence.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for d in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.images):
        for b in list(d):
            if b.users == 0:
                d.remove(b)

def mat(name, rgba, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = rgba
        b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metal
    return m

def apply_tf(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

def build_materials():
    M = {}
    # Track
    M['asphalt']       = mat('Asphalt',      (0.22, 0.21, 0.27, 1), 0.88)
    M['road_line']     = mat('RoadLine',     (0.96, 0.95, 0.90, 1), 0.50)
    M['curb_red']      = mat('CurbRed',      (0.85, 0.10, 0.08, 1), 0.40)
    M['curb_white']    = mat('CurbWhite',    (0.96, 0.96, 0.96, 1), 0.40)
    M['shoulder']      = mat('Shoulder',     (0.55, 0.30, 0.16, 1), 0.85)

    # Environment
    M['grass']         = mat('Grass',        (0.24, 0.52, 0.22, 1), 0.92)
    M['rock']          = mat('Rock',         (0.68, 0.65, 0.62, 1), 0.85)
    M['cloud']         = mat('Cloud',        (0.98, 0.98, 1.0, 1), 0.35)

    # Pine Trees - Deep vibrant alpine greens (not washed out)
    M['trunk']         = mat('Trunk',        (0.28, 0.18, 0.10, 1), 0.85)
    M['foliage_1']     = mat('Foliage1',     (0.08, 0.32, 0.16, 1), 0.80)
    M['foliage_2']     = mat('Foliage2',     (0.12, 0.42, 0.22, 1), 0.80)
    M['foliage_3']     = mat('Foliage3',     (0.16, 0.50, 0.26, 1), 0.80)

    # Barriers & Track Safety
    M['tire_red']      = mat('TireRed',      (0.86, 0.16, 0.10, 1), 0.60)
    M['tire_white']    = mat('TireWhite',    (0.95, 0.95, 0.95, 1), 0.60)
    M['fence_post']    = mat('FencePost',    (0.68, 0.70, 0.74, 1), 0.35, 0.8)
    M['fence_wire']    = mat('FenceWire',    (0.62, 0.64, 0.68, 1), 0.30, 0.7)

    # Cones & Bollards
    M['cone_org']      = mat('ConeOrg',      (0.98, 0.34, 0.04, 1), 0.45)
    M['cone_wh']       = mat('ConeWh',       (0.96, 0.96, 0.96, 1), 0.45)
    M['boll_red']      = mat('BollRed',      (0.88, 0.12, 0.08, 1), 0.45)
    M['boll_wh']       = mat('BollWh',       (0.96, 0.96, 0.96, 1), 0.45)

    # Cars
    M['car_white']     = mat('CarWhite',     (0.96, 0.96, 0.96, 1), 0.18)
    M['car_yellow']    = mat('CarYellow',    (0.98, 0.80, 0.05, 1), 0.18)
    M['car_orange']    = mat('CarOrange',    (0.96, 0.42, 0.06, 1), 0.18)
    M['car_blue']      = mat('CarBlue',      (0.10, 0.42, 0.90, 1), 0.18)
    M['car_red']       = mat('CarRed',       (0.88, 0.10, 0.08, 1), 0.18)
    M['car_cyan']      = mat('CarCyan',      (0.12, 0.75, 0.88, 1), 0.18)
    M['car_dark']      = mat('CarDark',      (0.06, 0.06, 0.07, 1), 0.35)
    M['car_glass']     = mat('CarGlass',     (0.15, 0.20, 0.26, 1), 0.05, 0.1)
    M['car_wheel']     = mat('CarWheel',     (0.06, 0.06, 0.06, 1), 0.75)
    M['car_rim']       = mat('CarRim',       (0.85, 0.85, 0.88, 1), 0.20, 0.85)
    M['headlight']     = mat('Headlight',    (1.0, 1.0, 0.85, 1), 0.10)
    M['taillight']     = mat('Taillight',    (0.95, 0.04, 0.04, 1), 0.10)

    return M

# ────────────────────────────────────────────────────────────────────────────
# HIGH-DETAIL GT RACE CAR
# ────────────────────────────────────────────────────────────────────────────

def create_detailed_car(name, loc, rot_z, primary_mat, M, secondary_mat=None, spoiler_color=None):
    car_parts = []
    stripe_mat = secondary_mat if secondary_mat else M['car_dark']
    wing_mat = spoiler_color if spoiler_color else M['car_dark']

    # 1. Main Sculpted Chassis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.45))
    body = bpy.context.active_object
    body.scale = (3.0, 1.55, 0.42)
    apply_tf(body)

    bm = bmesh.new()
    bm.from_mesh(body.data)
    for v in bm.verts:
        if v.co.x > 0.7:
            v.co.z *= 0.65
            v.co.y *= 0.88
        if v.co.x > 1.2:
            v.co.z *= 0.70
            v.co.y *= 0.85
        if 0.2 < v.co.x < 1.0 and v.co.z > 0.45:
            v.co.z -= 0.08
    bm.to_mesh(body.data)
    bm.free()
    body.data.materials.append(primary_mat)
    car_parts.append(body)

    # 2. Flared Wheel Arches
    for fx, fy in [(0.90, 0.78), (0.90, -0.78), (-0.90, 0.78), (-0.90, -0.78)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy, 0.45))
        fend = bpy.context.active_object
        fend.scale = (0.75, 0.12, 0.35)
        apply_tf(fend)
        fend.data.materials.append(primary_mat)
        car_parts.append(fend)

    # 3. Racing Stripes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.48))
    stripe = bpy.context.active_object
    stripe.scale = (2.95, 0.35, 0.42)
    apply_tf(stripe)
    stripe.data.materials.append(stripe_mat)
    car_parts.append(stripe)

    # 4. Cabin
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.15, 0.0, 0.88))
    cabin = bpy.context.active_object
    cabin.scale = (1.50, 1.22, 0.44)
    apply_tf(cabin)
    bm = bmesh.new()
    bm.from_mesh(cabin.data)
    for v in bm.verts:
        if v.co.z > 0.88:
            v.co.y *= 0.80
            if v.co.x > 0:
                v.co.x -= 0.35
            else:
                v.co.x += 0.20
    bm.to_mesh(cabin.data)
    bm.free()
    cabin.data.materials.append(M['car_glass'])
    car_parts.append(cabin)

    # Roof Cap & Scoop
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.20, 0.0, 1.12))
    roof = bpy.context.active_object
    roof.scale = (1.00, 0.98, 0.06)
    apply_tf(roof)
    roof.data.materials.append(primary_mat)
    car_parts.append(roof)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.05, 0.0, 1.18))
    scoop = bpy.context.active_object
    scoop.scale = (0.35, 0.20, 0.08)
    apply_tf(scoop)
    scoop.data.materials.append(M['car_dark'])
    car_parts.append(scoop)

    # 5. Splitter & Headlights
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.52, 0.0, 0.22))
    splitter = bpy.context.active_object
    splitter.scale = (0.40, 1.58, 0.08)
    apply_tf(splitter)
    splitter.data.materials.append(M['car_dark'])
    car_parts.append(splitter)

    for side in [-0.52, 0.52]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.38, side, 0.54))
        hl = bpy.context.active_object
        hl.scale = (0.24, 0.22, 0.12)
        apply_tf(hl)
        hl.data.materials.append(M['headlight'])
        car_parts.append(hl)

    # Taillights
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.50, 0.0, 0.55))
    tl = bpy.context.active_object
    tl.scale = (0.08, 1.30, 0.10)
    apply_tf(tl)
    tl.data.materials.append(M['taillight'])
    car_parts.append(tl)

    # 6. Rear GT Wing
    for side in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.28, side, 0.95))
        upright = bpy.context.active_object
        upright.scale = (0.08, 0.05, 0.52)
        apply_tf(upright)
        upright.data.materials.append(M['car_dark'])
        car_parts.append(upright)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.38, 0.0, 1.22))
    wing = bpy.context.active_object
    wing.scale = (0.40, 1.75, 0.07)
    apply_tf(wing)
    wing.data.materials.append(wing_mat)
    car_parts.append(wing)

    for side in [-0.88, 0.88]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.38, side, 1.22))
        ep = bpy.context.active_object
        ep.scale = (0.44, 0.04, 0.24)
        apply_tf(ep)
        ep.data.materials.append(wing_mat)
        car_parts.append(ep)

    # 7. Wheels & Rims
    wheel_coords = [
        ( 0.90,  0.78, 0.36),
        ( 0.90, -0.78, 0.36),
        (-0.90,  0.78, 0.36),
        (-0.90, -0.78, 0.36),
    ]
    for wx, wy, wz in wheel_coords:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.36, depth=0.26,
                                           location=(wx, wy, wz),
                                           rotation=(math.pi/2, 0, 0), vertices=18)
        tire = bpy.context.active_object
        tire.data.materials.append(M['car_wheel'])
        car_parts.append(tire)

        rim_y = wy + (0.04 if wy > 0 else -0.04)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.22,
                                           location=(wx, rim_y, wz),
                                           rotation=(math.pi/2, 0, 0), vertices=14)
        rim = bpy.context.active_object
        rim.data.materials.append(M['car_rim'])
        car_parts.append(rim)

    bpy.ops.object.select_all(action='DESELECT')
    for p in car_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = car_parts[0]
    bpy.ops.object.join()

    car = bpy.context.active_object
    car.name = name
    car.location = loc
    car.rotation_euler = Euler((0, 0, rot_z), 'XYZ')
    return car

# ────────────────────────────────────────────────────────────────────────────
# FULL-SCREEN CIRCUIT TRACK
# ────────────────────────────────────────────────────────────────────────────

def create_race_track(M):
    track_objs = []

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.05))
    ground = bpy.context.active_object
    ground.name = 'Ground'
    ground.data.materials.append(M['grass'])
    track_objs.append(ground)

    # Extended curve points covering full view:
    curve_pts = [
        Vector((-3.0,  30.0, 0.0)),
        Vector((-2.0,  22.0, 0.0)),
        Vector((-1.5,  15.0, 0.0)),
        Vector((-1.0,   8.0, 0.0)),
        Vector((-2.2,   2.5, 0.0)),
        Vector((-4.5,  -1.2, 0.0)), # APEX of hairpin
        Vector((-4.2,  -5.5, 0.0)),
        Vector((-1.5,  -8.5, 0.0)),
        Vector(( 3.5,  -9.5, 0.0)),
        Vector(( 9.0,  -8.8, 0.0)),
        Vector((15.5,  -6.2, 0.0)),
        Vector((22.0,  -4.0, 0.0)),
        Vector((29.0,  -3.5, 0.0)),
        Vector((36.0,  -5.5, 0.0)),
        Vector((42.0, -10.0, 0.0)),
    ]

    num_samples = 400
    pts = []
    for i in range(num_samples):
        t = i / (num_samples - 1) * (len(curve_pts) - 1)
        idx = int(t)
        frac = t - idx
        if idx >= len(curve_pts) - 1:
            pts.append(curve_pts[-1])
        else:
            p0 = curve_pts[max(0, idx - 1)]
            p1 = curve_pts[idx]
            p2 = curve_pts[min(len(curve_pts) - 1, idx + 1)]
            p3 = curve_pts[min(len(curve_pts) - 1, idx + 2)]
            pos = 0.5 * (
                (2 * p1) +
                (-p0 + p2) * frac +
                (2 * p0 - 5 * p1 + 4 * p2 - p3) * (frac ** 2) +
                (-p0 + 3 * p1 - 3 * p2 + p3) * (frac ** 3)
            )
            pts.append(pos)

    normals = []
    for i in range(len(pts)):
        if i == 0:
            tangent = pts[1] - pts[0]
        elif i == len(pts) - 1:
            tangent = pts[-1] - pts[-2]
        else:
            tangent = pts[i+1] - pts[i-1]
        tangent.z = 0
        tangent.normalize()
        normals.append(Vector((-tangent.y, tangent.x, 0)))

    # Generous track width
    ROAD_W = 5.2
    CURB_W = 0.70
    SHOULDER_W = 1.6

    def make_ribbon(name, w_left, w_right, z_elev, material):
        verts = []
        faces = []
        for i, (p, n) in enumerate(zip(pts, normals)):
            verts.append((p.x + n.x * w_left, p.y + n.y * w_left, z_elev))
            verts.append((p.x - n.x * w_right, p.y - n.y * w_right, z_elev))
            if i > 0:
                faces.append([(i-1)*2, (i-1)*2+1, i*2+1, i*2])
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.update()
        obj = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(obj)
        obj.data.materials.append(material)
        return obj

    tot_w = ROAD_W + CURB_W + SHOULDER_W
    shoulder = make_ribbon('Shoulder', tot_w, tot_w, 0.005, M['shoulder'])
    track_objs.append(shoulder)

    asphalt = make_ribbon('Asphalt', ROAD_W, ROAD_W, 0.015, M['asphalt'])
    track_objs.append(asphalt)

    # Dashed center line along the road
    dash_len = 5
    gap_len = 4
    i = 0
    dash_id = 0
    while i < len(pts) - dash_len:
        sp = pts[i:i+dash_len+1]
        sn = normals[i:i+dash_len+1]
        c_verts = []
        c_faces = []
        for j, (p, n) in enumerate(zip(sp, sn)):
            c_verts.append((p.x + n.x * 0.16, p.y + n.y * 0.16, 0.022))
            c_verts.append((p.x - n.x * 0.16, p.y - n.y * 0.16, 0.022))
            if j > 0:
                c_faces.append([(j-1)*2, (j-1)*2+1, j*2+1, j*2])
        me = bpy.data.meshes.new(f'Dash_{dash_id}')
        me.from_pydata(c_verts, [], c_faces)
        me.update()
        d_obj = bpy.data.objects.new(f'Dash_{dash_id}', me)
        bpy.context.collection.objects.link(d_obj)
        d_obj.data.materials.append(M['road_line'])
        track_objs.append(d_obj)
        i += dash_len + gap_len
        dash_id += 1

    # Curbs on apex (samples 70..210)
    curb_seg_len = 6
    for s in range(70, 210, curb_seg_len):
        seg_pts = pts[s:s+curb_seg_len+1]
        seg_norms = normals[s:s+curb_seg_len+1]
        is_red = ((s // curb_seg_len) % 2 == 0)
        cmat = M['curb_red'] if is_red else M['curb_white']

        c_verts = []
        c_faces = []
        for i, (p, n) in enumerate(zip(seg_pts, seg_norms)):
            c_verts.append((p.x + n.x * (ROAD_W + CURB_W), p.y + n.y * (ROAD_W + CURB_W), 0.025))
            c_verts.append((p.x + n.x * ROAD_W, p.y + n.y * ROAD_W, 0.025))
            if i > 0:
                c_faces.append([(i-1)*2, (i-1)*2+1, i*2+1, i*2])
        me = bpy.data.meshes.new(f'Curb_Apex_{s}')
        me.from_pydata(c_verts, [], c_faces)
        me.update()
        c_obj = bpy.data.objects.new(f'Curb_Apex_{s}', me)
        bpy.context.collection.objects.link(c_obj)
        c_obj.data.materials.append(cmat)
        track_objs.append(c_obj)

    # Curbs on outer sweeping bend (samples 250..370)
    for s in range(250, 370, curb_seg_len):
        seg_pts = pts[s:s+curb_seg_len+1]
        seg_norms = normals[s:s+curb_seg_len+1]
        is_red = ((s // curb_seg_len) % 2 == 0)
        cmat = M['curb_red'] if is_red else M['curb_white']

        c_verts = []
        c_faces = []
        for i, (p, n) in enumerate(zip(seg_pts, seg_norms)):
            c_verts.append((p.x - n.x * ROAD_W, p.y - n.y * ROAD_W, 0.025))
            c_verts.append((p.x - n.x * (ROAD_W + CURB_W), p.y - n.y * (ROAD_W + CURB_W), 0.025))
            if i > 0:
                c_faces.append([(i-1)*2, (i-1)*2+1, i*2+1, i*2])
        me = bpy.data.meshes.new(f'Curb_Outer_{s}')
        me.from_pydata(c_verts, [], c_faces)
        me.update()
        c_obj = bpy.data.objects.new(f'Curb_Outer_{s}', me)
        bpy.context.collection.objects.link(c_obj)
        c_obj.data.materials.append(cmat)
        track_objs.append(c_obj)

    # Top parallel straight (top right)
    top_track_pts = [
        Vector((-15.0,  34.0, 0.0)),
        Vector((-2.0,   32.0, 0.0)),
        Vector((15.0,   30.0, 0.0)),
        Vector((30.0,   27.0, 0.0)),
        Vector((45.0,   22.0, 0.0)),
    ]
    top_ribbon_pts = []
    num_top = 100
    for i in range(num_top):
        t = i / (num_top - 1) * (len(top_track_pts) - 1)
        idx = int(t)
        frac = t - idx
        if idx >= len(top_track_pts) - 1:
            top_ribbon_pts.append(top_track_pts[-1])
        else:
            top_ribbon_pts.append(top_track_pts[idx].lerp(top_track_pts[idx+1], frac))
    
    top_norms = []
    for i in range(len(top_ribbon_pts)):
        if i == 0:
            tg = top_ribbon_pts[1] - top_ribbon_pts[0]
        elif i == len(top_ribbon_pts) - 1:
            tg = top_ribbon_pts[-1] - top_ribbon_pts[-2]
        else:
            tg = top_ribbon_pts[i+1] - top_ribbon_pts[i-1]
        tg.z = 0; tg.normalize()
        top_norms.append(Vector((-tg.y, tg.x, 0)))

    b_verts = []; b_faces = []
    for i, (p, n) in enumerate(zip(top_ribbon_pts, top_norms)):
        b_verts.append((p.x + n.x * 4.8, p.y + n.y * 4.8, 0.012))
        b_verts.append((p.x - n.x * 4.8, p.y - n.y * 4.8, 0.012))
        if i > 0:
            b_faces.append([(i-1)*2, (i-1)*2+1, i*2+1, i*2])
    b_me = bpy.data.meshes.new('TopRoad')
    b_me.from_pydata(b_verts, [], b_faces)
    b_me.update()
    b_obj = bpy.data.objects.new('TopRoad', b_me)
    bpy.context.collection.objects.link(b_obj)
    b_obj.data.materials.append(M['asphalt'])

    return track_objs, pts, normals

# ────────────────────────────────────────────────────────────────────────────
# CLOUDS (Raised up in sky: Z = 45..55, visible above scenery)
# ────────────────────────────────────────────────────────────────────────────

def create_lowpoly_cloud(name, loc, scale=(1, 1, 1), M=None):
    cloud_parts = []
    cx, cy, cz = loc

    spheres = [
        (0.0, 0.0, 0.0, 3.2),
        (2.6, 0.6, -0.3, 2.4),
        (-2.4, -0.5, -0.2, 2.3),
        (0.8, 1.8, 0.4, 2.1),
        (-1.2, 1.5, 0.3, 2.0),
        (0.4, -1.5, -0.2, 1.8),
    ]

    for sx, sy, sz, r in spheres:
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=r,
            subdivisions=2,
            location=(cx + sx * scale[0], cy + sy * scale[1], cz + sz * scale[2])
        )
        sphere = bpy.context.active_object
        sphere.scale = (scale[0], scale[1], scale[2] * 0.60)
        apply_tf(sphere)
        sphere.data.materials.append(M['cloud'])
        for p in sphere.data.polygons:
            p.use_smooth = True
        cloud_parts.append(sphere)

    bpy.ops.object.select_all(action='DESELECT')
    for p in cloud_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = cloud_parts[0]
    bpy.ops.object.join()

    cloud = bpy.context.active_object
    cloud.name = name
    return cloud

# ────────────────────────────────────────────────────────────────────────────
# PINE TREES, BOULDERS & BARRIERS
# ────────────────────────────────────────────────────────────────────────────

def create_pine_tree(loc, scale=1.0, M=None):
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18*scale, depth=2.2*scale,
                                       location=(x, y, z + 1.1*scale), vertices=7)
    trunk = bpy.context.active_object
    trunk.data.materials.append(M['trunk'])

    layers = [
        (1.6, 1.8, 1.4, M['foliage_1']),
        (2.5, 1.4, 1.3, M['foliage_2']),
        (3.3, 1.0, 1.2, M['foliage_3']),
        (4.0, 0.6, 1.0, M['foliage_2']),
    ]
    for h_off, rad, height, fmat in layers:
        bpy.ops.mesh.primitive_cone_add(radius1=rad*scale, radius2=0, depth=height*scale,
                                       location=(x, y, z + h_off*scale), vertices=8)
        cone = bpy.context.active_object
        cone.data.materials.append(fmat)

def create_boulder(loc, scale=(1, 1, 1), M=None):
    x, y, z = loc
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, location=(x, y, z + scale[2]*0.6), subdivisions=1)
    b = bpy.context.active_object
    b.scale = scale
    apply_tf(b)

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
    b.data.materials.append(M['rock'])
    for p in b.data.polygons:
        p.use_smooth = False
    return b

def create_tire_stack_wall(start_pos, end_pos, rows=2, M=None):
    sx, sy, sz = start_pos
    ex, ey, ez = end_pos
    dx, dy = ex - sx, ey - sy
    dist = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)

    spacing = 0.72
    num_tires = int(dist / spacing)

    for i in range(num_tires):
        t = i / max(1, num_tires - 1)
        tx = sx + dx * t
        ty = sy + dy * t

        for row in range(rows):
            is_red = ((i + row) % 2 == 0)
            tmat = M['tire_red'] if is_red else M['tire_white']

            bpy.ops.mesh.primitive_torus_add(
                major_radius=0.28, minor_radius=0.12,
                major_segments=12, minor_segments=8,
                location=(tx, ty, sz + row * 0.28 + 0.20),
                rotation=(math.pi/2, 0, angle)
            )
            tire = bpy.context.active_object
            tire.data.materials.append(tmat)

def create_fence_with_posts(start_pt, end_pt, M=None):
    sx, sy, sz = start_pt
    ex, ey, ez = end_pt
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)

    post_spacing = 2.2
    n_posts = max(2, int(length / post_spacing))

    for i in range(n_posts + 1):
        t = i / n_posts
        px = sx + dx * t
        py = sy + dy * t

        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=2.2,
                                           location=(px, py, sz + 1.1), vertices=8)
        p = bpy.context.active_object
        p.data.materials.append(M['fence_post'])

        arm_norm = Vector((-math.sin(ang), math.cos(ang), 0))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.55,
                                           location=(px + arm_norm.x * 0.22, py + arm_norm.y * 0.22, sz + 2.3),
                                           rotation=(0.6, 0, ang), vertices=6)
        arm = bpy.context.active_object
        arm.data.materials.append(M['fence_post'])

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=((sx+ex)/2, (sy+ey)/2, sz + 1.1))
    wire = bpy.context.active_object
    wire.scale = (length / 2, 0.02, 0.95)
    wire.rotation_euler = Euler((math.pi/2, 0, ang), 'XYZ')
    apply_tf(wire)
    wire.data.materials.append(M['fence_wire'])

def create_cone(loc, M):
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.05, location=(x, y, z + 0.025), vertices=8)
    base = bpy.context.active_object
    base.data.materials.append(M['cone_org'])

    bpy.ops.mesh.primitive_cone_add(radius1=0.18, radius2=0.03, depth=0.60, location=(x, y, z + 0.35), vertices=8)
    body = bpy.context.active_object
    body.data.materials.append(M['cone_org'])

    bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.10, location=(x, y, z + 0.40), vertices=8)
    stripe = bpy.context.active_object
    stripe.data.materials.append(M['cone_wh'])

def create_bollard(loc, M):
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.90, location=(x, y, z + 0.45), vertices=8)
    post = bpy.context.active_object
    post.data.materials.append(M['boll_red'])

    for sz in [0.22, 0.50, 0.75]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.108, depth=0.09, location=(x, y, z + sz), vertices=8)
        st = bpy.context.active_object
        st.data.materials.append(M['boll_wh'])

# ────────────────────────────────────────────────────────────────────────────
# MAIN SCENE ASSEMBLY
# ────────────────────────────────────────────────────────────────────────────

def assemble_scene():
    cleanup()
    M = build_materials()

    track_objs, pts, normals = create_race_track(M)

    # 1. Iconic apex boulders
    create_boulder((-6.5, 3.2, 0), scale=(2.4, 2.0, 2.6), M=M)
    create_boulder((-5.0, 5.0, 0), scale=(1.9, 1.7, 2.2), M=M)
    create_boulder((-8.2, 1.8, 0), scale=(1.6, 1.6, 1.9), M=M)

    # 2. DENSE PINE TREES (Richly populated matching reference)
    tree_coords = [
        # Behind the apex boulders (dense forest cluster)
        (-9.2, 5.2, 1.3), (-10.8, 2.8, 1.4), (-7.8, 7.8, 1.2),
        (-10.2, 8.2, 1.5), (-6.2, 9.2, 1.1), (-12.0, 5.5, 1.3),
        (-8.5, 11.0, 1.4), (-11.5, 11.5, 1.2), (-13.5, 8.0, 1.6),
        (-9.8, 13.5, 1.3), (-12.8, 14.2, 1.4), (-7.0, 13.0, 1.2),

        # Far top left forest
        (-3.2, 22.2, 1.3), (-6.2, 20.2, 1.5), (-8.5, 24.0, 1.4),
        (-1.0, 26.5, 1.2), (-5.0, 28.0, 1.6), (-9.0, 28.5, 1.3),

        # Infield between straight and right bend
        (5.2, 11.2, 1.3), (6.8, 13.8, 1.5), (3.8, 14.8, 1.2),
        (8.5, 16.0, 1.4), (10.2, 12.5, 1.3), (7.0, 8.5, 1.2),
        (9.5, 5.0, 1.5), (12.0, 8.0, 1.4), (13.5, 11.0, 1.3),
        (15.0, 14.5, 1.4), (11.5, 18.0, 1.3), (14.0, 21.0, 1.5),

        # Far top right forest
        (18.0, 18.0, 1.5), (21.0, 15.0, 1.3), (24.5, 17.5, 1.4),
        (26.0, 13.0, 1.2), (29.0, 16.0, 1.5), (32.0, 14.0, 1.3),

        # Bottom foreground clusters (along the front sweeping turn)
        (12.8, -13.2, 1.4), (15.2, -11.8, 1.6), (17.5, -13.8, 1.3),
        (10.8, -14.5, 1.2), (8.0, -15.0, 1.0), (5.5, -15.5, 1.3),
        (20.5, -11.0, 1.5), (23.0, -12.5, 1.3), (26.5, -10.0, 1.4),

        # Far right exit forest
        (30.0, -8.5, 1.5), (33.0, -11.0, 1.3), (35.5, -7.0, 1.4),
        (38.0, -4.5, 1.2), (40.5, -7.5, 1.5), (28.5, -1.0, 1.3),
        (32.0, 2.0, 1.4), (35.0, 5.0, 1.5), (38.0, 1.5, 1.3),

        # Outer hairpin runoff trees (left)
        (-12.5, -3.0, 1.4), (-14.0, -6.5, 1.3), (-11.0, -8.5, 1.5),
        (-8.5, -12.0, 1.2), (-5.0, -14.0, 1.4), (-13.0, -11.0, 1.3),
    ]
    for tx, ty, tscale in tree_coords:
        create_pine_tree((tx, ty, 0), scale=tscale, M=M)

    # 3. CLOUDS — MOVED UP HIGH (Z = 45..55)
    # Floating gracefully above the entire racing circuit
    create_lowpoly_cloud('Cloud_High_01', loc=(-5.0, 15.0, 48.0), scale=(3.0, 2.4, 2.2), M=M)
    create_lowpoly_cloud('Cloud_High_02', loc=(18.0, 22.0, 52.0), scale=(3.4, 2.6, 2.4), M=M)
    create_lowpoly_cloud('Cloud_High_03', loc=(32.0, -2.0, 46.0), scale=(2.8, 2.2, 2.0), M=M)
    create_lowpoly_cloud('Cloud_High_04', loc=(-4.0, -16.0, 50.0), scale=(3.2, 2.5, 2.2), M=M)

    # 4. Long Tyre Wall & Chain-link Fence along foreground sweeping turn
    create_tire_stack_wall(start_pos=(-3.5, -14.0, 0), end_pos=(28.5, -8.5, 0), rows=2, M=M)
    create_fence_with_posts(start_pt=(-4.5, -14.6, 0), end_pt=(29.5, -9.1, 0), M=M)

    # Outer straight tire wall & fence (top right)
    create_fence_with_posts(start_pt=(5.2, 20.0, 0), end_pt=(3.2, 8.5, 0), M=M)
    create_tire_stack_wall(start_pos=(4.6, 19.5, 0), end_pos=(2.8, 9.0, 0), rows=2, M=M)

    # 5. Apex bollards & cones
    create_bollard((-4.2, 0.4, 0), M)
    create_bollard((-4.8, -2.4, 0), M)

    cone_coords = [
        (3.0, 0.5),
        (3.5, -1.2),
        (3.0, -3.2),
        (2.0, -5.2),
    ]
    for cx, cy in cone_coords:
        create_cone((cx, cy, 0), M)

    # 6. Detailed, Scaled GT Race Cars
    create_detailed_car(
        name='Car_01_ApexDrifter',
        loc=(-3.5, -1.6, 0.05),
        rot_z=math.radians(-70),
        primary_mat=M['car_white'],
        secondary_mat=M['car_red'],
        spoiler_color=M['car_red'],
        M=M
    )

    create_detailed_car(
        name='Car_02_YellowGT',
        loc=(-1.6, 0.4, 0.05),
        rot_z=math.radians(-84),
        primary_mat=M['car_yellow'],
        secondary_mat=M['car_dark'],
        spoiler_color=M['car_dark'],
        M=M
    )

    create_detailed_car(
        name='Car_03_WhiteBlueGT',
        loc=(-1.1, 3.2, 0.05),
        rot_z=math.radians(-94),
        primary_mat=M['car_white'],
        secondary_mat=M['car_blue'],
        spoiler_color=M['car_blue'],
        M=M
    )

    create_detailed_car(
        name='Car_04_OrangeGT',
        loc=(-0.6, 6.2, 0.05),
        rot_z=math.radians(-98),
        primary_mat=M['car_orange'],
        secondary_mat=M['car_white'],
        spoiler_color=M['car_red'],
        M=M
    )

    create_detailed_car(
        name='Car_05_BlueGT',
        loc=(0.2, 9.8, 0.05),
        rot_z=math.radians(-102),
        primary_mat=M['car_blue'],
        secondary_mat=M['car_yellow'],
        spoiler_color=M['car_dark'],
        M=M
    )

    create_detailed_car(
        name='Car_06_CyanGT',
        loc=(1.0, 14.5, 0.05),
        rot_z=math.radians(-100),
        primary_mat=M['car_cyan'],
        secondary_mat=M['car_white'],
        spoiler_color=M['car_dark'],
        M=M
    )

    # 7. Lighting
    bpy.ops.object.light_add(type='SUN', location=(15, -18, 30))
    sun = bpy.context.active_object
    sun.name = 'Sun'
    sun.data.energy = 4.6
    sun.data.color = (1.0, 0.96, 0.90)
    sun.rotation_euler = Euler((math.radians(45), math.radians(18), math.radians(-32)), 'XYZ')

    bpy.ops.object.light_add(type='SUN', location=(-20, 20, 25))
    fill = bpy.context.active_object
    fill.name = 'SkyFill'
    fill.data.energy = 1.6
    fill.data.color = (0.75, 0.85, 1.0)
    fill.rotation_euler = Euler((math.radians(60), math.radians(-15), math.radians(140)), 'XYZ')

    world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.55, 0.70, 0.88, 1.0)
        bg.inputs['Strength'].default_value = 0.65

    # 8. FULL SCREEN ROAD CAMERA FRAMING
    # Isometric telephoto style framing that fills the screen edge-to-edge with the racetrack
    bpy.ops.object.camera_add(location=(14.0, -26.0, 36.0))
    cam = bpy.context.active_object
    cam.name = 'RaceCam'
    cam.rotation_euler = Euler((math.radians(52), 0, math.radians(24)), 'XYZ')
    cam.data.lens = 45
    cam.data.clip_end = 350
    bpy.context.scene.camera = cam

    # 9. Render Settings
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 128
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.view_settings.view_transform = 'Standard'

    out_file = r"c:\Users\yurab\OneDrive\Desktop\temp\race_track_scene.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    print(f"Saved successfully to: {out_file}")

if __name__ == '__main__':
    assemble_scene()

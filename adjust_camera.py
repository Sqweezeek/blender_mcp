"""
Script to precisely center the camera on the racetrack action:
Hairpin turn + cars + bottom sweeper + entry straight.
"""
import bpy
import math
from mathutils import Vector, Euler

cam = bpy.data.objects.get('RaceCam')
if cam:
    # Camera centered on the track action (X=3, Y=-4) looking down at 54 degrees
    # This brings the bottom sweeper (Y=-12..-14) into full view at the bottom of the screen
    # and keeps the cars and hairpin in the center and entry straight at the top
    cam.location = (6.0, -18.0, 22.0)
    cam.rotation_euler = Euler((math.radians(52), 0, math.radians(24)), 'XYZ')
    cam.data.lens = 28 # Wide focal length so the entire track fills screen edge-to-edge
    cam.data.clip_end = 350

# Save blend
bpy.ops.wm.save_as_mainfile(filepath=r"c:\Users\yurab\OneDrive\Desktop\temp\race_track_scene.blend")
print("Camera re-centered on track action.")

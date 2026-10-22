"""Quick preview render of the race track scene."""
import bpy
import os

# Set up a fast preview render
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

# Output path
output_path = r"c:\Users\yurab\OneDrive\Desktop\temp\race_track_preview.png"
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'PNG'

# Render
bpy.ops.render.render(write_still=True)
print(f"Preview rendered to: {output_path}")

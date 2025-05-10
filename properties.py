"""
Il modulo gestisce le proprietà aggiunte dall'add-on
"""

import bpy
from bpy.types import Camera

# ... proprietà per la GUI ...
class PixelizeProperties(bpy.types.PropertyGroup):
    """
    Proprietà dell'addon
    """
    
    # proprietà per il mapping
    camera: bpy.props.PointerProperty(name = "Camera", type = Camera)  # consente la selezione della camera dalla quale renderizzare
    camera_x_resolution: bpy.props.IntProperty(name = "Camera Resolution X", default = 64)  # risuluzione x della camera
    camera_y_resolution: bpy.props.IntProperty(name = "Camera Resolution Y", default = 64)  # risoluzione y della camera
    
    # proprietà per il rendering
    preview_samples: bpy.props.IntProperty(name="Preview Samples", default=10, soft_min=1, soft_max=100)
    final_samples: bpy.props.IntProperty(name="Final Samples", default=100, soft_min=1, soft_max=1000)
    subject: bpy.props.PointerProperty(name="Subject", type = bpy.types.Object)
    frame_size: bpy.props.IntProperty(name = "Frame Size", default = 64)
    center_frame: bpy.props.BoolProperty(name = "Center Frame", default = False)
    
    # proprietà per i materiali
    color_palette: bpy.props.StringProperty(name = "Palette Path", default = "")
        
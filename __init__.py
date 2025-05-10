bl_info = {
    "name": "Pixelize",
    "author": "Leonardo Caliendo",
    "version": (1, 0),
    "blender": (4, 3, 0),
    "description": "Advanced techniques for pixel art rendering",
    "category": "Render",
}

import bpy
from bpy.utils import register_class, unregister_class


from . import properties
from . import panels
from . import render
from . import camera
from . import settings
from . import materials
from . import buffers


def register():
    """
    Il metodo gestisce la registrazione dei componenti blender
    """
    
    # ... proprietà ...
    register_class(properties.PixelizeProperties)
    bpy.types.Scene.pixel_props = bpy.props.PointerProperty(type = properties.PixelizeProperties)
    
    # ... operatori ...
    register_class(settings.SetupPixelArtEnvironment)
    register_class(camera.CameraMappingGroupSetting)
    register_class(buffers.ClearBuffers)
    register_class(materials.ImportColorPalette)
    register_class(render.RenderPixelArt)
    register_class(render.RenderPixelArtPreview)
    register_class(render.RenderPixelArtAnimation)
    register_class(render.RenderMultiAngle)
    register_class(render.RenderMultiAngleAnimation)
    
    # ... interfaccia grafica ...
    register_class(panels.RenderingPanel)
    register_class(panels.PixelArtMaterialPanel)
    
def unregister():
    """
    Il metodo gestisce la cancellazione delle componenti
    """
    
    # ... proprietà ...
    del bpy.types.Scene.pixel_props
    unregister_class(properties.PixelizeProperties)
    
    # ... operatori ...
    unregister_class(settings.SetupPixelArtEnvironment)
    unregister_class(camera.CameraMappingGroupSetting)
    unregister_class(buffers.ClearBuffers)
    unregister_class(materials.ImportColorPalette)
    unregister_class(render.RenderPixelArt)
    unregister_class(render.RenderPixelArtPreview)
    unregister_class(render.RenderPixelArtAnimation)
    unregister_class(render.RenderMultiAngle)
    unregister_class(render.RenderMultiAngleAnimation)

    # ... interfaccia grafica ...
    unregister_class(panels.RenderingPanel)
    unregister_class(panels.PixelArtMaterialPanel)


if __name__ == "__main__":
    register()
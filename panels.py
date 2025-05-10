"""
Il modulo offre la gestione del pannello di rendering
"""

from bpy.types import Panel, Scene, Context, UILayout

class RenderingPanel(Panel):
    """
    La classe definisce il pannello di interfaccia nella sezione rendering.
    """
    
    bl_label: str = "Pixelize Rendering"
    bl_idname: str = "PT_Pixelize"
    bl_space_type: str = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw(self, context: Context) -> None:
        """
        Il metodo gestisce come viene mostrato a schermo il pannello
        """
        layout = self.layout
        scene = context.scene
        
        layout.operator("settings.pixelize")
        
        # ... gestione della camera ...
        layout.prop(scene.pixel_props, "camera")
        layout.prop(scene.pixel_props, "camera_x_resolution")
        layout.prop(scene.pixel_props, "camera_y_resolution")
        
        layout.operator("cameramapping.setup")

        # ... campi di testo per le proprietà ...
        layout.prop(scene.pixel_props, "preview_samples")
        layout.prop(scene.pixel_props, "final_samples")
        layout.prop(scene.pixel_props, "center_frame")
        
        # ... tasto per il nuovo materiale ...
        layout.operator("render.pixelart_preview")
        layout.operator("render.pixelart")
        layout.operator("render.pixelart_animation")
        
        # ... rendering avanzato ...
        layout.prop(scene.pixel_props, "subject")
        layout.prop(scene.pixel_props, "frame_size")
        layout.operator("render.multi_angle")
        layout.operator("render.multiangle_animation")
        

class PixelArtMaterialPanel(Panel):
    """
    La classe definisce l'interfaccia del pannello dei materiali
    """
    
    bl_label: str = "Pixel Art Materials"
    bl_idname: str = "PT_Pixelize_Materials"
    bl_space_type: str = "PROPERTIES"
    bl_region_type: str = "WINDOW"
    bl_context: str = "material"
    
    def draw(self, context: Context):
        """
        Il metodo definisce come viene rappresentato il panel.
        """
        
        layout: UILayout = self.layout
        scene: Scene = context.scene
        
        # ... campi per l'inserimento dei parametri ...
        layout.prop(scene.pixel_props, "color_palette")
        
        # ... tasti per l'invocazione degli operatori ...
        #layout.operator("material.create")
        layout.operator("material.palette")
        layout.operator("material.new_material")
        layout.operator("material.clear_buffers")

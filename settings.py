"""
Il modulo gestisce la configurazione dei parametri di base per il rendering in pixel art
"""

import bpy
from bpy.types import Operator, Scene, NodeTree, Node, Context

from . import materials
from . import buffers
from . import const


class SetupPixelArtEnvironment(Operator):
    """
    Classe che consente il set-up del rendering in pixel art
    """
    
    bl_label = "Setup Pixel Art Environment"
    bl_idname = "settings.pixelize"
    
    def basic_setup(self):
        """
        Imposta i parametri di base
        """
        
        data = bpy.data
        scene = data.scenes["Scene"]
        cycles = scene.cycles
        scene.render.engine = "CYCLES"  # setta il motore di rendering
        
        # ... parametri di rendering ...
        cycles.samples = 1
        cycles.max_bounces = 0
        cycles.diffuse_bounces = 0
        cycles.glossy_bounces = 0
        cycles.filter_width = 0.01
        scene.view_settings.view_transform = "Standard"
        scene.render.dither_intensity = 0
        bpy.data.scenes["Scene"].render.image_settings.compression = 0
        bpy.data.scenes["Scene"].render.image_settings.color_depth = '16'
        bpy.data.scenes["Scene"].render.film_transparent = True
        bpy.data.cameras["Camera"].type = "ORTHO"  # cambia il tipo di camera usata
    
    def set_freestyle(self):
        """
        Il metodo gestisce le impostazioni di Freestyle
        """
        
        # ... setting del freestyle ...
        scene: Scene = bpy.data.scenes["Scene"]
        scene.render.use_freestyle = True
        scene.render.line_thickness_mode = "RELATIVE"
        bpy.data.linestyles["LineStyle"].thickness = 4.4
        bpy.data.linestyles["LineStyle"].thickness_position = "INSIDE"
        
    def set_compositor(self):
        """
        Il metodo gestisce il setting del compositor
        """
        
        scene: Scene = bpy.data.scenes["Scene"]
        scene.use_nodes = True
        composition_tree: NodeTree = scene.node_tree
        
        if len(composition_tree.nodes) > 3: return
        
        # ... nodo di uscita ...
        output_node: Node = composition_tree.nodes["Composite"]
        output_node.location = (0, 0)  
        
        render_node: Node = composition_tree.nodes["Render Layers"]
        render_node.location = (-600, -600)
        
        mix_node: Node = composition_tree.nodes.new("CompositorNodeMixRGB")
        mix_node.location = (-300, 0)
        
        freestyle_node: Node = composition_tree.nodes.new("CompositorNodeImage")
        freestyle_node.location = (-600, 600)
        freestyle_node.image = bpy.data.images[const.FREESTYLE_BUFFER]
        
        border_node: Node = composition_tree.nodes.new("CompositorNodeImage")
        border_node.location = (-600, 0)
        border_node.image = bpy.data.images[const.BORDER_BUFFER]
        
        # ... collegamenti ...
        composition_tree.links.new(mix_node.outputs["Image"], output_node.inputs["Image"])
        composition_tree.links.new(freestyle_node.outputs["Image"], mix_node.inputs[0])
        composition_tree.links.new(border_node.outputs["Image"], mix_node.inputs[1])
        composition_tree.links.new(render_node.outputs["Image"], mix_node.inputs[2])
        
    def execute(self, context: Context):
        """
        Esegue l'operazione
        """
        
        self.basic_setup()
        
        # ... creazione materiali ...
        materials.PixelArtMaterialsUtils.new_material(const.DIFFUSE_MATERIAL, "ShaderNodeBsdfPrincipled")
        materials.PixelArtMaterialsUtils.new_material(const.EMISSION_MATERIAL, "ShaderNodeEmission")
        
        # ... buffer per il rendering ...
        buffers.BufferUtils.new_buffer(const.DIFFUSE_BUFFER)
        buffers.BufferUtils.new_buffer(const.FREESTYLE_BUFFER)
        buffers.BufferUtils.new_buffer(const.BORDER_BUFFER)
        bpy.ops.file.pack_all()  # salva i buffer
        
        self.set_freestyle()
        self.set_compositor()
        return {'FINISHED'}
"""
Il modulo offre le funzionalità per la gestione della camera
"""

import bpy
from bpy.types import Operator, NodeGroup, Node, Context, Camera

from . import const

class CameraMappingGroupSetting(Operator):
    """
    Operatore che consente il settaggio dell'nodo di mapping della camera
    """
    
    bl_idname: str = "cameramapping.setup"
    bl_label: str = "Setting Camera Mapping Group"
    
    # ... costanti ...
    CAMERA_SCALE_NODE: str = "CameraScale"
    CAMERA_RESOLUTION_X_NODE: str = "CameraResX"
    CAMERA_RESOLUTION_Y_NODE: str = "CameraResY"
    CAMERA_COORD_NODE: str = "CoordNode"
    
    # ... metodi ...
    def _define_input_node(self, group: NodeGroup) -> Node:
        """
        Il metodo regola la creazione di un nodo di ingresso
        """
        
        node: Node = group.nodes.new("NodeGroupInput")
        node.location = (-1000, 0)
        return node
    
    def _define_output_node(self, group: NodeGroup) -> Node:
        """
        Il metodo regola la definizione del nodo di uscita.
        """
        
        group.interface.new_socket(name = "LightingData", in_out = 'OUTPUT', socket_type = "NodeSocketFloat")  # aggiunge un pin di uscita al gruppo
        node: Node = group.nodes.new("NodeGroupOutput")
        node.location = (0, 0)
        return node
    
    def _define_texture_node(self, group: NodeGroup) -> Node:
        """
        Il metodo regola la definizione del nodo per le texture
        """
        
        node: Node = group.nodes.new("ShaderNodeTexImage")
        node.location = (-400, 0)
        node.image = bpy.data.images[const.DIFFUSE_BUFFER]
        node.extension = "CLIP"
        node.interpolation = "Closest"
        return node
    
    def _define_offset_node(self, group: NodeGroup) -> Node:
        """
        Il metodo regola la definizione di un nodo di offset
        """
        
        node: Node = group.nodes.new("ShaderNodeVectorMath")
        node.location = (-700, 0)
        node.inputs[1].default_value = (0.5, 0.5, 0.5)
        node.operation = 'ADD'
        return node
    
    def _define_combine_node(self, group: NodeGroup) -> Node:
        """
        Il metodo regola la definizione di un nodo di combinazione
        """
        
        node: Node = group.nodes.new("ShaderNodeCombineXYZ")
        node.location = (-1000, 0)
        return node
    
    def _define_scale_x_node(self, group: NodeGroup) -> Node:
        """
        Il metodo definisce la creazione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeMath")
        node.location = (-1300, 0)
        node.operation = 'DIVIDE'
        return node
    
    def _define_scale_y_node(self, group: NodeGroup) -> Node: 
        """
        Il metodo definisce la creazione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeMath")
        node.location = (-1300, 300)
        node.operation = 'DIVIDE'
        return node
    
    def _define_separation_node(self, group: NodeGroup) -> Node:
        """
        Il metodo definisce il nodo di separazione
        """
        
        node: Node = group.nodes.new("ShaderNodeSeparateXYZ")
        node.location = (-1600, 0)
        return node
    
    def _define_camera_scale_y_node(self, group: NodeGroup) -> Node:
        """
        Il metodo gestisce la definizione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeMath")
        node.location = (-1600, -300)
        node.operation = 'MULTIPLY'
        return node
    
    def _define_camera_scale_node(self, group: NodeGroup, camera_name: str) -> Node:
        """
        Il metodo consente la definizione del metodo
        """
        
        node: Node = group.nodes.new("ShaderNodeValue")
        node.location = (-1900, -300)
        node.label = self.CAMERA_SCALE_NODE
        node.name = self.CAMERA_SCALE_NODE
        node.outputs[0].default_value = bpy.data.cameras[camera_name].ortho_scale
        return node
    
    def _define_camera_ratio_node(self, group: NodeGroup) -> Node:
        """
        Il metodo gestisce la creazione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeMath")
        node.location = (-1900, -600)
        node.operation = 'DIVIDE'
        return node
    
    def _define_camera_res_x_node(self, group: NodeGroup, width: int) -> Node:
        """
        Il metodo gestisce la definizione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeValue")
        node.location = (-2200, -600)
        node.label = self.CAMERA_RESOLUTION_X_NODE
        node.name = self.CAMERA_RESOLUTION_X_NODE
        node.outputs[0].default_value = width
        return node        
    
    def _define_camera_res_y_node(self, group: NodeGroup, height: int) -> Node:
        """
        Il metodo gestisce la creazione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeValue")
        node.location = (-2200, -900)
        node.label = self.CAMERA_RESOLUTION_Y_NODE
        node.name = self.CAMERA_RESOLUTION_Y_NODE
        node.outputs[0].default_value = height
        return node   
    
    def _define_coord_node(self, group: NodeGroup, camera_name: str) -> Node:
        """
        Il metodo gestice la creazione del nodo
        """
        
        node: Node = group.nodes.new("ShaderNodeTexCoord")
        node.location = (-2200, 0)
        node.label = self.CAMERA_COORD_NODE
        node.name = self.CAMERA_COORD_NODE
        node.object = bpy.data.objects[camera_name]
        return node
    
    def adjust(self, camera_name: str,  width: int, height: int) -> None:
        """
        Il metodo consente di adeguare il gruppo alle nuove impostazioni della camera
        """
        
        group: NodeGroup = bpy.data.node_groups[const.CAMERA_MAPPING_GROUP]  # ricava il gruppo
        
        # ... regola i nodi di mapping della camera ...
        group.nodes[self.CAMERA_SCALE_NODE].outputs[0].default_value = bpy.data.cameras[camera_name].ortho_scale
        group.nodes[self.CAMERA_RESOLUTION_X_NODE].outputs[0].default_value = width
        group.nodes[self.CAMERA_RESOLUTION_Y_NODE].outputs[0].default_value = height
        group.nodes[self.CAMERA_COORD_NODE].object = bpy.data.objects[camera_name]
        
        return
        
    def create(self, camera_name: str, width: int, height: int) -> None:
        """
        Il metodo consente la creazione del nodo di mapping
        """
        
        group: NodeGroup = bpy.data.node_groups.new(type = "ShaderNodeTree", name = const.CAMERA_MAPPING_GROUP)  # crea il gruppo
        
        # ... setting dei nodi ...
        input_node: Node = self._define_input_node(group)
        output_node: Node = self._define_output_node(group)  
        texture_node: Node = self._define_texture_node(group)
        offset_node: Node = self._define_offset_node(group)
        combine_node: Node = self._define_combine_node(group)
        scale_x_node: Node = self._define_scale_x_node(group)
        scale_y_node: Node = self._define_scale_y_node(group)
        separate_node: Node = self._define_separation_node(group)
        camera_scale_y_node: Node = self._define_camera_scale_y_node(group)
        camera_scale_node: Node = self._define_camera_scale_node(group, camera_name)
        camera_ratio_node: Node = self._define_camera_ratio_node(group)
        camera_res_x_node: Node = self._define_camera_res_x_node(group, width)
        camera_res_y_node: Node = self._define_camera_res_y_node(group, height)
        coord_node: Node = self._define_coord_node(group, camera_name)
        
        # ... collegamenti ...
        group.links.new(texture_node.outputs["Color"], output_node.inputs[0])  # texture -> output
        group.links.new(offset_node.outputs["Vector"], texture_node.inputs["Vector"])  # offset -> texture
        group.links.new(combine_node.outputs["Vector"], offset_node.inputs[0])  # combine -> offset
        group.links.new(scale_x_node.outputs["Value"], combine_node.inputs["X"])  # scale_x -> combine
        group.links.new(scale_y_node.outputs["Value"], combine_node.inputs["Y"])  # scale_y -> combine
        group.links.new(separate_node.outputs["X"], scale_x_node.inputs[0])  # separate -> scale_x
        group.links.new(separate_node.outputs["Y"], scale_y_node.inputs[0])  # separate -> scale_y
        group.links.new(coord_node.outputs["Object"], separate_node.inputs["Vector"])  # camera_scale_y -> separate
        group.links.new(camera_scale_y_node.outputs[0], scale_y_node.inputs[1])  # camera_scale_y -> scale_y
        group.links.new(camera_scale_node.outputs["Value"], scale_x_node.inputs[1])  # camera_scale -> scale_x
        group.links.new(camera_scale_node.outputs["Value"], camera_scale_y_node.inputs[0])  # camera_scale -> camera_scale_y
        group.links.new(camera_ratio_node.outputs["Value"], camera_scale_y_node.inputs[1])  # camera_ratio -> camera_scale_y
        group.links.new(camera_res_y_node.outputs["Value"], camera_ratio_node.inputs[0])  # camera_res_y -> camera_ratio
        group.links.new(camera_res_x_node.outputs["Value"], camera_ratio_node.inputs[1])  # camera_res_x -> camera_ratio
          
    def execute(self, context: Context):
        """
        Il metodo gestice l'esecuzione del operatore
        """
        
        # ... ricava le nuove dimensioni richieste della camera ...
        width: int = context.scene.pixel_props.camera_x_resolution
        height: int = context.scene.pixel_props.camera_y_resolution
        camera: Camera = context.scene.pixel_props.camera
        camera_name: str = camera.name
        
        # ... camera ...
        camera_obj = bpy.data.objects[camera_name]  # ottiene la camera richiesta.
        if camera_obj is not None :
            bpy.context.scene.camera = camera_obj  # setta la camera
        else: return {'CANCELLED'}
        
        bpy.data.scenes["Scene"].render.resolution_x = width
        bpy.data.scenes["Scene"].render.resolution_y = height
        
        
        if const.CAMERA_MAPPING_GROUP in bpy.data.node_groups:  # se il nodo esiste già
            self.adjust(camera_name, width, height)
        else:
            self.create(camera_name, width, height)
            
        return {'FINISHED'}
"""
Il modulo contiene le funzionalità necessarie per la gestione dei materiali.
"""

from mathutils import Color
from bpy.types import Node, Material, Operator, Panel, Context, UILayout, Scene
import bpy
import os
from dataclasses import dataclass
from typing import Optional, Any
import json

from . import const

@dataclass
class PixelizeColor:
    """
    classe che incapsula i dati sul colore del materiale pixelize
    """
    
    gradients: dict[float, Color]  # associa ai livelli della color map i colori
    border: Color  # il colore del bordo
    dithering: float  # il valore di dithering da applicare
    light: Optional[Color] # il colore da usare per la sfumatura chiara
    dark: Optional[Color]  # il colore da usare per la sfumatura scura
     

class PixelArtMaterialsUtils:
    """
    La classe raccoglie una serie di funzionalità di base per la gestione dei materiali.
    """
    
    MIN_VALUE: float = 0.1  # valore minimo di luminosità
    
    @staticmethod
    def hex_to_color(hex_color: str) -> Color:
        """
        Il metodo consente di ottenere un colore a paritire dal suo codice esadecimale
        
        Args:
            - hex_color: il codice esadecimale che individua il colore.
            
        Returns:
            - il colore corrispondente al codice esadecimale.
        """
        # Rimuove il simbolo '#' se presente
        print(hex_color)
        hex_color = hex_color.lstrip('#')
        
        r, g, b = [int(hex_color[i:i+2], 16)  / 255 for i in (0, 2, 4)]
        
        return Color((r, g, b)).from_srgb_to_scene_linear()  # per mantenere la coerenza con il colore
    
    @staticmethod
    def new_material(name: str, material_type) -> Material:
        """
        Il metodo gestisce la creazione di un nuovo materiale.
        
        Args:
            - name: il node da assegnare al materiale
            - material_type: il tipo di materiale da usare
            
        Returns:
            - il nuovo materiale creato
        """    
        
        if name in bpy.data.materials:
            print("Il materiale esiste già")
            return bpy.data.materials[name]
        
        material: Material = bpy.data.materials.new(name)  # crea un nuovo materiale
        material.use_fake_user = True  # evita che il materiale venga rimosso
        material.use_nodes = True
        
        bsdf: Node = material.node_tree.nodes["Principled BSDF"]
        material.node_tree.nodes.remove(bsdf)
        
        # ... ottiene il canale di output ...
        material_output: Node = material.node_tree.nodes["Material Output"]
        material_output.location = (0, 0)  # posizione il nodo di ouscita
        
        # ... crea un nuovo shader ...
        shader: Node = material.node_tree.nodes.new(material_type)  # crea un nuovo shader
        shader.location = (-200, 0)
        shader.inputs[0].default_value = (1, 1, 1, 1)
        
        material.node_tree.links.new(shader.outputs[0], material_output.inputs[0])  # collega lo shader all'uscita
        
        return material 
    
    @staticmethod
    def set_mapping_node(material: Material) -> Node:
        """
        Il metodo setta il nodo di mapping per il materiale.
        """
        mapping_node: Node = material.node_tree.nodes.new("ShaderNodeGroup")
        mapping_node.node_tree = bpy.data.node_groups[const.CAMERA_MAPPING_GROUP]
        mapping_node.location = (-1300, 0)
        return mapping_node
    
    @staticmethod
    def set_mix_node(material: Material, color_gradient: PixelizeColor) -> Node:
        """
        Il metodo setta il nodo di mix per il materiale.
        """
        
        mix_node: Node = material.node_tree.nodes.new("ShaderNodeMixRGB")
        color: Color = color_gradient.border
        mix_node.inputs[2].default_value = color.r, color.g, color.b, 1  # il colore del bordo dell'immagine
        mix_node.location = (-400, 0)
        return mix_node
    
    @staticmethod
    def set_border_node(material: Material) -> Node:
        """
        Il metodo genera il nodo per la gestione del bordo
        """
        border_node: Node = material.node_tree.nodes.new("ShaderNodeValue")
        border_node.location = (-700, 100)
        border_node.label = "IsBorder"
        border_node.outputs[0].default_value = 0
        return border_node
    
    @staticmethod
    def set_color_ramp(material: Material, color_gradient: PixelizeColor) -> Node:
        """
        Il metodo gestisce il nodo per la gestione del colore basandosi sul dizionario gradients di PixelizeColor.
        """
        
        # Creazione del nodo Color Ramp
        ramp_node: Node = material.node_tree.nodes.new("ShaderNodeValToRGB")
        ramp_node.location = (-800, 0)
        ramp_node.color_ramp.interpolation = "CONSTANT"

        # Ordiniamo i gradienti per posizione e impostiamo i colori
        sorted_gradients = sorted(color_gradient.gradients.items())  # Ordina in base alla posizione
        
        # Assicuriamoci che ci siano abbastanza elementi nella color ramp
        while len(ramp_node.color_ramp.elements) < len(sorted_gradients):
            ramp_node.color_ramp.elements.new(0.5)  # Posizione arbitraria, verrà sovrascritta

        # Impostiamo i colori
        for i, (position, color) in enumerate(sorted_gradients):
            ramp_node.color_ramp.elements[i].position = position
            ramp_node.color_ramp.elements[i].color = (color.r, color.g, color.b, 1)

        return ramp_node
    
    @staticmethod
    def set_add_node(material: Material, dithering: float) -> Node:
        """
        Il metodo consente di aggiungere il nodo per sommare il dithering al camera mapping
        
        Args:
            - material: il materiale a cui aggiungere il nodo.
            - dithering: regola quanto dithering applicare.
        """
        
        add_node: Node = material.node_tree.nodes.new("ShaderNodeMixRGB")
        add_node.blend_type = "ADD"
        add_node.location = (-1000, -500)
        add_node.inputs[0].default_value = dithering
        return add_node
    
    @staticmethod
    def set_texture_checker_node(material: Material, color: PixelizeColor) -> Node:
        """
        Il metodo crea il nodo per il checking delle texture
        """
        node: Node = material.node_tree.nodes.new("ShaderNodeTexChecker")
        node.location = (-1300, -1000)
        
        node.inputs[1].default_value = color.light.r, color.light.g, color.light.b, 1
        node.inputs[2].default_value = color.dark.r, color.dark.g, color.dark.b, 1
        
        return node
    
    @staticmethod
    def set_combine(material: Material) -> Node:
        """
        Il metodo crea il nodo per combinare il dithering su x ed y
        """
        
        node: Node = material.node_tree.nodes.new("ShaderNodeCombineXYZ")
        node.location = (-1500, -1000)
        return node
    
    @staticmethod
    def set_multiply_x(material: Material) -> Node:
        """
        Il metodo crea il nodo per miltiplicare la componente x
        """
        
        node: Node = material.node_tree.nodes.new("ShaderNodeMath")
        node.operation = "MULTIPLY"
        node.location = (-1700, -800)
        return node   
    
    @staticmethod
    def set_multiply_y(material: Material) -> Node:
        """
        Il metodo crea il nodo per miltiplicare la componente x
        """
        
        node: Node = material.node_tree.nodes.new("ShaderNodeMath")
        node.operation = "MULTIPLY"
        node.location = (-1700, -1200)
        return node   
    
    @staticmethod
    def set_res_x_node(material: Material) -> Node:
        """
        Il metodo setta il nodo che contiene la risoluzione x dell'immagine
        """ 
        
        node: Node = material.node_tree.nodes.new("ShaderNodeValue")
        node.location = (-1900, -800)
        node.label = "ResolutionX"
        return node
    
    @staticmethod
    def set_separate_node(material: Material) -> Node:
        """
        Il metodo setta il nodo per la separazione delle componenti
        """
        
        node: Node = material.node_tree.nodes.new("ShaderNodeSeparateXYZ")
        node.location = (-1900, -1000)
        return node
    
    @staticmethod
    def set_res_y_node(material: Material) -> Node:
        """
        Il metodo setta il nodo che contiene la risoluzione y dell'immagine
        """
        
        node: Node = material.node_tree.nodes.new("ShaderNodeValue")
        node.location = (-1900, -1400)
        node.label = "ResolutionY"
        return node
    
    @staticmethod
    def set_tex_coord(material: Material) -> Node:
        """
        Il metodo setta il nodo per la gestione delle coordinate delle texture.
        """
        
        node: Node = material.node_tree.nodes.new("ShaderNodeTexCoord")
        node.location = (-2100, -1400)
        return node
    
    @staticmethod
    def create_material(name: str, color: PixelizeColor) -> bool:
        """
        Il metodo gestisce la creazione del materiale
        """
        if name == "" or name in bpy.data.materials: return False
        
        # ... creazione dei nodi ...
        material = PixelArtMaterialsUtils.new_material(name, "ShaderNodeEmission")
        mapping_node: Node = PixelArtMaterialsUtils.set_mapping_node(material)
        mix_node: Node = PixelArtMaterialsUtils.set_mix_node(material, color)
        border_node: Node = PixelArtMaterialsUtils.set_border_node(material)
        ramp_node: Node = PixelArtMaterialsUtils.set_color_ramp(material, color)  
        add_node: Node = PixelArtMaterialsUtils.set_add_node(material, color.dithering)  
        checker_node: Node = PixelArtMaterialsUtils.set_texture_checker_node(material, color)
        mul_x_node: Node = PixelArtMaterialsUtils.set_multiply_x(material)
        mul_y_node: Node = PixelArtMaterialsUtils.set_multiply_y(material)
        combine_node: Node = PixelArtMaterialsUtils.set_combine(material)
        separate_node: Node = PixelArtMaterialsUtils.set_separate_node(material)
        res_x_node: Node = PixelArtMaterialsUtils.set_res_x_node(material)  # viene aggiornato automaticamente al momento del rendering
        res_y_node: Node = PixelArtMaterialsUtils.set_res_y_node(material)  # ... idem
        tex_coord_node: Node = PixelArtMaterialsUtils.set_tex_coord(material)
        
        # ... gestione dei collegamenti ...
        links = material.node_tree.links
        links.new(tex_coord_node.outputs["Window"], separate_node.inputs["Vector"])
        links.new(separate_node.outputs["X"], mul_x_node.inputs[0])
        links.new(res_x_node.outputs["Value"], mul_x_node.inputs[1])
        links.new(separate_node.outputs["Y"], mul_y_node.inputs[0])
        links.new(res_y_node.outputs["Value"], mul_y_node.inputs[1])
        links.new(mul_x_node.outputs["Value"], combine_node.inputs["X"])
        links.new(mul_y_node.outputs["Value"], combine_node.inputs["Y"])
        links.new(combine_node.outputs["Vector"], checker_node.inputs["Vector"])
        links.new(mapping_node.outputs["LightingData"], add_node.inputs["Color1"])
        links.new(checker_node.outputs["Color"], add_node.inputs["Color2"])
        links.new(add_node.outputs["Color"], ramp_node.inputs["Fac"])
        links.new(ramp_node.outputs["Color"], mix_node.inputs["Color1"])
        links.new(border_node.outputs["Value"], mix_node.inputs["Fac"])
        links.new(mix_node.outputs["Color"], material.node_tree.nodes["Emission"].inputs["Color"])
        
        return True
    
    
class ImportColorPalette(Operator):
    """
    Operatore che consente di importare una palette di colori a partire da un file '.hex'
    """
    
    bl_idname: str = "material.palette"
    bl_label: str = "Import Color Palette"
    
    @staticmethod
    def read_palette_file(path: str) -> dict[str, Color]:
        """
        Il metodo consente la lettura dei codici esadecimali da un file
        
        Args:
            - path: il path del file da aprire.
            
        Returns:
            - la lista dei codice esadecimali.
        """
        
        with open(path, "r") as file:
            data: dict[str, Any] = json.load(file)  # carica i dati dal file
            
        palette: dict[str, Color] = {}
        for color_name, material_data in data.items():
            print(color_name)
            print(material_data)
            
            material_color: PixelizeColor = PixelizeColor(
                
                gradients = {float(level): PixelArtMaterialsUtils.hex_to_color(material_data['gradients'][level]) for level in material_data['gradients']},  # carica i gradienti
                border = PixelArtMaterialsUtils.hex_to_color(material_data['border']),
                dithering = material_data['dithering'],
                light = PixelArtMaterialsUtils.hex_to_color(material_data['light']) if material_data['light'] is not None else Color((255, 255, 255)),
                dark = PixelArtMaterialsUtils.hex_to_color(material_data['dark']) if material_data['dark'] is not None else Color((0, 0, 0))
                   
            )
            
            palette[color_name] = material_color
            
        return palette
    
    @staticmethod
    def execute(self, context: Context):
        """
        Il metodo consente l'importazione di una palette cromatica.
        """
        
        path: str = context.scene.pixel_props.color_palette

        if not os.path.exists(path): 
            raise FileNotFoundError(f"il file '{path}' non esiste")
        
        palette: dict[str, PixelizeColor] = ImportColorPalette.read_palette_file(path)  # carica la palette
        for name, color in palette.items():
            PixelArtMaterialsUtils.create_material(name, color)
        
        return {'FINISHED'}
    
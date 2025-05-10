"""
Il modulo offre le funzionalità necessarie per la gestione del rendering
"""

import bpy
from bpy.types import Node, Scene, Operator, Context
import subprocess
from typing import Optional
import os
import math
import sys

# ... installazione di Pillow per il post processing (se manca) ...
subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
from PIL import Image

from . import const
from . import buffers
from . import camera


class RenderUtils:
    """
    classe che raccoglie alcune funzioni di utilità per il rendering
    """
    
    @staticmethod
    def set_node_data(node: Node, is_border: bool) -> None:
        """
        Il metodo setta i dati del nodo
        """
        camera_name: str = bpy.context.scene.camera.name
        
        if node.label == "IsBorder":
            node.outputs[0].default_value = 1 if is_border else 0
            
        if node.label == "CameraScale":
            node.outputs[0].default_value = bpy.data.cameras[camera_name].ortho_scale
            
        if node.label == "ResolutionX":
            node.outputs[0].default_value = bpy.data.scenes["Scene"].render.resolution_x
            
        if node.label == "ResolutionY":
            node.outputs[0].default_value = bpy.data.scenes["Scene"].render.resolution_y 

    @staticmethod
    def center_image(img: Image) -> Image:
        """
        Il metodo centra l'immagine
        """
        
        if img.mode != 'RGBA': img = img.convert('RGBA')
        width, height = img.size
        pixels = img.load()  # carica i pixel
        min_x, min_y = width, height  # inizializza i valori minimi
        max_x, max_y = 0, 0  # inizializza i valori massimi
        
        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] > 0:  # se il pixel non è completamente trasparente
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        
        if min_x > max_x or min_y > max_y:  # se non ci sono pixel visibili
            return img.copy()
        
        print("CENTERING FRAME")
        bbox: tuple[int, int, int, int] = (min_x, min_y, max_x + 1, max_y + 1)  # il rettangolo che contiene l'immagine
        cropped: Image.Image = img.crop(bbox)  # ritaglia l'immagine
        
        center_x, center_y = width // 2, height // 2  # centro dell'immagine
        cropped_width, cropped_height = cropped.size  # dimensioni dell'immagine ritagliata
        offset_x  = center_x - cropped_width // 2  # offset orizzontale
        offset_y  = center_y - cropped_height // 2
        new_img: Image.Image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        new_img.paste(cropped, (offset_x, offset_y))
        
        return new_img
        
    @staticmethod
    def set_render_settings(samples: int = 1, denoising: bool = False, freestyle: bool = False, diffuse_override: bool = False,
                                emission_override: bool = False, is_border: bool = False, use_compositor: bool = False) -> None:
        """
        Il metodo setta i parametri di rendering
        """
            
        scene: Scene = bpy.context.scene
        view_layer = bpy.context.view_layer
            
        # ... settings di base ...
        scene.cycles.samples = samples
        scene.cycles.use_denoising = denoising
        scene.render.use_freestyle = freestyle
        scene.use_nodes = use_compositor
        
        # ... override dei materiali ...
        view_layer.material_override = None
        if diffuse_override: view_layer.material_override = bpy.data.materials[const.DIFFUSE_MATERIAL]
        elif emission_override: view_layer.material_override = bpy.data.materials[const.EMISSION_MATERIAL]
        
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    RenderUtils.set_node_data(node, is_border)
        
        for node_group in bpy.data.node_groups:
            for node in node_group.nodes:
                RenderUtils.set_node_data(node, is_border)
        
    @staticmethod
    def render_pixel_art(samples) -> None:
        """
        Il metodo gestisce il rendering in pixel art
        """
            
        assert bpy.data.filepath  # abort se il file non è salvato
        nodes = bpy.data.node_groups[const.CAMERA_MAPPING_GROUP].nodes  # nodi del gruppo di mapping
        links = bpy.data.node_groups[const.CAMERA_MAPPING_GROUP].links  # collegamenti del gruppo di mapping
            
        scene: Scene = bpy.data.scenes["Scene"]
        resX: int = scene.render.resolution_x
        resY: int = scene.render.resolution_y
        isLandscape: bool = resX >= resY
            
        if bpy.context.scene.camera.type == "ORTHO" and isLandscape:
            links.new(nodes["Vector Math"].outputs[0], nodes["Image Texture"].inputs[0])
        else:
            links.new(nodes[camera.CameraMappingGroupSetting.CAMERA_COORD_NODE].outputs[5], nodes["Image Texture"].inputs[0])
            
        RenderUtils.set_render_settings(samples = samples, denoising = True, diffuse_override = True)
        buffers.BufferUtils.render_buffer(const.DIFFUSE_BUFFER)
        
        RenderUtils.set_render_settings(freestyle=True, emission_override=True)
        buffers.BufferUtils.render_buffer(const.FREESTYLE_BUFFER)
        
        RenderUtils.set_render_settings(is_border=True)
        buffers.BufferUtils.render_buffer(const.BORDER_BUFFER)
        
        RenderUtils.set_render_settings(use_compositor=True)
        bpy.ops.render.render(use_viewport = True, write_still = True)
        
        scene.render.use_freestyle = True  # ripristina il freestyle dopo il rendering
        

    @staticmethod
    def create_spritesheet(frames: list[str], rows: int, cols: int, output_path: str, frame_size: int, center_frame: bool):
        """
        Il metodo consente di sintetizzare una spritesheet a partire da una lista di immagini.
        """

        img: Image = Image.new("RGBA", (frame_size * cols, frame_size * rows))

        idx: int = 0  # l'indice dell'immagine
        for col in range(cols):
            for row in range(rows):
                path: str = frames[idx]
                idx += 1
                frame = Image.open(path + ".png").resize((frame_size, frame_size), Image.NEAREST)
                
                if center_frame: frame = RenderUtils.center_image(frame)  # centra l'immagine
                img.paste(frame, (col * frame_size, row * frame_size))
        
        img.save(output_path)
        

# ... operatori ...
class RenderPixelArt(Operator):
    """
    Operatore che gestisce il rendering in pixel art
    """
    bl_label: str = "Render Pixel Art"
    bl_idname: str = "render.pixelart"
    
    def execute(self, context: Context):
        """
        Esegue l'operazione
        """
        
        RenderUtils.render_pixel_art(context.scene.pixel_props.final_samples)
        return {'FINISHED'}
    
class RenderPixelArtPreview(Operator):
    """
    Operatore che gestisce il rendering in pixel art
    """
    bl_label: str = "Render Pixel Art Preview"
    bl_idname: str = "render.pixelart_preview"
    
    def execute(self, context: Context):
        """
        Esegue l'operazione
        """
        
        RenderUtils.render_pixel_art(context.scene.pixel_props.preview_samples)
        return {'FINISHED'}    
    
class RenderPixelArtAnimation(Operator):
    """
    Operatore che gestisce il rendering in pixel art delle animazioni
    """    
    bl_label: str = "Render Pixel Art Animation"
    bl_idname: str = "render.pixelart_animation"
    
    def execute(self, context: Context):
        """
        Esegue l'operazione
        """
        
        scene: Scene = context.scene
        start = scene.frame_start
        end = scene.frame_end
        path: str = bpy.data.filepath
        for frame in range(start, end):
            scene.frame_current = frame
            scene.render.filepath = path + str(frame)   
            RenderUtils.render_pixel_art(context.scene.pixel_props.final_samples)
            
        return {'FINISHED'}

class RenderMultiAngle(Operator):
    """
    Consente il rendering di un oggetto da diverse angolazioni
    """     
    
    bl_label = "Multi-Angle Rendering"
    bl_idname = "render.multi_angle"
    
    def execute(self, context: Context):
        """
        Gestisce il rendering da 8 angolazioni
        """
        
        subject: Optional[bpy.types.Object] = context.scene.pixel_props.subject
        frame_size: int = context.scene.pixel_props.frame_size
        center_frame: bool = context.scene.pixel_props.center_frame
        if subject is None: return
        path: str = os.path.dirname(bpy.data.filepath)  # la cartella in cui si trova il progetto
        files: list[str] = []  # lista dei file creati
        
        for idx in range(8): 
            angle: int = idx * 45
            subject.rotation_euler[2] = math.radians(angle)
            filepath: str = os.path.join(path, f"frame_{idx}")
            files.append(filepath)
            context.scene.render.filepath = filepath   
            RenderUtils.render_pixel_art(context.scene.pixel_props.final_samples)
        
        output_path: str = os.path.join(path, 'multiangle.png')
        RenderUtils.create_spritesheet(files, 8, 1, output_path, frame_size=frame_size, center_frame=center_frame)
        
        for file in files: os.remove(file + '.png')  # cancella i singoli frame
        subject.rotation_euler[2] = math.radians(0)  # applica la rotazione
        return {'FINISHED'}


class RenderMultiAngleAnimation(Operator):
    """
    Operatore che gestisce il rendering in pixel art delle animazioni
    """
    bl_label: str = "Render MultiAngle Animation"
    bl_idname: str = "render.multiangle_animation"

    def execute(self, context: Context):
        """
        Esegue l'operazione
        """

        subject: Optional[bpy.types.Object] = context.scene.pixel_props.subject
        frame_size: int = context.scene.pixel_props.frame_size
        if subject is None: return

        scene: Scene = context.scene
        start = scene.frame_start
        end = scene.frame_end
        path: str = os.path.dirname(bpy.data.filepath)  # la cartella in cui si trova il progetto
        frames: list[str] = []

        idx: int = 0
        tot_frames: int = 0
        for frame in range(start, end + 1):
            scene.frame_current = frame

            tot_frames += 1
            for phi in range(8):
                angle: int = phi * 45
                subject.rotation_euler[2] = math.radians(angle)  # applica la rotazione
                filepath: str = os.path.join(path, f"frame_{idx}")
                idx += 1
                frames.append(filepath)
                context.scene.render.filepath = filepath
                RenderUtils.render_pixel_art(context.scene.pixel_props.final_samples)

            subject.rotation_euler[2] = math.radians(0)  # applica la rotazione

        output_path: str = os.path.join(path, 'animation.png')
        RenderUtils.create_spritesheet(frames, 8, tot_frames, output_path,frame_size = frame_size, center_frame=context.scene.pixel_props.center_frame)

        for file in frames: os.remove(file + '.png')
        return {'FINISHED'}
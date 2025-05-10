"""
Il modulo offre delle funzionalità per la gestione dei buffer
"""

import bpy
from bpy.types import Scene, Operator, Context
import os

from . import const


class BufferUtils:
    """
    La classe raccoglie delle funzionalità di utilità per la gestione dei buffer
    """
    
    @staticmethod
    def new_buffer(name: str) -> None: 
        """
        Il metodo consente la creazione di un nuovo buffer per il rendering.

        Args:
            name (str): il nome del buffer.
        """
        
        if name in bpy.data.images:
            print("Il buffer esiste già")
            return bpy.data.images[name]
        
        scene: Scene = bpy.data.scenes["Scene"]
        rw: int = scene.render.resolution_x
        rh: int = scene.render.resolution_y
        bpy.ops.image.new(name=name, width=rw, height=rh, alpha=True)  
        bpy.data.images[name].use_fake_user = True  # evita che l'immagine venga rimossa
        return


    @staticmethod
    def clear_buffer(name: str) -> None:
        """
        Il metodo consente di ripulire il buffer
        """
        
        if name not in bpy.data.images: return
        
        img = bpy.data.images[name]

        # Assicura che l'immagine abbia dati di pixel
        width, height = img.size
        values: list[float] = [0.0 for _ in range(width * height * 4)]
        img.pixels.foreach_set(values)
        img.update()


    @staticmethod
    def render_buffer(buffer_name: str) -> None:
        """
        Il metodo gestisce il rendering del buffer.
        """
        
        old_path: str = bpy.data.scenes["Scene"].render.filepath
        new_path: str = "//" + buffer_name + ".png"
        bpy.data.scenes["Scene"].render.filepath = new_path
        
        bpy.ops.render.render(use_viewport = True, write_still = True)
        bpy.data.scenes["Scene"].render.filepath = old_path
        
        tex = bpy.data.images[buffer_name]
        tex.source = "FILE"
        tex.filepath = new_path
        tex.reload()
        tex.pack()
        
        os.remove(bpy.path.abspath(new_path))  # rimuove il file temporaneo
        

class ClearBuffers(Operator):
    """
    Operatore che consente la pulizia dei buffer di rendering
    """
    
    bl_label: str = "Clear Buffers"
    bl_idname: str = "material.clear_buffers"
    
    def execute(self, context: Context):
        """
        Il metodo consente la pulizia dei buffer
        """
        
        BufferUtils.clear_buffer(const.DIFFUSE_BUFFER)
        BufferUtils.clear_buffer(const.FREESTYLE_BUFFER)
        BufferUtils.clear_buffer(const.BORDER_BUFFER)
import bpy
import os
import sys
import numpy as np
from mathutils import *

import time

def get_argument(arg):
    args = sys.argv
    for i in range(len(args)):
        if args[i] == arg:
            return args[i+1]
    print("Could not find argument for ", arg)
    return None

def render_exr(filename, output_dir, res_x, res_y):
    for node in bpy.context.scene.node_tree.nodes:
        if node.name == "File Output":
            fileoutput_node = node
            
    bpy.context.scene.use_nodes=True
    bpy.context.scene.view_layers[0].cycles.use_denoising = True
    bpy.context.scene.render.image_settings.file_format='OPEN_EXR'
    bpy.context.scene.render.image_settings.color_mode = 'BW'
    abs_path = os.path.join(os.getcwd(), output_dir)
    full_path = os.path.join(abs_path, filename)
    fileoutput_node.base_path = full_path
    bpy.context.scene.render.filepath = full_path
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.ops.render.render(write_still=False)



if __name__ == '__main__':
    
    bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
    

    
    render_exr("depth-img", "images", 1920, 1080)
    #time.sleep(1)
    
    bpy.context.scene.use_nodes=False
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

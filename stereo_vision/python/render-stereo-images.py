
import bpy
from math import *
import numpy as np
from mathutils import *
import os

def render(filename, output_dir, res_x, res_y):
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, filename + ".png")
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    PIXELS_X = 1920
    PIXELS_Y = 1080

    scene = bpy.context.scene
    scene.camera = bpy.data.objects["LeftCamera"]
    render("leftCam", "images/stereo-images", PIXELS_X, PIXELS_Y)
    scene.camera = bpy.data.objects["RightCamera"]
    render("rightCam", "images/stereo-images", PIXELS_X, PIXELS_Y)

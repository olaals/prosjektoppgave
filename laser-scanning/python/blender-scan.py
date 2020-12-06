import bpy
import os
import sys
import mathutils
import numpy as np
import bpy

def get_argument(arg):
    args = sys.argv
    for i in range(len(args)):
        if args[i] == arg:
            return args[i+1]
            laser_scanner_obj.location = START_POS
    print("Could not find argument for ", arg)
    return None

def render(filename, output_dir, res_x, res_y):
    bpy.context.scene.view_layers[0].cycles.use_denoising = True
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, filename + ".png")
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.ops.render.render(write_still=True)

def writeCSV(filename, matrix):
    np.savetxt(filename, matrix, delimiter=",", fmt='% s')

    


if __name__ == '__main__':
    RES_X = 1920
    RES_Y = 1080
    START_POS = mathutils.Vector((-0.6,-0.5,0.25))
    END_X_POS = 0.6
    NUM_PICS = 120
    X_VALUES = np.linspace(START_POS[0], END_X_POS, NUM_PICS)
    laser_scanner_obj = bpy.data.objects["LaserScannerBase"]
    laser_scanner_obj.location = START_POS
    
    index = 0
    subscripts=["%03d" % x for x in range(NUM_PICS)]
    
    for x in X_VALUES:
        writeCSV("matrices/tf-world-cam/T-W-C" + subscripts[index] + ".csv", laser_scanner_obj.matrix_world)

        print(x)
        print(index)
        laser_scanner_obj.location[0] = x
        render("scan_"+subscripts[index], "images/scan-images", RES_X, RES_Y)
        
        index += 1

    laser_scanner_obj.location = START_POS

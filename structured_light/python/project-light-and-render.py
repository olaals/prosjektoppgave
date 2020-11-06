import bpy
import os
import sys

def get_argument(arg):
    args = sys.argv
    for i in range(len(args)):
        if args[i] == arg:
            return args[i+1]
    print("Could not find argument for ", arg)
    return None

def load_pattern_images(pattern_dir):
    pattern_img_list = []
    file_name_dir_list = os.listdir(pattern_dir)
    file_name_dir_list.sort()
    for file_name in file_name_dir_list:
        image = bpy.data.images.load(os.path.join(pattern_dir, file_name))
        pattern_img_list.append(image)
    return pattern_img_list

def change_pattern_projector(projector_light_name, proj_obj, img):
    img_text_node = None
    for node in bpy.data.lights[projector_light_name].node_tree.nodes:
        if node.name == "Image Texture":
            img_text_node = node
            proj_obj.proj_settings.use_custom_texture_res = True
            proj_obj.proj_settings.use_custom_texture_res = False
    
    if img_text_node == None:
        print("ERROR: light has no image texture node")
    else:
        img_text_node.image = img
        print("Succesfully changed pattern on projector")

def render(filename, output_dir, res_x, res_y):
    bpy.context.scene.view_layers[0].cycles.use_denoising = True
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, filename + ".png")
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.ops.render.render(write_still=True)
    
def turn_off_projector(proj_spot_name):
    spot = bpy.data.lights[proj_spot_name]
    spot.energy = 0

def turn_on_projector(proj_spot_name, power):
    spot = bpy.data.lights[proj_spot_name]
    spot.energy = power


if __name__ == '__main__':
    PATTERN_DIR = get_argument("--pattern")
    if PATTERN_DIR is None:
        PATTERN_DIR = os.path.join(os.getcwd(), "../../../patterns/patterns-7/")
    else:
        PATTERN_DIR = os.path.join(os.getcwd(), PATTERN_DIR)

    OUTPUT_DIR = get_argument("--output")
    if OUTPUT_DIR is None:
        OUTPUT_DIR = os.path.join(os.getcwd(), "images/structure-lighted")
    else:
        OUTPUT_DIR = os.path.join(os.getcwd(), OUTPUT_DIR)
    OUTPUT_FILENAME = "sl_img"
    OUTPUT_NOPROJ_FILENAME = "no-projector"
    OUTPUT_NOPROJ_DIR = "images"
    PROJECTOR_LIGHT_NAME = "Spot"
    RES_X = 1920
    RES_Y = 1080
    PROJECTOR_POWER = 20000
    print(PATTERN_DIR)
    
    proj_obj = bpy.data.objects["Projector"]

    
    print(proj_obj.proj_settings.projected_texture)


    turn_off_projector(PROJECTOR_LIGHT_NAME)
    render(OUTPUT_NOPROJ_FILENAME, OUTPUT_NOPROJ_DIR, RES_X, RES_Y)
    turn_on_projector(PROJECTOR_LIGHT_NAME, PROJECTOR_POWER)

    
    pattern_img_list = load_pattern_images(PATTERN_DIR)
    
    print("")
    print("pattern_img_list")
    print("")
    print(pattern_img_list)
    
    ind = 0
    for pattern_img in pattern_img_list:
        print("index in loop: ", ind)
        change_pattern_projector(PROJECTOR_LIGHT_NAME, proj_obj, pattern_img)
        render(OUTPUT_FILENAME + "_" + str(ind), OUTPUT_DIR, RES_X, RES_Y)
        ind += 1
    

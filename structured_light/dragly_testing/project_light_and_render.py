import bpy
import os


def load_pattern_images(pattern_dir):
    pattern_img_list = []
    file_name_dir_list = os.listdir(pattern_dir)
    file_name_dir_list.sort()
    for file_name in file_name_dir_list:
        image = bpy.data.images.load(os.path.join(pattern_dir, file_name))
        pattern_img_list.append(image)
    return pattern_img_list

def change_pattern_projector(projector_light_name, img):
    img_text_node = None
    for node in bpy.data.lights[projector_light_name].node_tree.nodes:
        if node.name == "Image Texture":
            img_text_node = node
    
    if img_text_node == None:
        print("ERROR: light has no image texture node")
    else:
        img_text_node.image = img
        print("Succesfully changed pattern on projector")

def render(filename, output_dir, res_x, res_y):
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, filename + ".png")
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    PATTERN_DIR = os.path.join(os.path.join(os.getcwd(), os.pardir), "patterns")
    OUTPUT_DIR = os.path.join(os.path.join(os.getcwd(), os.pardir), "struc_lighted")
    OUTPUT_FILENAME = "monkey_refl"
    PROJECTOR_LIGHT_NAME = "Light"
    RES_X = 1920
    RES_Y = 1080
    

    
    pattern_img_list = load_pattern_images(PATTERN_DIR)
    
    ind = 0
    for pattern_img in pattern_img_list:
        change_pattern_projector(PROJECTOR_LIGHT_NAME, pattern_img)
        render(OUTPUT_FILENAME + "_" + str(ind), OUTPUT_DIR, RES_X, RES_Y)
        ind += 1

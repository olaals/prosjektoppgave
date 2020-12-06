import bpy
from math import *
import numpy as np
from mathutils import *
import os

def VecToso3(omg):
    """Converts a 3-vector to an so(3) representation
    :param omg: A 3-vector
    :return: The skew symmetric representation of omg
    Example Input:
        omg = np.array([1, 2, 3])
    Output:
        np.array([[ 0, -3,  2],
                  [ 3,  0, -1],
                  [-2,  1,  0]])
    """
    return Matrix([[0,      -omg[2],  omg[1]],
                     [omg[2],       0, -omg[0]],
                     [-omg[1], omg[0],       0]])

def getEssential(quat_world_leftcam, quat_world_rightcam, transl_world_leftcam, transl_world_rightcam):
    #let C1 = leftcam
    #let C2 = rightcam
    #let W = world
    R_W_C2 = quat_world_rightcam.to_matrix()
    R_C2_W = R_W_C2.transposed()
    R_C2_C1 = quat_world_rightcam.rotation_difference(quat_world_leftcam).to_matrix()
    t_C2_C1_W = transl_world_leftcam - transl_world_rightcam
    t_C2_C1_C2 = R_C2_W @t_C2_C1_W
    essential_matrix = R_C2_C1@VecToso3(t_C2_C1_C2)
    return essential_matrix, R_C2_C1, t_C2_C1_C2

def render(filename, output_dir, res_x, res_y):
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.image_settings.file_format='PNG'
    bpy.context.scene.render.filepath = os.path.join(output_dir, filename + ".png")
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.ops.render.render(write_still=True)
    
def writeCSV(filename, matrix):
    np.savetxt(filename, matrix, delimiter=",", fmt='% s')



print("######   Start blender script: stereo setup   ######")

FOCAL_LEN = bpy.data.cameras["Camera.001"].lens
PIXELS_X = 1920
PIXELS_Y = 1080
PW = 10*10**(-6)
print("Focal length: ", FOCAL_LEN, " mm")
print("Pixels of rendered picture x (width): ", PIXELS_X)
print("Pixels of rendered picture y (height): ", PIXELS_Y)
print("Width of pixel in mm: ", PW)


K = np.array([[FOCAL_LEN*10**(-3)/PW, 0, PIXELS_X/2], [0, FOCAL_LEN*10**(-3)/PW, PIXELS_Y/2],[0,0,1]])
K_inv = 1/(FOCAL_LEN*10**(-3))*np.array([[PW, 0, -PW*PIXELS_X/2],[0, PW, -PW*PIXELS_Y/2],[0,0,FOCAL_LEN*10**(-3)]])

left_cam = bpy.data.objects["LeftCameraAxis"]
right_cam = bpy.data.objects["RightCameraAxis"]
transf_world_leftcam = left_cam.matrix_world
transf_world_rightcam = right_cam.matrix_world

loc_world_leftcam, rot_world_leftcam_quat, _ = transf_world_leftcam.decompose()
loc_world_rightcam, rot_world_rightcam_quat, _ = transf_world_rightcam.decompose()
rot_leftcam_rightcam_quat = rot_world_leftcam_quat.rotation_difference(rot_world_rightcam_quat)
rot_leftcam_rightcam = rot_leftcam_rightcam_quat.to_matrix()

E, R_C2_C1, t_C2_C1_C2 = getEssential(rot_world_leftcam_quat, rot_world_rightcam_quat, loc_world_leftcam, loc_world_rightcam)

print("Camera matrix")
print(K)
print("Inverse camera matrix")
print(K_inv)
print("Essential Matrix")
print(E)

#writeCSV("camera-matrix.csv", K)
#writeCSV("inv-camera-matrix.csv", K_inv)
writeCSV("essential-matrix.csv", E)
writeCSV("R-C2-C1.csv", R_C2_C1)
writeCSV("t-C2-C1-C2.csv", t_C2_C1_C2)

scene = bpy.context.scene
scene.camera = bpy.data.objects["LeftCamera"]
render("leftCam", "stereo-images", PIXELS_X, PIXELS_Y)
scene.camera = bpy.data.objects["RightCamera"]
render("rightCam", "stereo-images", PIXELS_X, PIXELS_Y)

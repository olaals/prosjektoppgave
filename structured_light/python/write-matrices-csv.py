import bpy
import os
import sys
import numpy as np
from mathutils import *

def get_argument(arg):
    args = sys.argv
    for i in range(len(args)):
        if args[i] == arg:
            return args[i+1]
    print("Could not find argument for ", arg)
    return None

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


def writeCSV(filename, matrix, dir=None):
    if dir == None:
        np.savetxt(filename, matrix, delimiter=",", fmt='% s')
    else:
        current_dir = os.getcwd()
        new_folder = os.path.join(current_dir, dir)
        try:
            os.mkdir(new_folder)
        except:
            pass
        save_path = os.path.join(new_folder, filename)
        print("save path")
        print(save_path)
        np.savetxt(save_path, matrix, delimiter=",", fmt='% s')

def get_camera_matrix(focal_len, pixel_dim, res_x, res_y):
    K = np.array([[focal_len*10**(-3)/pixel_dim, 0, res_x/2, 0], [0, focal_len*10**(-3)/pixel_dim, res_y/2, 0],[0,0,1,0], [0,0,0,1]])
    return K

def get_inverse_camera_matrix(focal_len, pixel_dim, res_x, res_y):
    K_inv = 1/(focal_len*10**(-3))*np.array([[pixel_dim, 0, -pixel_dim*res_x/2, 0],[0, pixel_dim, -pixel_dim*res_y/2, 0],[0,0,focal_len*10**(-3), 0], [0,0,0,focal_len*1e-3]])
    return K_inv

def invert_transformation_matrix(transf_mat):
    transl, quat, _ = transf_mat.decompose()
    rot_mat = quat.to_matrix()
    inv_rot_mat = rot_mat.transposed()
    inv_rot_mat_4x4 = inv_rot_mat.to_4x4()
    loc_mat = Matrix.Translation(-transl)
    return inv_rot_mat_4x4@loc_mat

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



if __name__ == '__main__':
    PRINT_INFO = True
    WRITE_CSV = True
    resolution_x = bpy.context.scene.render.resolution_x
    resolution_y = bpy.context.scene.render.resolution_y
    pixel_dim = 10e-6
    focal_len = bpy.data.cameras["Camera.001"].lens
    K = get_camera_matrix(focal_len, pixel_dim, resolution_x, resolution_y)
    K_inv = get_inverse_camera_matrix(focal_len, pixel_dim, resolution_x, resolution_y)

    
    cam_axis = bpy.data.objects["CameraAxis"]
    transf_mat_world_cam = cam_axis.matrix_world
    proj_axis = bpy.data.objects["ProjectorAxis"]
    transf_mat_world_proj = proj_axis.matrix_world
    transf_mat_proj_world = invert_transformation_matrix(transf_mat_world_proj)
    transf_proj_cam = transf_mat_proj_world@transf_mat_world_cam

    loc_world_cam, rot_world_cam_quat, _ = transf_mat_world_cam.decompose()
    loc_world_proj, rot_world_proj_quat, _ = transf_mat_proj_world.decompose()
    E = np.eye(4)
    E3x3, R_PC, t_PCP = getEssential(rot_world_cam_quat, rot_world_proj_quat, loc_world_cam, loc_world_proj)
    print(E3x3)
    E[0:3,0:3] = E3x3
    

    
    
    if WRITE_CSV:
        writeCSV("cam-mat.csv", K, "matrices")
        writeCSV("inv-cam-mat.csv", K_inv, "matrices")
        writeCSV("transf-world-proj.csv", transf_mat_world_proj, "matrices")
        writeCSV("transf-proj-cam.csv", transf_proj_cam, "matrices")
        writeCSV("essential-mat.csv", E, "matrices")
        writeCSV("R_PC.csv", R_PC, "matrices")
        writeCSV("t_PCP.csv", t_PCP, "matrices")
    
    if PRINT_INFO:
        print("Camera matrix")
        print(K)
        print("Inverse camera matrix")
        print(K_inv)
        print("Render resolution_x", resolution_x, " resolution_y: ", resolution_y)
        print("Pixel dim: ", pixel_dim)
        print("Focal length: ", focal_len, "mm")
        print("")
        print("Transformation world to projector")
        print(transf_mat_world_proj)
        print("Transformation world to camera")
        print(transf_mat_world_cam)
        print("Transformation projector to camera")
        print(transf_proj_cam)

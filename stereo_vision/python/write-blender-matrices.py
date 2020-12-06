
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
    
def writeCSV(filename, matrix):
    np.savetxt(filename, matrix, delimiter=",", fmt='% s')

if __name__ == '__main__':

    left_cam = bpy.data.objects["LeftCameraAxis"]
    right_cam = bpy.data.objects["RightCameraAxis"]
    transf_world_leftcam = left_cam.matrix_world
    transf_world_rightcam = right_cam.matrix_world

    loc_world_leftcam, rot_world_leftcam_quat, _ = transf_world_leftcam.decompose()
    loc_world_rightcam, rot_world_rightcam_quat, _ = transf_world_rightcam.decompose()
    rot_leftcam_rightcam_quat = rot_world_leftcam_quat.rotation_difference(rot_world_rightcam_quat)
    rot_leftcam_rightcam = rot_leftcam_rightcam_quat.to_matrix()

    E, R_C2_C1, t_C2_C1_C2 = getEssential(rot_world_leftcam_quat, rot_world_rightcam_quat, loc_world_leftcam, loc_world_rightcam)

    print("Essential Matrix")
    print(E)

    writeCSV("matrices/essential-matrix.csv", E)
    writeCSV("matrices/R-C2-C1.csv", R_C2_C1)
    writeCSV("matrices/t-C2-C1-C2.csv", t_C2_C1_C2)


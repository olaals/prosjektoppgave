import glm
import math
import numpy as np
from scipy.spatial.transform import Rotation as Rot

def convert4x4_glm_to_numpy(glm_mat):
    np_mat = np.zeros((4,4))
    for i in range(4):
        for j in range(4):
            np_mat[i,j] = glm_mat[i,j]
    return np_mat


def create_inverse_projection():
    aspect = 1920.0/1080.0
    fovx = 53.0
    fovy = fovx * (1.0 /aspect) * (math.pi/180)
    near = 0.1
    far = 100.0
    projection = glm.perspective(fovy, aspect, near, far)
    inv_projection_F = glm.inverse(projection)
    inv_projection_np = convert4x4_glm_to_numpy(inv_projection_F)
    return inv_projection_np

def create_inverse_rotation():
    angle = -6.0 / 180.0 * math.pi
    angle_axis = Rot.from_rotvec(angle * np.array([0, 1, 0]))
    rot_mat = angle_axis.as_matrix()
    print(rot_mat)
    inv_rot_mat = rot_mat.transpose()
    return inv_rot_mat

def create_inverse_translation():
    offset = -0.2
    trans = np.array([offset, 0,0])
    inv_trans = -trans
    return inv_trans

def assemble_trans_mat(rot_mat, trans):
    transmat = np.zeros((4,4))
    transmat[3,3] = 1
    transmat[0:3, 0:3] = rot_mat
    transmat[0:3, 3] = trans
    return transmat

def create_inverse_transformation():
    inv_rot = create_inverse_rotation()
    inv_translation = create_inverse_translation()
    inv_transformation = assemble_trans_mat(inv_rot, inv_translation)
    return inv_transformation

def unproject_camera(n_cam, inv_proj, inv_trans):
    
    p_cam = inv_proj@n_cam
    p_cam = p_cam/p_cam[3] # not sure if 3 or 2
    p_pro = inv_trans@p_cam  
    return p_pro

def unproject_projector(n_pro, inv_proj):
    p_pro = inv_pro@n_pro
    p_pro = p_pro/p_pro[3] # not sure if 3 or 2
    return p_pro

def find_camera_line(width, height):
    

a = create_inverse_projection()
print(a)

inv_rot_mat = create_inverse_rotation()
print(inv_rot_mat)

inv_trans = create_inverse_transformation()
print(inv_trans)

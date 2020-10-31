import glm
import math
import numpy as np
from scipy.spatial.transform import Rotation as Rot
import cv2
import matplotlib.pyplot as plt

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
    p_pro = inv_proj@n_pro
    p_pro = p_pro/p_pro[3] # not sure if 3 or 2
    return p_pro

    
def find_camera_line(x, y, width, height, inv_proj, inv_trans):
    nx = 2.0 * x / width - 1.0
    ny = 2.0 * ((1.0 - y) / height) - 1.0
    normal_cam1 = np.array([nx, ny, 0.1, 1.0])
    normal_cam2 = np.array([nx, ny, 0.7, 1.0])
    p_cam1 = unproject_camera(normal_cam1, inv_proj, inv_trans)
    p_cam2 = unproject_camera(normal_cam2, inv_proj, inv_trans)
    l_cam = p_cam2 - p_cam1
    return p_cam1, l_cam

def find_projector_line(projector_x, inv_proj):
    normal_pro = np.array([projector_x, 0, 0.7, 1.0])
    l_pro = unproject_projector(normal_pro, inv_proj)
    return l_pro

def cross2D(a,b):
    return a[0] * b[2] - b[0] * a[2]

def intersect(camera_position1, camera_line, projector_line):
    p = np.array([0.0, 0.0, 0.0, 1.0])
    r = projector_line - p
    q = camera_position1
    s = camera_line

    pxr = cross2D(p,r)
    qxr = cross2D(q,r)
    qmpxr = qxr - pxr
    rxs = cross2D(r,s)
    u_cam = qmpxr / rxs
    return q + s * u_cam


def show_image(img):
    plt.imshow(img, cmap="gray")
    plt.show()

if __name__ == '__main__':
    PRINT_VALS = True
    x_val_img = cv2.imread("sl-projects/monkey/no-reflection/x_val_img.png", cv2.IMREAD_GRAYSCALE)
    HEIGHT, WIDTH = x_val_img.shape
    max_val = np.amax(x_val_img).astype(np.float32)
    print("max_val", max_val)
    x_val_img = x_val_img / max_val - 2.0
    show_image((x_val_img + 2.0) * 255)
    max_val = np.amax(x_val_img)
    print("max_val", max_val)
    print(WIDTH, HEIGHT)
    inv_trans = create_inverse_transformation()
    inv_rot = create_inverse_rotation()
    inv_proj = create_inverse_projection()
    inv_proj = inv_proj.transpose()
    depth_img = np.zeros((HEIGHT, WIDTH))
    STEP = 6

    if PRINT_VALS:
        print("inverse projection")
        print(inv_proj)
        print(inv_proj[2,3])
        print("inverse trans")
        print(inv_trans)
        print("inverse rotation")
        print(inv_rot)

    input("Press Enter to continue...")

    for row in range(HEIGHT):
        for col in range(0, WIDTH, STEP):
            proj_x = x_val_img[row, col]
            if (proj_x == 0):
                continue
            p_cam1, l_cam = find_camera_line(col, row, WIDTH, HEIGHT, inv_proj, inv_trans)
            l_pro = find_projector_line(proj_x, inv_proj)
            intrsect = intersect(p_cam1, l_cam, l_pro)
            if intrsect[2] > 0:
                continue
            depth_img[row,col] = -intrsect[2]
            if PRINT_VALS:
                print("row", row)
                print("col", col)
                print("pos cam")
                print(p_cam1)
                print("camera line")
                print(l_cam)
                print("proj_x")
                print(proj_x)
                print("line projector")
                print(l_pro)
                print("intersection")
                print(intrsect)
            if row*col % (HEIGHT*WIDTH/10) == 0:
                print(row)
    
    print(depth_img)
    print("max val depth img")
    print(np.amax(depth_img))
    
    depth_img = depth_img/np.amax(depth_img)*100
    cv2.imwrite("depth_img.png", depth_img)
    show_image(depth_img)



    










    
"""
a = create_inverse_projection()
print(a)

inv_rot_mat = create_inverse_rotation()
print(inv_rot_mat)

inv_trans = create_inverse_transformation()
print(inv_trans)
"""
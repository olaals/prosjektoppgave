import cv2
import numpy as np

import math
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as Rot

def show_image(img):
    plt.imshow(img, cmap="gray")
    plt.show()

def scale_image_to_x_vals(img, current_max, x_max):
    img = img/current_max * x_max
    return img


def get_camera_mat(foc_len, px_dim, img_width, img_height):
    #foc_len: mm
    #px_dim: m
    #img_width: #num
    foc_len = foc_len*10**(-3)
    u0 = img_width/2
    v0 = img_height/2

    K = np.array([[foc_len/px_dim, 0, u0], [0, foc_len/px_dim,v0], [0, 0, 1]])
    return K

def get_inverse_camera_mat(foc_len, px_dim, img_width, img_height):
    #foc_len: mm
    #px_dim: m
    #img_width: #num
    K_inv = np.zeros((3,3))
    foc_len = foc_len*10**(-3)
    u0 = img_width/2
    v0 = img_height/2

    K_inv[0,0] = px_dim/foc_len
    K_inv[0,2] = -px_dim*u0/foc_len
    K_inv[1,1] = px_dim/foc_len
    K_inv[1,2] = -px_dim*v0/foc_len
    K_inv[2,2] = 1.0
    

    #K_inv = 1/foc_len * np.ndarray([[px_dim, 0, -px_dim * u0], [0, px_dim, -px_dim*v0],[0, 0, foc_len]])

    return K_inv

def create_inverse_rotation():
    angle = 6.0 / 180.0 * math.pi
    angle_axis = Rot.from_rotvec(angle * np.array([0, 1, 0]))
    rot_mat = angle_axis.as_matrix()
    print(rot_mat)
    inv_rot_mat = rot_mat.transpose()
    return inv_rot_mat

def create_inverse_translation():
    offset = 0.2
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
    
def cross2D(a,b):
    return a[0] * b[2] - b[0] * a[2]

if __name__ == '__main__':
    FOCAL_LEN = 36.1 #mm
    PX_DIM = 10e-6

    PRINT_INFO = True
    proj_x_img = cv2.imread("projector-x.png", cv2.IMREAD_GRAYSCALE)
    HEIGHT, WIDTH = proj_x_img.shape
    print(HEIGHT, WIDTH)
    proj_x_img = scale_image_to_x_vals(proj_x_img, 255, WIDTH)
    print(proj_x_img.shape)
    K_inv = get_inverse_camera_mat(FOCAL_LEN, PX_DIM, WIDTH, HEIGHT)
    inv_trans = create_inverse_transformation()
    if PRINT_INFO:
        print(np.amax(proj_x_img))
        print(np.amin(proj_x_img))
        print(get_camera_mat(15, 10e-6, 1280, 1024))
        print("inv cam mat")
        print(K_inv)
        print("inv trans,")
        print(inv_trans)

    depth_img = np.zeros((HEIGHT, WIDTH))


    for row in range(HEIGHT):
        for col in range(WIDTH):
            if proj_x_img[row, col] == 0:
                continue
            proj_x_val = proj_x_img[row, col]
            px = np.array([col, row, 1.0])

            s_cam = K_inv@px
            s_cam1 = np.append(s_cam, [1])
            s_cam2 = s_cam1 * 2
            s_cam2[3] = 1
            p1 = np.matmul(inv_trans, s_cam1)
            p2 = np.matmul(inv_trans, s_cam2)
            #cam_line = p2 - p1
            cam_line = np.array([p1[2] - p2[2], p2[0] - p1[0], p1[0]*p2[2] - p2[0]*p1[2]])

            px_pro = np.array([proj_x_val, 0, 1])
            s_pro = K_inv@px_pro
            s_pro = np.append(s_pro, [1])
            p1_pro = s_pro
            p2_pro = np.array([0,0,0,1])

            proj_line = np.array([p1_pro[2] - p2_pro[2], p2_pro[0] - p1_pro[0], 0])
            proj_line = proj_line[0:3]
            intersect = np.cross(cam_line, proj_line)
            intersect = intersect/intersect[2]
            depth_img[row,col] = -intersect[1]

            if row%(HEIGHT/10) == 0:
                print(row)
    
    cv2.imwrite("depth_img_raw.png", depth_img)
    np.save("depth_img_np", depth_img)

    depth_img = depth_img/3*255.0
    depth_img[depth_img>255.0] = 255
    depth_img[depth_img<1.0] = 0
    cv2.imwrite("depth_img.png", depth_img)
    show_image(depth_img)










            







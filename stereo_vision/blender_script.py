import bpy
from math import *
import numpy as np

CAM1_LOC = (-1, -4, 0)
CAM1_ROT = (pi/2, 0, -pi/16)
CAM2_LOC = (1, -4, 0)
CAM2_ROT = (pi/2, 0, pi/16)
FOCAL_LEN = 50 # mm
PIXELS_X = 160
PIXELS_Y = 128
PW = 10*10**(-6)
print("Cam1 location:", "x: ", CAM1_LOC[0], " y:", CAM1_LOC[1], " z:", CAM1_LOC[2])
print("Cam1 rotation:", "x: ", CAM1_ROT[0], " y:", CAM1_ROT[1], " z:", CAM1_ROT[2])
print("Cam2 location:", "x: ", CAM2_LOC[0], " y:", CAM2_LOC[1], " z:", CAM2_LOC[2])
print("Cam2 rotation:", "x: ", CAM2_ROT[0], " y:", CAM2_ROT[1], " z:", CAM2_ROT[2])
print("Focal length: ", FOCAL_LEN, " mm")
print("Pixels of rendered picture x (width): ", PIXELS_X)
print("Pixels of rendered picture y (height): ", PIXELS_Y)
print("Width of pixel in mm: ", PW)

K = np.array([[FOCAL_LEN*10**(-3)/PW, 0, PIXELS_X/2], [0, FOCAL_LEN*10**(-3)/PW, PIXELS_Y/2],[0,0,1]])
K_inv = 1/(FOCAL_LEN*10**(-3))*np.array([[PW, 0, -PW*PIXELS_X/2],[0, PW, -PW*PIXELS_Y/2],[0,0,FOCAL_LEN*10**(-3)]])

# Calculates Rotation Matrix given euler angles.
def eulerAnglesToRotationMatrix(theta) :
    
    R_x = np.array([[1,         0,                  0                   ],
                    [0,         cos(theta[0]), -sin(theta[0]) ],
                    [0,         sin(theta[0]), cos(theta[0])  ]
                    ])
        
        
                    
    R_y = np.array([[cos(theta[1]),    0,      sin(theta[1])  ],
                    [0,                     1,      0                   ],
                    [-sin(theta[1]),   0,      cos(theta[1])  ]
                    ])
                
    R_z = np.array([[cos(theta[2]),    -sin(theta[2]),    0],
                    [sin(theta[2]),    cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])
                    
                    
    R = np.dot(R_z, np.dot( R_y, R_x ))

    return R

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
    return np.array([[0,      -omg[2],  omg[1]],
                     [omg[2],       0, -omg[0]],
                     [-omg[1], omg[0],       0]])


if __name__ == '__main__':
    
    R_CW_C = eulerAnglesToRotationMatrix((pi, 0, 0))


    R_0_CW1=eulerAnglesToRotationMatrix(CAM1_ROT)
    R_0_C1 = np.matmul(R_0_CW1, R_CW_C)
    
    R_0_CW2 = eulerAnglesToRotationMatrix(CAM2_ROT)
    R_0_C2 = np.matmul(R_0_CW2,R_CW_C)
    
    # Rotation matrix from camera 1 to camera 2
    R_C1_C2 = np.matmul(np.transpose(R_0_C1),R_0_C2)
    # Rotation matrix from camera2 to camera 1
    R_C2_C1 = np.transpose(R_C1_C2)
    # translation vector from cam2 to cam1
    t_C2_C1_0 = np.array([CAM1_LOC[0] - CAM2_LOC[0], CAM1_LOC[1]-CAM2_LOC[1], CAM1_LOC[2]-CAM2_LOC[2]])
    # translation vector from cam2 to cam1 in cam2 frame
    t_C2_C1_C2 = np.matmul(t_C2_C1_0, R_0_C2);
    print("Pos vec cam2 to cam1 in cam2 frame")
    print(t_C2_C1_C2)
    
    # Essential matrix
    E = np.matmul(VecToso3(t_C2_C1_C2), R_C2_C1)
    print("Essential matrix")
    print(E)
    
    # Camera matrix
    print("Camera matrix")
    print(K)
    print("Inverse camera matrix")
    print(K_inv)


    

    bpy.context.scene.render.resolution_x = PIXELS_X
    bpy.context.scene.render.resolution_y = PIXELS_Y


    for o in bpy.context.scene.objects:
        if o.type == 'CAMERA':
            o.select_set(True)
        else:
            o.select_set(False)

    # Call the operator only once
    bpy.ops.object.delete()

    scn = bpy.context.scene
    ## SPAWN STEREO CAMERA

    # create the first camera
    cam1 = bpy.data.cameras.new("Cam 1")
    cam1.lens = FOCAL_LEN

    # create the first camera object
    cam_obj1 = bpy.data.objects.new("Cam 1", cam1)
    cam_obj1.location = CAM1_LOC
    cam_obj1.rotation_euler = CAM1_ROT
    scn.collection.objects.link(cam_obj1)

    # create the second camera
    cam2 = bpy.data.cameras.new("Cam 2")
    cam2.lens = FOCAL_LEN

    # create the second camera object
    cam_obj2 = bpy.data.objects.new("Cam 2", cam2)
    cam_obj2.location = CAM2_LOC
    cam_obj2.rotation_euler = CAM2_ROT
    scn.collection.objects.link(cam_obj2)


    bpy.context.scene.render.engine = 'CYCLES'


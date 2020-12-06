import numpy as np
import cv2 
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

SHOW_IMAGES = True
FILENAME_PIC1 = "monkey_cam1left_160x128.png" 
FILENAME_PIC2 = "monkey_cam2right_160x128.png" 

FOCAL_LEN = 50*10**(-3) #m
print("focal len")
print(FOCAL_LEN)
PW = 10*10**(-6)
print("pixel width")
print(PW)
IMG_WIDTH = 160
IMG_HEIGHT = 128
U = IMG_WIDTH/2
V = IMG_HEIGHT/2

def isBlackPixel(pixel):
    if pixel[0] < 20 and pixel[1] < 20 and pixel[2] < 20:
        return True

essential = np.array([ [-6.16297582e-33, -3.90180644e-01, -7.16750215e-17],
                        [-3.90180644e-01, -6.47112461e-32,  1.96157056e+00],
                        [-7.16750215e-17, -1.96157056e+00,  5.85482703e-32]])

print("Essemtial")
print(essential)
cam_mat = np.array([   [FOCAL_LEN/PW,    0.,  U],
                        [   0., FOCAL_LEN/PW,  V],
                        [   0.,    0.,    1.]])

inv_cam_mat = 1/FOCAL_LEN*np.array([[PW, 0, -PW*U],
                                    [0, PW, -PW*V],
                                    [0, 0, FOCAL_LEN]])
print("inv camera matrix")
print(inv_cam_mat)

print("Camera matrix")
print(cam_mat)

img1 = cv2.imread(FILENAME_PIC1)
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
img2 = cv2.imread(FILENAME_PIC2)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)


if SHOW_IMAGES:
    f, axarr = plt.subplots(2)
    axarr[0].imshow(img1)
    axarr[1].imshow(img2)
    plt.show()


print(isBlackPixel(img1[0][0]))

min_norm_pix = inv_cam_mat @np.array([0,0,1])
print("min normalized image coordinate")
print(min_norm_pix)
max_norm_pix = inv_cam_mat @ np.array([IMG_WIDTH,IMG_HEIGHT,1])
print("max normalized image coordinate")
print(max_norm_pix)

ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

i = 0
for r in range(IMG_HEIGHT):
    for c in range(IMG_WIDTH):
        if not isBlackPixel(img1[r][c]):
            norm_coord = inv_cam_mat @np.array([c, r, 1])
            plt.scatter(norm_coord[0], norm_coord[1])
            epi_line = essential @norm_coord

            

plt.show()
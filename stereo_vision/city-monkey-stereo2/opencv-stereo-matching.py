import cv2
import matplotlib.pyplot as plt
import numpy as np



RIGHT_IMG_PATH = "stereo-images/rightCam.png"
LEFT_IMG_PATH = "stereo-images/leftCam.png"


img_right = cv2.imread(RIGHT_IMG_PATH)
img_left = cv2.imread(LEFT_IMG_PATH)

print("img right shape")
print(img_right.shape)

K = np.genfromtxt("camera-matrix.csv", delimiter=",")
print("K")
print(K)
R_C2_C1 = np.genfromtxt("R-C2-C1.csv", delimiter=",")
R_C1_C2 = R_C2_C1.transpose()
t_C2_C1_C2 = np.genfromtxt("t-C2-C1-C2.csv", delimiter=",")
t_C1_C2_C2 = -t_C2_C1_C2
t_C1_C2_C1 = R_C1_C2@t_C1_C2_C2

print(t_C2_C1_C2)
print("R_C1_C2")
print(R_C1_C2)
dist_coefsR = np.array([0, 0, 0, 0, 0.])

t_C1_C2_C1 = np.array([0.1997, 0, 0.01])


print(K)
R1, R2, P1, P2, Q, _,_= cv2.stereoRectify(K,dist_coefsR, K, dist_coefsR, (1920,1080), R_C1_C2, t_C1_C2_C1, alpha=0)
print(R1)

print("img left shape :2")
print(img_left.shape[:2])



mapx1, mapy1 = cv2.initUndistortRectifyMap(K, dist_coefsR, R1, K,
                                            (1920, 1080),
                                            cv2.CV_32F)
print(K)
mapx2, mapy2 = cv2.initUndistortRectifyMap(K, dist_coefsR, R2, K,
                                            (1920, 1080),
                                            cv2.CV_32F)
print("new cam mat")
print(K)

img_rect1 = cv2.remap(img_left, mapx1, mapy1, cv2.INTER_LINEAR)
img_rect2 = cv2.remap(img_right, mapx2, mapy2, cv2.INTER_LINEAR)
print("img rect shape")
print(img_rect1.shape)
plt.imshow(img_rect1)
plt.show()
plt.imshow(img_rect2)
plt.show()

# draw the images side by side
total_size = (max(img_rect1.shape[0], img_rect2.shape[0]),
                img_rect1.shape[1] + img_rect2.shape[1], 3)
img = np.zeros(total_size, dtype=np.uint8)
img[:img_rect1.shape[0], :img_rect1.shape[1]] = img_rect1
img[:img_rect2.shape[0], img_rect1.shape[1]:] = img_rect2

# draw horizontal lines every 25 px accross the side by side image
for i in range(20, img.shape[0], 25):
    cv2.line(img, (0, i), (img.shape[1], i), (255, 0, 0))

#img = cv2.resize(img, (int(1920/2), int(1080/2)))
cv2.imwrite("images/rect.png", img)

#Set disparity parameters
#Note: disparity range is tuned according to specific parameters obtained through trial and error. 
win_size = 5
min_disp = 128 +32
max_disp = 256 +32#min_disp * 9
num_disp = max_disp - min_disp # Needs to be divisible by 16
#Create Block matching object. 
stereo = cv2.StereoSGBM_create(
 minDisparity= min_disp,
 numDisparities = num_disp,
 blockSize = 5,
 uniquenessRatio = 10,
 speckleWindowSize = 100,
 speckleRange = 32,
 disp12MaxDiff = 5,
 P1 = 8*3*win_size**2,
 P2 = 32*3*win_size**2,
 mode=cv2.STEREO_SGBM_MODE_HH)

disp = stereo.compute(img_rect1, img_rect2)

plt.imshow(disp)
plt.show()



output = cv2.reprojectImageTo3D(disp, Q)
#print(output.shape)
#print(output)

output = output.reshape(-1,3)
output[:,2] /= 6
#np.savetxt("output.txt", output, delimiter=";", fmt='% s')

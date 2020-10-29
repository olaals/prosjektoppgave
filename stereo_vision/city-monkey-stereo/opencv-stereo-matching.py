import cv2
import matplotlib.pyplot as plt

RIGHT_IMG_PATH = "stereo-images/rightCam.png"
LEFT_IMG_PATH = "stereo-images/leftCam.png"


img_right = cv2.imread(RIGHT_IMG_PATH, 0)
img_left = cv2.imread(LEFT_IMG_PATH, 0)

stereo = cv2.StereoBM_create(numDisparities=16*3, blockSize=15)

disparity = stereo.compute(img_left, img_right)
plt.imshow(disparity, 'gray')
plt.show()
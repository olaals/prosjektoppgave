import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_image(img):
    plt.imshow(img, cmap="gray")
    plt.show()


#proj_x_img = cv2.imread("depth_img_raw.png", cv2.IMREAD_GRAYSCALE)
#print(np.amax(proj_x_img))
#show_image(proj_x_img)
#proj_x_img[proj_x_img>3] = 0
#show_image(proj_x_img)

depth_img = np.load("depth_img_np.npy")
depth_img = depth_img/3*255.0
depth_img[depth_img>255.0] = 254.0
depth_img[depth_img<1] = 0
cv2.imwrite("depth_img.png", depth_img)
show_image(depth_img)
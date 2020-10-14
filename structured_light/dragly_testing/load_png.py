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

depth_img = cv2.imread("cpp/projector-x.png", cv2.IMREAD_GRAYSCALE)
print(np.amax(depth_img))
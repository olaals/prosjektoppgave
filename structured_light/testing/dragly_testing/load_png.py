import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys

def show_image(img):
    plt.imshow(img, cmap="gray")
    plt.show()

def get_argument(arg):
    args = sys.argv
    for i in range(len(args)):
        if args[i] == arg:
            return args[i+1]
    print("Could not find argument for ", arg)
    return None


#proj_x_img = cv2.imread("depth_img_raw.png", cv2.IMREAD_GRAYSCALE)
#print(np.amax(proj_x_img))
#show_image(proj_x_img)
#proj_x_img[proj_x_img>3] = 0
#show_image(proj_x_img)

image_file = get_argument("--input")
if image_file is None:
    image_file = "sl-projects/monkey/no-reflection/projector-x.png"

depth_img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
show_image(depth_img)

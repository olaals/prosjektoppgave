import cv2
import matplotlib.pyplot as plt
import os
import numpy as np

img_folder = "images"


def load_images_from_folder(folder):
    images = []
    img_folder_list = os.listdir(folder)
    img_folder_list.sort()
    print(img_folder_list)
    for filename in img_folder_list:
        img = cv2.imread(os.path.join(folder, filename))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if img is not None:
            images.append(img)
    return images


def show_image(img):
    plt.imshow(img, cmap="gray")
    plt.show()


print(os.listdir(img_folder))

img_list = load_images_from_folder(img_folder)
avg_img = np.ndarray((1080, 1920))
N = 0

for img in img_list:
    print("hei")
    N += 1
    avg_img += img

avg_img /= N
avg_img = np.around(avg_img)


show_image(avg_img)

for img in img_list:
    bin_img = (img > avg_img)*255
    show_image(bin_img)
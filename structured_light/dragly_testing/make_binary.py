import cv2
import matplotlib.pyplot as plt
import os
import numpy as np

img_folder = "images"
output_dir = "bin_images"
show_images = False

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
    if show_images:
        plt.imshow(img, cmap="gray")
        plt.show()


print(os.listdir(img_folder))

img_list = load_images_from_folder(img_folder)
avg_img = np.zeros((1080, 1920))
N = 0

for img in img_list:
    N += 1
    avg_img += img

avg_img /= N
avg_img = np.around(avg_img)


x_value_image = np.zeros((1080, 1920))
print("x val image")
print(x_value_image)
xxx =  np.ndarray((1080, 1920))
img_list.reverse()
x_factor = 1

for img in img_list:
    bin_img = (img > avg_img)*1.0
    show_image(bin_img)
    x_value_image += bin_img * x_factor
    x_factor *= 2
    show_image(x_value_image)

cv2.imwrite(os.path.join(output_dir, "x_val_img.png"), x_value_image)


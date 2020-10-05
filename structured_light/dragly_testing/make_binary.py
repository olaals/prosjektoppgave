import cv2
import matplotlib.pyplot as plt
import os
import numpy as np


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

def show_image_list(img_list):
    for img in img_list:
        show_image(img)

def get_average_img(img_list, shape):
    avg_img = np.zeros(shape)
    N = 0
    for img in img_list:
        N += 1
        avg_img += img

    avg_img /= N
    avg_img = np.around(avg_img)
    return avg_img

def make_binary_images(img_list, avg_img):
    bin_img_list = []
    for img in img_list:
        bin_img = (img > avg_img)*1.0
        bin_img_list.append(bin_img)
    return bin_img_list

def binary_images_to_projector_x_val_img(bin_img_list, shape):
    x_value_image = np.zeros(shape)
    bin_img_list.reverse()
    x_factor = 1
    for bin_img in bin_img_list:
        x_value_image += bin_img * x_factor
        x_factor *= 2
    return x_value_image

def save_image(img, folder, filename, filetype):
    cv2.imwrite(os.path.join(folder, filename) + filetype, img)

def save_image_list(img_list, folder, filename, filetype):
    subscript = 0
    for img in img_list:
        img *= 255
        save_path = os.path.join(folder, filename) + "_" + str(subscript) + filetype
        print("savepathkjo")
        print(save_path)
        cv2.imwrite(save_path, img)
        subscript += 1



if __name__ == '__main__':

    STRUCTURED_LIGHT_INPUT_DIR = "images"
    X_VAL_IMG_DIR = "projector_x_images"
    X_VAL_PNG = "x_val_img"
    BINARY_IMG_DIR = "bin_images"
    BINARY_IMG_PNG = "binary_image" 
    FILETYPE_PNG = ".png"
    HEIGHT, WIDTH = 1080, 1920
    SHOW_IMAGES = False
    SAVE_IMAGES = True

    img_list = load_images_from_folder(STRUCTURED_LIGHT_INPUT_DIR)
    avg_img = get_average_img(img_list, (HEIGHT, WIDTH))
    bin_img_list = make_binary_images(img_list, avg_img)
    x_val_img = binary_images_to_projector_x_val_img(bin_img_list, (HEIGHT, WIDTH))

    if SHOW_IMAGES:
        show_image_list(bin_img_list)
        show_image(x_val_img)

    if SAVE_IMAGES:
        save_image(x_val_img, X_VAL_IMG_DIR, X_VAL_PNG, FILETYPE_PNG)
        save_image_list(bin_img_list, BINARY_IMG_DIR, BINARY_IMG_PNG, FILETYPE_PNG )
        








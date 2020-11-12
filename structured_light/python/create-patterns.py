from pylab import zeros, ones, indices, uint8
from PIL import Image
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import cv2


def show_image(img):
    plt.imshow(img, cmap="gray")
    plt.show()


def get_argument_or_default(arg, default):
    args = sys.argv
    for i in range(len(args)):
        if args[i] == arg:
            return args[i+1]
    print("Could not find argument for ", arg)
    return default


"""
rows = 1024
patterns = 7
data = zeros((patterns, rows, rows))
for i in range(patterns):
    divisions = 2 ** (i + 1)
    step = rows / divisions
    period = 2 * step
    data[i] = ones((rows, rows)) * ((indices((rows, rows))[1] % period) > step)
    print(indices((rows, rows)).shape)
    img = Image.fromarray(255 * data[i].astype(uint8), mode='L')
    #img.save("patterns/pattern_{}.png".format(i + 1))

"""


def create_pattern_img(patterns, rows, cols):
    img = np.zeros((rows, cols))
    divisions = 2 ** (patterns+1)
    step = cols / divisions
    period = 2 * step
    img = ones((rows, cols)) * \
        ((indices((rows, cols))[1] % period) > step) * 255
    #img[:,:] = (np.array(list(range(ROWS))).astype(np.uint8)%period > step)*255
    return img


def create_inverse_pattern_img(patterns, rows):
    img = np.zeros((rows, rows))
    divisions = 2 ** (patterns+1)
    step = rows / divisions
    period = 2 * step
    img = ones((rows, rows)) * \
        ((indices((rows, rows))[1] % period) < step) * 255
    return img


if __name__ == '__main__':
    ROWS = 1024
    COLS = 1920
    PATTERNS = 8
    SAVE_FOLDER = os.path.join(
        os.getcwd(), get_argument_or_default("--output", "../patterns/patterns-8"))
    PATTERN_FILE_NAME = "pattern"
    EXTENSION = ".png"

    ind = 0
    for i in range(PATTERNS):
        pattern_img = create_pattern_img(i, ROWS, COLS)
        filepath = os.path.join(
            SAVE_FOLDER, PATTERN_FILE_NAME + "-" + str(ind) + EXTENSION)
        cv2.imwrite(filepath, pattern_img)
        ind += 1

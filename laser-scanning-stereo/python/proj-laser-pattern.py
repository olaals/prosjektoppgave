import cv2
import numpy as np


if __name__ == "__main__":
    WIDTH = 1920
    HEIGHT = 1080
    WIDTH_LINE = 6

    img = np.zeros((HEIGHT, WIDTH, 3))
    img[:, int(WIDTH/2-WIDTH_LINE/2):int(WIDTH/2+WIDTH_LINE/2), 2] = 255

    cv2.imwrite("../patterns/red.png", img)


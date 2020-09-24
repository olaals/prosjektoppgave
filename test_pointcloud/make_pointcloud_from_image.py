
import cv2

WRITE_TO_FILE = True

img = cv2.imread("monkey_1_cam1.png")

ofile = open("genxyz.txt", "w")

img_height, img_width, _ = img.shape
print(img_height)
w = 0
h = 0
z = 0
scale = 100

if WRITE_TO_FILE:
    for y in img:
        h = h+1
        for x in y:
            w = w + 1
            if(w == img_width):
                w = 0
            ofile.write(str(w/scale) + " " + str(h/scale) + " " + str(z) + " ")
            ofile.write(str(x[0]) +" "+ str(x[1]) +" " + str(x[2]) + "\n")
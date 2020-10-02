import os, numpy, PIL
from PIL import Image
import cv2

img_folder = "images"

def load_images_from_folder(folder):
    images = []
    img_folder_list = os.listdir(folder)
    print(img_folder_list)
    return [os.path.join(folder,filename) for filename in img_folder_list]
    for filename in img_folder_list: 
        return os.path.join(folder,filename)
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images
# Access all PNG files in directory

imlist = load_images_from_folder(img_folder)
print(imlist)

# Assuming all images are the same size, get dimensions of first image
w,h=Image.open(imlist[0]).size
N=len(imlist)

# Create a numpy array of floats to store the average (assume RGB images)
arr=numpy.zeros((h,w,4),numpy.float)

# Build up average pixel intensities, casting each image as an array of floats
for im in imlist:
    imarr=numpy.array(Image.open(im),dtype=numpy.float)
    arr=arr+imarr/N

# Round values in array and cast as 8-bit integer
arr=numpy.array(numpy.round(arr),dtype=numpy.uint8)

# Generate, save and preview final image
out=Image.fromarray(arr,mode="RGB")
out.save("Average.png")
out.show()
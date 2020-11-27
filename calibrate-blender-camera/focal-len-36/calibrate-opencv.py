import numpy as np
import cv2 as cv
import glob
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((9*6,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('images/*.png')
print(images)
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (9,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (9,6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(10)
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("distortion coefficients")
print(dist)
print("cam mat")
print(mtx)

img = cv.imread(images[0])
h,  w = img.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
print(newcameramtx)
print(np.linalg.inv(newcameramtx))
inv_cam_mat = np.linalg.inv(newcameramtx)
inv_cam_mat_4x4 = np.eye(4)
inv_cam_mat_4x4[0:3,0:3] = inv_cam_mat
print(inv_cam_mat_4x4)
cam_mat_4x4 = np.eye(4)
cam_mat_4x4[0:3,0:3] = newcameramtx


np.savetxt("camera-matrix.csv", newcameramtx, delimiter=",")
np.savetxt("inv-camera-matrix.csv", inv_cam_mat, delimiter=",")
np.savetxt("camera-matrix-4x4.csv", cam_mat_4x4, delimiter=",")
np.savetxt("inv-camera-matrix-4x4.csv", inv_cam_mat_4x4, delimiter=",")

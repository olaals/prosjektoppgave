
disp("hei")
close all
clc
clear

focalLen = 36 * 1e-3; % m
sx = 10e-6;
imageSize = [1920, 1080];
principalPoint = [1920/2, 1080/2];

intrinsics = cameraIntrinsics([focalLen/sx, focalLen/sx], principalPoint, imageSize);
IntrinsicMatrix = intrinsics.IntrinsicMatrix

cameraParms = cameraParameters('IntrinsicMatrix', IntrinsicMatrix, 'ImageSize', [1080, 1920])


stereoParams = stereoParameters(cameraParms, cameraParms, roty(-6), [0.199725911, 0,0.01046719])


img_left = imread('stereo-images/leftCam.png');
img_right = imread('stereo-images/rightCam.png');

[imgLeftRect, imgRightRect] = rectifyStereoImages(img_left, img_right, stereoParams);
figure
imshow(imgLeftRect)
figure
imshow(imgRightRect)
A = stereoAnaglyph(imgLeftRect,imgRightRect);
figure
imtool(A)
title('Red-Cyan composite view of the rectified stereo pair image')

%figure
%imshow(imgLeftRect)
%figure
%imshow(imgRightRect)
imwrite(imgLeftRect, 'img-left-rect.png')
imwrite(imgRightRect, 'img-right-rect.png')

imgLeftRectGray = rgb2gray(imgLeftRect);
imgRightRectGray = rgb2gray(imgRightRect);
%imshow(imgLeftRectGray)

disparityRange = [256-64, 256+64];
disparityMap = disparitySGM(imgLeftRectGray, imgRightRectGray, 'DisparityRange', disparityRange);
%imshow(disparityMap, [0, 64]);
%title('Disparity Map');
%colormap jet
%colorbar



points3D = reconstructScene(disparityMap, stereoParams);

% Convert to meters and create a pointCloud object
points3D = points3D;
ptCloud = pointCloud(points3D, 'Color', imgLeftRect);
disp(size(points3D))
disp(max(points3D, [], 2));
sizePt = size(points3D);
points3D2 = reshape(points3D, [], 3);
colors3D = ptCloud.Color;
disp("size color 3d")
disp(size(colors3D));
colors3D = reshape(colors3D, [], 3);
disp("pt2")
maxVals = max(points3D2);
minVals = min(points3D2);
%points3D2 = rmmissing(points3D2);
colors3D = single(colors3D);

disp("sizes")
disp(size(points3D2))
disp(size(colors3D))

rgbxyz = [points3D2 colors3D];
disp("size rgbxyz")
disp(size(rgbxyz))
rgbxyz = rmmissing(rgbxyz);

writematrix(rgbxyz, 'proj.txt', 'Delimiter', ';');

% Create a streaming point cloud viewer
 player3D = pcplayer([minVals(1), maxVals(1)], [minVals(2), maxVals(2)], [minVals(3), maxVals(3)], 'VerticalAxis', 'y', ...
    'VerticalAxisDir', 'down');

% Visualize the point cloud
view(player3D, ptCloud);
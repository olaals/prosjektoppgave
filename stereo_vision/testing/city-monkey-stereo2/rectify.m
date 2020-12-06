

%camMat = readmatrix("camera-matrix.csv")
essentialMat = readmatrix("essential-matrix.csv");
R_C2_C1 = readmatrix("R-C2-C1.csv");
t_C2_C1_C2 = readmatrix("t-C2-C1-C2");

normCoord = [1;1;1];

line = essentialMat*normCoord
line = line/line(2)



imgLeft = imread('stereo-images/leftCam.png');
imgRight = imread('stereo-images/rightCam.png');


%imshow(img_left)
imgLeftRedlines = drawRedLines(imgLeft);
imgRightRedlines = drawRedLines(imgRight);



function compareImages(img1, img2)
    compareImg = [img1, img2];
    figure
    imshow(compareImg)
end

function img = drawRedLines(img)
    dim = size(img);
    height = dim(1);
    width = dim(2);
    for i = height/10:height/10:height-height/10
        img(i-1:i+1,:,1) = ones(3,width,1)*255;
    end
end
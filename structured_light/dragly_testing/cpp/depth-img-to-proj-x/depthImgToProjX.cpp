#define GLM_ENABLE_EXPERIMENTAL 1
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <Halide.h>
#include <fstream>
#include <glm/ext.hpp>
#include <glm/glm.hpp>
#include <halide_image_io.h>
#include <stdio.h>
#include <iostream>
#include <ImfRgbaFile.h>
#include <ImfStringAttribute.h>
#include <ImfMatrixAttribute.h>
#include <ImfArray.h>
#include <algorithm>
#include <ImfNamespace.h>
#include <tuple>
#include <math.h>

namespace IMF = OPENEXR_IMF_NAMESPACE;

using namespace IMF;
using namespace IMATH_NAMESPACE;

using namespace Halide;
using namespace Halide::Tools;
using namespace Eigen;
using namespace std;

using Vector4h = Matrix<Halide::Expr, 4, 1>;
using Matrix4h = Matrix<Halide::Expr, 4, 4>;

Var x, y, c, i, ii, xo, yo, xi, yi, img;

ostream &operator<<(ostream &os, const Matrix4h &m)
{
    os << m(0, 0) << " " << m(0, 1) << " " << m(0, 2) << " " << m(0, 3) << "\n"
       << m(1, 0) << " " << m(1, 1) << " " << m(1, 2) << " " << m(1, 3) << "\n"
       << m(2, 0) << " " << m(2, 1) << " " << m(2, 2) << " " << m(2, 3) << "\n"
       << m(3, 0) << " " << m(3, 1) << " " << m(3, 2) << " " << m(3, 3) << endl;
    return os;
}

ostream &operator<<(ostream &os, const Vector4h &v)
{
    os << v(0) << "\n"
       << v(1) << "\n"
       << v(2) << "\n"
       << v(3) << endl;
    return os;
}

Matrix4h getCameraMatrix(float focalLen, float pxDim, int width, int height)
{

    focalLen = focalLen * 10e-3;
    float u0 = width / 2.0;
    float v0 = height / 2.0;
    Matrix4h camMat;
    camMat << focalLen / pxDim, 0.0f, u0, 0.0f,
        0.0f, focalLen / pxDim, v0, 0.0f,
        0.0f, 0.0f, 1.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 1.0f;

    return camMat;
}

Matrix4h getInvCameraMat(float focalLen, float pxDim, int width, int height)
{
    focalLen = focalLen * 10e-3;
    float u0 = width / 2.0;
    float v0 = height / 2.0;
    Matrix4h camMat;
    float zero = 0.0;
    float one = 1.0;
    camMat << pxDim / focalLen, 0.0f, -pxDim * u0 / focalLen, 0.0f,
        0.0f, pxDim / focalLen, -pxDim * v0 / focalLen, 0.0f,
        0.0f, 0.0f, 1.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 1.0f;

    return camMat;
}

Matrix4h getTransMatProjToCam()
{
    Matrix4h transMat;
    transMat << 0.9945219f, 0.0f, -0.10452846f, -0.2f,
        0.0f, 1.0f, 0.0f, 0.0f,
        0.10452846f, 0.0f, 0.9945219f, 0.0f,
        0.0f, 0.0f, 0.0f, 1.0f;
    return transMat;
}

tuple<int, int> readOpenEXR(const char filename[], Array2D<Rgba> &pixels)
{
    RgbaInputFile file(filename);
    Box2i dw = file.dataWindow();

    int width = dw.max.x - dw.min.x + 1;
    int height = dw.max.y - dw.min.y + 1;
    tuple<int, int> dim(width, height);
    pixels.resizeErase(height, width);

    file.setFrameBuffer(&pixels[0][0] - dw.min.x - dw.min.y * width, 1, width);
    file.readPixels(dw.min.y, dw.max.y);
    return dim;
}

void exrArrayToHalideBuffer(Array2D<Rgba> &pixels, Buffer<float> &halideBuffer, int width, int height)
{
    for (int row{0}; row < height; row++)
    {
        for (int col{0}; col < width; col++)
        {
            isinf(pixels[row][col].r) ? pixels[row][col].r = 0.0f : pixels[row][col].r = pixels[row][col].r;
            halideBuffer(col, row) = pixels[row][col].r;
        }
    }
}

void saveImage(Expr result, size_t width, size_t height, const string &basename)
{
    Target target = get_host_target();
    Func byteResult;
    byteResult(x, y) = cast<uint8_t>(clamp(result, 0.0f, 1.0f) * 255.0f);
    byteResult.compile_jit(target);
    Buffer<uint8_t> output(width, height);
    byteResult.realize(output);
    stringstream filename;
    filename << basename << ".png";
    save_image(output, filename.str());
}

void saveImageEXR(Expr result, int width, int height, const char fileName[])
{
    Target target = get_host_target();
    Func byteResult;
    byteResult(x, y) = result;
    Buffer<float> output(width, height);
    byteResult.compile_jit(target);
    byteResult.realize(output);

    Array2D<Rgba> pixels;
    pixels.resizeErase(height, width);
    for (int row{0}; row < height; row++)
    {
        for (int col{0}; col < width; col++)
        {
            pixels[row][col].r = output(col, row);
            pixels[row][col].g = output(col, row);
            pixels[row][col].b = output(col, row);
        }
    }
    RgbaOutputFile file(fileName, width, height, WRITE_RGBA);
    file.setFrameBuffer(&pixels[0][0], 1, width);
    file.writePixels(height);
}

void debugImageEXR(Expr channel1Expr, Expr channel2Expr, Expr channel3Expr, int width, int height, const char fileName[])
{
    Target target = get_host_target();
    Func byteResult;
    byteResult(x, y, c) = 0.0f;
    byteResult(x, y, 0) = channel1Expr;
    byteResult(x, y, 1) = channel2Expr;
    byteResult(x, y, 2) = channel3Expr;
    Buffer<float> output(width, height, 3);
    byteResult.compile_jit(target);
    byteResult.realize(output);

    Array2D<Rgba> pixels;
    pixels.resizeErase(height, width);
    for (int row{0}; row < height; row++)
    {
        for (int col{0}; col < width; col++)
        {
            pixels[row][col].r = output(col, row, 0);
            pixels[row][col].g = output(col, row, 1);
            pixels[row][col].b = output(col, row, 2);
        }
    }
    RgbaOutputFile file(fileName, width, height, WRITE_RGBA);
    file.setFrameBuffer(&pixels[0][0], 1, width);
    file.writePixels(height);
}

int main(int argc, char **argv)
{
    const string INPUTFILE = "depth-image-gt.exr";
    const int FOCAL_LEN = 36.1;
    const float PX_DIM = 10 * 10e-6;

    Array2D<Rgba> pixels;
    int width, height;
    tie(width, height) = readOpenEXR(INPUTFILE.c_str(), pixels);
    Buffer<float> input(width, height);
    exrArrayToHalideBuffer(pixels, input, width, height);
    cout << input(0, 0) << endl;
    Expr zDepthCam = input(x, y);

    Matrix4h camMat = getCameraMatrix(FOCAL_LEN, PX_DIM, width, height);
    Matrix4h camMatInv = getInvCameraMat(FOCAL_LEN, PX_DIM, width, height);
    Matrix4h transfMatProjToCam = getTransMatProjToCam();
    cout << camMat << endl;
    Vector4h pxCam{x, y, 1.0f, 1.0f};
    Vector4h normCam = camMatInv * pxCam;
    debugImageEXR(normCam(0), normCam(1), normCam(2), width, height, "normCam.exr");
    cout << "normCam" << endl;
    cout << normCam << endl;
    Vector4h ptCam = normCam / normCam(2) * zDepthCam;
    debugImageEXR(ptCam(0), ptCam(1), ptCam(2), width, height, "ptCam.exr");
    cout << normCam << endl;
    Vector4h ptProj = transfMatProjToCam * ptCam;
    debugImageEXR(ptProj(0), ptProj(1), ptProj(2), width, height, "ptProj.exr");
    Vector4h normProj = camMat * ptProj;
    normProj = normProj / normProj(2);
    debugImageEXR(normProj(0), normProj(1), normProj(2), width, height, "normProj.exr");
    Expr xValProj = normProj(0);
    //saveImage(xValProj, width, height, "x-val-proj-gt");
    saveImageEXR(xValProj, width, height, "x-val-proj-gt.exr");

    return 0;
}

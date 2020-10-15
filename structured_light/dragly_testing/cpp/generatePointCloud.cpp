#define GLM_ENABLE_EXPERIMENTAL 1
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <Halide.h>
#include <fstream>
#include <glm/ext.hpp>
#include <glm/glm.hpp>
#include <halide_image_io.h>
#include <iostream>
#include <stdio.h>

using std::string;
using std::stringstream;
using std::vector;

using namespace std;
using namespace Halide;
using namespace Halide::Tools;
using namespace Eigen;

using Vector4h = Matrix<Halide::Expr, 4, 1>;
using Matrix4h = Matrix<Halide::Expr, 4, 4>;

Var x, y;

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

Matrix4h getInvCameraMat(float focalLen, float pxDim, int width, int height)
{

    focalLen = focalLen * 10e-3;
    float u0 = width / 2.0;
    float v0 = height / 2.0;
    Matrix4h camMat;
    float zero = 0.0;
    float one = 1.0;
    camMat << pxDim / focalLen, zero, -pxDim * u0 / focalLen, zero,
        zero, pxDim / focalLen, -pxDim * v0 / focalLen, zero,
        zero, zero, one, zero,
        zero, zero, zero, one;

    return camMat;
}

Matrix4h getTransformationMatrix()
{
    Matrix4h transMat;
    transMat << 0.9945219f, 0.0f, -0.10452846f, -0.2f,
        0.0f, 1.0f, 0.0f, 0.0f,
        0.10452846f, 0.0f, 0.9945219f, 0.0f,
        0.0f, 0.0f, 0.0f, 1.0f;
    return transMat;
}

Vector4h makeAxBzCLine(Vector4h a, Vector4h b)
{
    Vector4h result;
    result(0) = a(2) - b(2);
    result(1) = b(0) - a(0);
    result(2) = a(0) * b(2) - b(0) * a(2);
    result(3) = 1.0f;
    return result;
}

Vector4h cross3(Vector4h a, Vector4h b)
{
    Vector4h res;
    res(0) = a(1) * b(2) - a(2) * b(1);
    res(1) = a(2) * b(0) - a(0) * b(2);
    res(2) = a(0) * b(1) - a(1) * b(0);
    res(3) = 0;
    return res;
}

int main(int argc, char **argv)
{
    const float FOCAL_LEN = 36.1;
    const float PX_DIM = 10 * 10e-6;

    Halide::Buffer<uint8_t> input = load_image("projector-x.png");
    const int HEIGHT = input.height();
    const int WIDTH = input.width();

    Matrix4h InvK = getInvCameraMat(FOCAL_LEN, PX_DIM, WIDTH, HEIGHT);
    Matrix4h transMat = getTransformationMatrix();

    Vector4h px{x, y, 1.0f, 1.0f};

    Vector4h normCam1 = InvK * px;
    Vector4h normCam2 = 2 * normCam1;
    normCam2(3) = 1;

    Vector4h pointCam1 = transMat * normCam1;
    Vector4h pointCam2 = transMat * normCam2;

    Vector4h cameraLine = makeAxBzCLine(pointCam1, pointCam2);

    Vector4h pxProj{input(x, y) / 255.0f * 1920.0f, 0.0f, 1.0f, 1.0f};
    Vector4h normProj1 = InvK * pxProj;
    Vector4h normProj2{0.0f, 0.0f, 0.0f, 1.0f};

    Vector4h projectorLine = makeAxBzCLine(normProj1, normProj2);
    Vector4h intersection = cross3(cameraLine, projectorLine);
    intersection = intersection / intersection(2);
    intersection = intersection * (input(x, y) > 0);

    Expr depth = -intersection(1) / 4.0f * 255.0f;
    //cout << depth << endl;

    Func output;
    output(x, y) = Halide::cast<uint8_t>(depth);

    Buffer<uint8_t> result(input.width(), input.height());

    output.realize(result);
    save_image(result, "depth_img.png");

    return 0;
}

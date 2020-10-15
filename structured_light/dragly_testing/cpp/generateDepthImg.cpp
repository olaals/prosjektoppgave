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

Var x, y, c;

struct Point
{
    float x;
    float y;
    float z;
};

ostream &operator<<(ostream &os, const Matrix4h &m)
{
    os << m(0, 0) << " " << m(0, 1) << " " << m(0, 2) << " " << m(0, 3) << "\n"
       << m(1, 0) << " " << m(1, 1) << " " << m(1, 2) << " " << m(1, 3) << "\n"
       << m(2, 0) << " " << m(2, 1) << " " << m(2, 2) << " " << m(2, 3) << "\n"
       << m(3, 0) << " " << m(3, 1) << " " << m(3, 2) << " " << m(3, 3) << endl;
    return os;
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

Expr dot3(Vector4h a, Vector4h b)
{
    Expr res;
    res = a(0) * b(0) + a(1) * b(1) + a(2) * b(2);
    return res;
}

tuple<Vector4h, Vector4h> pluckerLine(Vector4h p1, Vector4h p2)
{
    Vector4h l;
    Vector4h l_dash;
    l = p1(3) * p2 - p2(3) * p1;
    l(3) = 0;
    l_dash = cross3(p1, p2);
    return {l, l_dash};
}

Vector4h pluckerPlane(Vector4h l, Vector4h l_dash, Vector4h pluckPt)
{
    Vector4h u;
    u = -pluckPt(3) * l_dash + cross3(pluckPt, l);
    u(3) = dot3(pluckPt, l_dash);
    return u;
}

Vector4h intersectionLinePlane(Vector4h l, Vector4h l_dash, Vector4h plPlane)
{
    Vector4h intersection;
    intersection = -plPlane(3) * l + cross3(plPlane, l_dash);
    intersection(3) = dot3(plPlane, l);
    return intersection;
}

int main(int argc, char **argv)
{
    const float FOCAL_LEN = 36.1;
    const float PX_DIM = 10 * 10e-6;
    const bool POINT_CLOUD_GLOBAL_FRAME = true;
    const bool POINT_CLOUD_PROJ_FRAME = true;

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

    const auto [camLine, camLineDash] = pluckerLine(pointCam1, pointCam2);
    //Vector4h cameraLine = makeAxBzCLine(pointCam1, pointCam2);

    Vector4h pxProj{input(x, y) / 255.0f * 1920.0f, 0.0f, 1.0f, 1.0f};
    Vector4h normProj1 = InvK * pxProj;
    Vector4h normProj2{0.0f, 0.0f, 0.0f, 1.0f};
    Vector4h normProj3{0.0f, 1.0f, 0.0f, 1.0f};

    const auto [projLine, projLineDash] = pluckerLine(normProj2, normProj3);
    Vector4h ProjPlane = pluckerPlane(projLine, projLineDash, normProj1);
    Vector4h intersection = intersectionLinePlane(camLine, camLineDash, ProjPlane);
    intersection = intersection / intersection(3);
    intersection *= (input(x, y) > 0);

    //Vector4h projectorLine = makeAxBzCLine(normProj1, normProj2);
    //Vector4h intersection = cross3(cameraLine, projectorLine);
    //intersection = intersection / intersection(2);
    //intersection = intersection * (input(x, y) > 0);

    //Expr depth = -intersection(1);
    //Expr depth = -intersection(1) / 4.0f * 255.0f;
    //cout << depth << endl;

    //Func output;
    //output(x, y) = Halide::cast<uint8_t>(depth);

    //Buffer<uint8_t> result(input.width(), input.height());

    //output.realize(result);
    //save_image(result, "depth_img.png");

    Expr depth = intersection(3);

    saveImage(depth, input.width(), input.height(), "depth_img.png");

    Func result;
    result(x, y, c) = 0.0f;
    result(x, y, 0) = intersection(0);
    result(x, y, 1) = intersection(1);
    result(x, y, 2) = intersection(2);

    Buffer<float> output(input.width(), input.height(), 3);
    result.realize(output);
    std::vector<Point> points;
    for (int j = 0; j < output.height(); j++)
    {
        for (int i = 0; i < output.width(); i++)
        {
            const auto x = output(i, j, 0);
            const auto y = output(i, j, 1);
            const auto z = output(i, j, 2);
            if (x == 0.0 && y == 0.0 && z == 0.0)
            {
                continue;
            }
            if (x < -10.0f || x > 10.0f || y < -10.0f || y > 10.0f || z < -10.0f || z > 10.0f)
            {
                continue;
            }
            points.push_back({x, y, z});
        }
    }
    std::ofstream outFile;
    outFile.open("out.xyz");
    outFile << points.size() << "\n";
    outFile << "comment"
            << "\n";
    for (const auto &point : points)
    {
        outFile << point.x << " " << point.y << " " << point.z << "\n";
    }

    return 0;
}

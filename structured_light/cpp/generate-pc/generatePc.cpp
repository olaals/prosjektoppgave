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
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

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
    uint16_t r;
    uint16_t g;
    uint16_t b;
};

Matrix4h read4x4MatFromCSV(string csvFile)
{
    Matrix4h transfMat;
    ifstream in(csvFile);
    vector<float> floatVec;
    if (in)
    {
        string line;
        while (getline(in, line))
        {
            stringstream sep(line);
            string field;
            while (getline(sep, field, ','))
            {
                float val = stod(field);
                floatVec.push_back(val);
            }
        }
    }
    transfMat << floatVec[0], floatVec[1], floatVec[2], floatVec[3],
        floatVec[4], floatVec[5], floatVec[6], floatVec[7],
        floatVec[8], floatVec[9], floatVec[10], floatVec[11],
        floatVec[12], floatVec[13], floatVec[14], floatVec[15];
    return transfMat;
}

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

Matrix4h getTransMatWorldToProj()
{
    Matrix4h transMat;
    transMat << -0.99862951f, 0.0f, 0.0523359f, 0.1f,
        0.00908804f, -0.1734101f, 0.9986295f, 3.0f,
        -0.052335f, -1.0f, 0.0f, 1.0f,
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

template <typename Function>
void writeBufferToXYZFile(Buffer<float> &buffer, Buffer<uint8_t> &color, string filename, string deliminator, Function condFunc)
{
    std::vector<Point> points;
    for (int j = 0; j < buffer.height(); j++)
    {
        for (int i = 0; i < buffer.width(); i++)
        {
            const auto x = buffer(i, j, 0);
            const auto y = buffer(i, j, 1);
            const auto z = buffer(i, j, 2);
            uint8_t r = color(i, j, 0);
            uint8_t g = color(i, j, 1);
            uint8_t b = color(i, j, 2);
            if (condFunc(x, y, z))
            {
                continue;
            }
            points.push_back({x, y, z, r, g, b});
        }
    }
    std::ofstream outFile;
    outFile.open(filename);
    outFile << points.size() << "\n";
    const auto d = deliminator;
    for (const auto &point : points)
    {
        outFile << point.x << d << point.y << d << point.z << d << point.r << d << point.g << d << point.b << "\n";
    }
}

bool conditionProjector(float x, float y, float z)
{
    return (x < -10.0f || x > 10.0f || y < -10.0f || y > 10.0f || z < -10.0f || z > 10.0f);
}

bool noCondition(float x, float y, float z)
{
    return false;
}

int main(int argc, char **argv)
{
    const float FOCAL_LEN = 36.1;
    const float PX_DIM = 10 * 10e-6;
    const bool POINT_CLOUD_GLOBAL_FRAME = true;
    const bool POINT_CLOUD_PROJ_FRAME = true;
    const string PROJECTOR_X_PNG = "images/x-val-img.png";
    const string TRANSF_MAT_WORLD_TO_PROJ_CSV = "matrices/transf-world-proj.csv";
    const string TRANSF_PROJ_CAM_CSV = "matrices/transf-proj-cam.csv";
    const string INV_CAM_MAT_CSV = "matrices/inv-cam-mat.csv";
    const string SAVE_DEPTH_IMAGE = "images/depth_img.png";
    const string SAVE_XYZ_PROJ = "pointclouds/proj.txt";
    const string SAVE_XYZ_WORLD = "pointclouds/world.txt";
    const string NO_PROJECTOR_PNG = "images/no-projector.png";

    Halide::Buffer<uint8_t> input = load_image(PROJECTOR_X_PNG);
    const int HEIGHT = input.height();
    const int WIDTH = input.width();

    Matrix4h InvK = read4x4MatFromCSV(INV_CAM_MAT_CSV);
    Matrix4h transMatProjToCam = read4x4MatFromCSV(TRANSF_PROJ_CAM_CSV);
    Matrix4h transMatWorldToProj = read4x4MatFromCSV(TRANSF_MAT_WORLD_TO_PROJ_CSV);
    Matrix4h essentialMat = read4x4MatFromCSV("matrices/essential-mat.csv");

    cout << essentialMat << endl;

    //cout << "Tranformation Matrix World to Projector" << endl;
    //cout << transMatWorldToProj << endl;

    //Vector4h px{x, y, 1.0f, 0.0f};

    //Vector4h normCam1 = InvK * px;
    //normCam1(3) = 1.0f;
    //Vector4h normCam2 = 2 * normCam1;
    //normCam2(3) = 1.0f;

    //Vector4h pointCam1 = transMatProjToCam * normCam1;
    //pointCam1 = pointCam1 / pointCam1(3);
    //Vector4h pointCam2 = transMatProjToCam * normCam2;
    //pointCam2 /= pointCam2(3);

    //const auto [camLine, camLineDash] = pluckerLine(pointCam1, pointCam2);
    ////Vector4h cameraLine = makeAxBzCLine(pointCam1, pointCam2);

    //Vector4h pxProj{input(x, y) / 255.0f * 1920.0f, 0.0f, 1.0f, 0.0f};
    //Vector4h normProj1 = InvK * pxProj;
    //normProj1 = normProj1 / normProj1(2);
    //normProj1(3) = 1.0f;
    //Vector4h normProj2{0.0f, 0.0f, 0.0f, 1.0f};
    //Vector4h normProj3{0.0f, 1.0f, 0.0f, 1.0f};

    //const auto [projLine, projLineDash] = pluckerLine(normProj2, normProj3);
    //Vector4h ProjPlane = pluckerPlane(projLine, projLineDash, normProj1);
    //Vector4h intersection = intersectionLinePlane(camLine, camLineDash, ProjPlane);
    //intersection = intersection / intersection(3);
    //intersection *= (input(x, y) > 0); // does this make sense?

    //Expr depth = intersection(3);

    //saveImage(depth, input.width(), input.height(), SAVE_DEPTH_IMAGE);

    //Halide::Buffer<uint8_t> color = load_image(NO_PROJECTOR_PNG);

    //if (POINT_CLOUD_PROJ_FRAME)
    //{
    //Func result;
    //result(x, y, c) = 0.0f;
    //result(x, y, 0) = intersection(0);
    //result(x, y, 1) = intersection(1);
    //result(x, y, 2) = intersection(2);

    //Buffer<float> output(input.width(), input.height(), 3);
    //result.realize(output);
    //writeBufferToXYZFile(output, color, SAVE_XYZ_PROJ, ";", conditionProjector);
    //}
    //if (POINT_CLOUD_GLOBAL_FRAME)
    //{

    //Vector4h ptGlobalFrame = transMatWorldToProj * intersection;
    //Func result_w;
    //result_w(x, y, c) = 0.0f;
    //result_w(x, y, 0) = ptGlobalFrame(0);
    //result_w(x, y, 1) = ptGlobalFrame(1);
    //result_w(x, y, 2) = ptGlobalFrame(2);

    //Buffer<float> output_w(input.width(), input.height(), 3);
    //result_w.realize(output_w);
    //writeBufferToXYZFile(output_w, color, SAVE_XYZ_WORLD, ";", conditionProjector);
    //}

    return 0;
}

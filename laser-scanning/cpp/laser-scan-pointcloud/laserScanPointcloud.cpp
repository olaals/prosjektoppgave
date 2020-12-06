#pragma once

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
#include <filesystem>
#include <ImfRgbaFile.h>
#include <ImfStringAttribute.h>
#include <ImfMatrixAttribute.h>
#include <ImfArray.h>
#include <algorithm>
#include <ImfNamespace.h>
#include <tuple>
#include <math.h>

#include "utilities.h"

namespace IMF = OPENEXR_IMF_NAMESPACE;

using namespace IMF;
using namespace IMATH_NAMESPACE;

using std::string;
using std::stringstream;
using std::vector;

using namespace std;
using namespace Halide;
using namespace Halide::Tools;
using namespace Eigen;
using std::filesystem::directory_iterator;

using Vector4h = Matrix<Halide::Expr, 4, 1>;
using Matrix4h = Matrix<Halide::Expr, 4, 4>;

Var x, y, c, i, pcx, pcy, xtf, ytf;

struct Point
{
    float x;
    float y;
    float z;
    uint16_t r;
    uint16_t g;
    uint16_t b;
};

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

Buffer<uint8_t> loadImages(vector<string> filenames)
{
    if (filenames.empty())
    {
        throw std::invalid_argument("List of filenames cannot be empty");
    }
    vector<Buffer<uint8_t>> images;
    Func assigner;
    assigner(x, y, c, i) = cast<uint8_t>(0);
    for (int i = 0; i < filenames.size(); i++)
    {
        const auto filename = filenames[i];
        images.push_back(load_image(filename));
        assigner(x, y, c, i) = images[i](x, y, c);
    }
    Buffer<uint8_t> input(images[0].width(), images[0].height(), images[0].channels(), images.size());
    assigner.realize(input);
    return input;
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

bool conditionProjector(float x, float y, float z)
{
    return (x < -10.0f || x > 10.0f || y < -10.0f || y > 10.0f || z < -10.0f || z > 10.0f);
}

bool noCondition(float x, float y, float z)
{
    return false;
}

void saveImages(Expr result, size_t width, size_t height, size_t imageCount, const string &basename)
{
    Target target = get_host_target();
    Func byteResult;
    byteResult(x, y, i) = cast<uint8_t>(clamp(result, 0.0f, 1.0f) * 255.0f);
    byteResult.compile_jit(target);
    Buffer<uint8_t> output(width, height, imageCount);
    byteResult.realize(output);
    for (int i = 0; i < imageCount; i++)
    {
        stringstream filename;
        filename << basename << i << ".png";
        const Buffer<uint8_t> image = output.sliced(2, i);
        save_image(image, filename.str());
    }
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

void debugImageEXR(Expr channel1Expr, Expr channel2Expr, Expr channel3Expr, int width, int height, const char fileName[])
{
    channel1Expr = cast<float>(channel1Expr);
    channel2Expr = cast<float>(channel2Expr);
    channel3Expr = cast<float>(channel3Expr);
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
    const int NUM_IMAGES = 120;
    std::vector<std::string> filenames;
    for (const auto &file : directory_iterator("images/scan-images"))
    {
        filenames.push_back(file.path());
    }
    sort(filenames.begin(), filenames.end());

    Buffer<uint8_t> input = loadImages(filenames);

    vector<string> tfsFilenames;

    for (const auto &csv : directory_iterator("matrices/tf-world-cam"))
    {
        tfsFilenames.push_back(csv.path());
    }
    sort(tfsFilenames.begin(), tfsFilenames.end());
    vector<Matrix4h> tfs;
    for (string &filename : tfsFilenames)
    {
        cout << filename << endl;
        Matrix4h tf = read4x4MatFromCSV(filename);
        tfs.push_back(tf);
    }
    cout << "tfs 0 " << endl;
    cout << tfs[0] << endl;

    Expr redFilter = input(x, y, 0, i) > 150;

    Matrix4h E = read4x4MatFromCSV("matrices/essential-matrix.csv");
    Matrix4h K = read4x4MatFromCSV("matrices/cam-mat.csv");
    Matrix4h invK = read4x4MatFromCSV("matrices/inv-cam-mat.csv");
    Matrix4h T_CP = read4x4MatFromCSV("matrices/T-C1-C2.csv");
    Matrix4h T_WC = read4x4MatFromCSV("matrices/T-W-C1.csv");
    Vector4h t_CP{0, 0, 0, 0};
    t_CP(0) = T_CP(0, 3);
    t_CP(1) = T_CP(1, 3);
    t_CP(2) = T_CP(2, 3);
    t_CP(3) = T_CP(3, 3);
    cout << t_CP << endl;

    Vector4h scanNormal_P{1.0f, 0.0f, 0.0f, 1.0f};
    Vector4h scanPlane_C = T_CP * scanNormal_P;
    scanPlane_C(3) = -dot3(scanPlane_C, t_CP);

    Vector4h px{x, y, 1.0f, 0.0f};
    Vector4h normCoord_C = invK * px;
    Vector4h lineDash{0.0f, 0.0f, 0.0f, 0.0f};
    Vector4h intersect = intersectionLinePlane(normCoord_C, lineDash, scanPlane_C);
    intersect = intersect * redFilter;
    intersect = intersect / intersect[3];
    intersect = T_WC * intersect;
    intersect = intersect / intersect[3];
    //saveImage(intersect[2], 1920, 1080, "images/debug/depth.png");

    Func result;
    result(x, y, c, i) = 0.0f;
    result(x, y, 0, i) = intersect[0];
    result(x, y, 1, i) = intersect[1];
    result(x, y, 2, i) = intersect[2];

    Buffer<float> output(1920, 1080, 3, NUM_IMAGES);
    result.realize(output);
    vector<Point> points;
    std::ofstream outFile;
    outFile.open("pointclouds/out.txt");

    for (int indImage = 0; indImage < NUM_IMAGES; indImage++)
    {
        cout << "processed image " << indImage << endl;
        for (int xxx = 0; xxx < output.width(); xxx++)
        {
            for (int yyy = 0; yyy < output.height(); yyy++)
            {

                float xPoint = output(xxx, yyy, 0, indImage) + indImage * 0.005f;
                float yPoint = output(xxx, yyy, 1, indImage);
                float zPoint = output(xxx, yyy, 2, indImage);

                if (abs(zPoint > 0.01))
                {
                    outFile << xPoint << ";" << yPoint << ";" << zPoint << "\n";
                }
                points.push_back({xPoint, yPoint, zPoint, 0, 0, 0});
            }
        }
    }
    outFile.close();

    //debugImageEXR(intersect[2], intersect[2], intersect[2], 1920, 1080, "images/debug/depth.exr");
}

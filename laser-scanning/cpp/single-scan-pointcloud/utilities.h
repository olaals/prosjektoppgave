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

Matrix4h read4x4MatFromCSV(string csvFile);
ostream &operator<<(ostream &os, const Matrix4h &m);
ostream &operator<<(ostream &os, const Vector4h &v);

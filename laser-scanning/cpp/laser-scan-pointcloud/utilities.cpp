#include "utilities.h"

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

ostream &operator<<(ostream &os, const Vector4h &v)
{
    os << v(0) << "\n"
       << v(1) << "\n"
       << v(2) << "\n"
       << v(3) << endl;
    return os;
}

cmake_minimum_required(VERSION 3.10)

project(DepthImageToProjectorX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ZLIB REQUIRED)
find_package(PNG REQUIRED)
find_package(JPEG REQUIRED)
find_package(Threads)
find_package(Eigen3 3.3 REQUIRED NO_MODULE)
find_package(OpenEXR)

add_executable(depthImgToProjX depthImgToProjX.cpp)

target_include_directories(
   depthImgToProjX
    PRIVATE
    /home/ola/library/Halide/include
    /home/ola/library/Halide/tools
    ${PNG_INCLUDE_DIR}
    ${JPEG_INCLUDE_DIR}
    ${EIGEN3_INCLUDE_DIR}
)

target_link_libraries(
   depthImgToProjX
    PRIVATE
    ${PNG_LIBRARY}
    ${JPEG_LIBRARY}
    ${CMAKE_THREAD_LIBS_INIT}
    dl
    -L/home/ola/library/Halide/bin/
    Halide
    Eigen3::Eigen
    OpenEXR::IlmImf
)

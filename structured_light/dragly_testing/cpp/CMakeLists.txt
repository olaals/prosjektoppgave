cmake_minimum_required(VERSION 3.12)

project(generateDepthImg)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(JPEG REQUIRED)
find_package(Threads)
find_package(Eigen3 3.3 REQUIRED NO_MODULE)
find_package(ZLIB REQUIRED)
find_package(PNG REQUIRED)

add_executable(generateDepthImg generateDepthImg.cpp)

target_include_directories(
   generateDepthImg
    PRIVATE
    /home/ola/library/Halide/include
    /home/ola/library/Halide/tools
    ${EIGEN3_INCLUDE_DIR}
    ${PNG_INCLUDE_DIR}
    ${JPEG_INCLUDE_DIR}
)

target_link_libraries(
   generateDepthImg
    PRIVATE
    ${CMAKE_THREAD_LIBS_INIT}
    ${PNG_LIBRARY}
    ${JPEG_LIBRARY}
    dl
    -L/home/ola/library/Halide/bin/
    -lHalide
    Eigen3::Eigen
)


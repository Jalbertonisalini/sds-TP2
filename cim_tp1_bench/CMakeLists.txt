cmake_minimum_required(VERSION 3.15)
project(cim_tp1_bench VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS False)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -O3")

include_directories(include)

add_executable(cim_bench
    src/main.cpp
    src/cell_index_method.cpp
)

cmake_minimum_required(VERSION 3.15)
project(SimulacionSistemas_TP2 VERSION 1.0 LANGUAGES CXX)

# Obligamos a usar C++17 como mínimo
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS False)

# Agregamos flags de compilación estrictos para asegurar buenas prácticas
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -O3")

include_directories(include)

add_executable(simulador
    src/main.cpp
    src/CellIndexMethod.cpp
    src/OutputWriter.cpp
    src/SimulationEngine.cpp
    # A medida que sumemos los .cpp, los agregamos acá
)
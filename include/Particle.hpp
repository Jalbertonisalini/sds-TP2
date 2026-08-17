#pragma once
#include "Vec2.hpp"

struct Particle {
    int id;
    Vec2 position;
    double angle; 
    double radius{0.0};
};
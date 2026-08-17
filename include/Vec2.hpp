#pragma once
#include <cmath>

struct Vec2 {
    double x{0.0};
    double y{0.0};

    constexpr Vec2() = default;
    constexpr Vec2(double x_val, double y_val) : x(x_val), y(y_val) {}

    [[nodiscard]] constexpr Vec2 operator+(const Vec2& other) const {
        return {x + other.x, y + other.y};
    }

    [[nodiscard]] constexpr Vec2 operator-(const Vec2& other) const {
        return {x - other.x, y - other.y};
    }

    [[nodiscard]] constexpr Vec2 operator*(double scalar) const {
        return {x * scalar, y * scalar};
    }

    constexpr Vec2& operator+=(const Vec2& other) {
        x += other.x;
        y += other.y;
        return *this;
    }

    [[nodiscard]] double norm() const {
        return std::sqrt(x * x + y * y);
    }

    [[nodiscard]] constexpr double norm_sq() const {
        return x * x + y * y;
    }
};
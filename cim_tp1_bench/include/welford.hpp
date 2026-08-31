#pragma once
#include <cmath>

// Puerto directo de SDS-TP1/source/java/Welford.java
// Media y desvío estándar muestral (ddof=1) en línea.
class Welford {
public:
    void add(double value) {
        n_++;
        double delta = value - mean_;
        mean_ += delta / n_;
        m2_ += delta * (value - mean_);
    }

    [[nodiscard]] double mean() const { return mean_; }

    [[nodiscard]] double std() const {
        if (n_ < 2) return 0.0;
        return std::sqrt(m2_ / (n_ - 1));
    }

private:
    int n_ = 0;
    double mean_ = 0.0;
    double m2_ = 0.0;
};

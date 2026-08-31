#include "cell_index_method.hpp"
#include <cmath>

namespace cim_tp1 {

double max_radius(const std::vector<Particle>& particles) {
    double max = 0;
    for (const auto& p : particles) {
        if (p.radius > max) max = p.radius;
    }
    return max;
}

int max_allowed_m(double L, double rc, double r_max) {
    double denom = rc + 2 * r_max;
    return static_cast<int>(std::floor(L / denom - 1e-9));
}

}  // namespace cim_tp1

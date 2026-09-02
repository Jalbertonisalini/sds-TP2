#include "cell_index_method_reusable.hpp"
#include <cmath>
#include <algorithm>

namespace {

void try_pair(const Particle& a, const Particle& b, double L, double rc, bool pbc,
              std::vector<std::vector<int>>& neighbors) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    if (pbc) {
        dx -= L * std::round(dx / L);
        dy -= L * std::round(dy / L);
    }
    double d = std::sqrt(dx * dx + dy * dy) - a.radius - b.radius;
    if (d <= rc) {
        neighbors[a.id].push_back(b.id);
        neighbors[b.id].push_back(a.id);
    }
}

}  // namespace

const std::vector<std::vector<int>>& CellIndexMethodReusable::run(const std::vector<Particle>& particles, double L,
                                                                    int M, double rc, bool pbc) {
    int N = static_cast<int>(particles.size());

    if (head_.size() != static_cast<size_t>(M) * M) head_.assign(static_cast<size_t>(M) * M, -1);
    else std::fill(head_.begin(), head_.end(), -1);
    if (next_.size() != static_cast<size_t>(N)) next_.resize(N);
    if (neighbors_.size() != static_cast<size_t>(N)) neighbors_.resize(N);
    for (auto& n : neighbors_) n.clear();

    double cell_size = L / M;
    for (const auto& p : particles) {
        int cx = std::min(M - 1, std::max(0, static_cast<int>(p.x / cell_size)));
        int cy = std::min(M - 1, std::max(0, static_cast<int>(p.y / cell_size)));
        int cell = cy * M + cx;
        next_[p.id] = head_[cell];
        head_[cell] = p.id;
    }

    const int dirs[4][2] = {{0, 1}, {1, 1}, {1, 0}, {1, -1}};

    for (int cy = 0; cy < M; ++cy) {
        for (int cx = 0; cx < M; ++cx) {
            int cell = cy * M + cx;

            // Pares dentro de la propia celda (cada par una sola vez).
            for (int a = head_[cell]; a != -1; a = next_[a]) {
                for (int b = next_[a]; b != -1; b = next_[b]) {
                    try_pair(particles[a], particles[b], L, rc, pbc, neighbors_);
                }
            }

            for (const auto& d : dirs) {
                int ny = cy + d[0];
                int nx = cx + d[1];
                if (pbc) {
                    ny = ((ny % M) + M) % M;
                    nx = ((nx % M) + M) % M;
                } else if (ny < 0 || ny >= M || nx < 0 || nx >= M) {
                    continue;
                }
                if (ny == cy && nx == cx) continue;  // celda vecina envuelta sobre sí misma (M chico + PBC)

                int ncell = ny * M + nx;
                for (int a = head_[cell]; a != -1; a = next_[a]) {
                    for (int b = head_[ncell]; b != -1; b = next_[b]) {
                        try_pair(particles[a], particles[b], L, rc, pbc, neighbors_);
                    }
                }
            }
        }
    }
    return neighbors_;
}

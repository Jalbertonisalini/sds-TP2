#include "CellIndexMethod.hpp"
#include <cmath>
#include <stdexcept>
#include <algorithm>

CellIndexMethod::CellIndexMethod(const SimulationConfig& config)
    : L(config.L), rc(config.rc), r_max(config.r_max), periodic(config.periodic) {
    
    // Condición estricta para el tamaño de celda: L/M >= rc + 2*r_max
    double min_cell_size = rc + 2.0 * r_max;
    
    if (min_cell_size > L) {
        M = 1; // Si el radio de interacción es muy grande, hay 1 sola celda
    } else {
        M = static_cast<int>(std::floor(L / min_cell_size));
    }
    
    if (M <= 0) {
        throw std::invalid_argument("Error: M calculo 0. Revisa rc y r_max.");
    }
    
    cell_size = L / M;
    head.resize(M * M, -1);
}

int CellIndexMethod::wrap(int index) const {
    if (index < 0) return index + M;
    if (index >= M) return index - M;
    return index;
}

int CellIndexMethod::get_cell_index(double x, double y) const {
    int col = static_cast<int>(x / cell_size);
    int row = static_cast<int>(y / cell_size);
    
    if (col >= M) col = M - 1;
    if (row >= M) row = M - 1;
    if (col < 0) col = 0;
    if (row < 0) row = 0;
    
    return row * M + col;
}

void CellIndexMethod::build(const std::vector<Particle>& particles) {
    std::fill(head.begin(), head.end(), -1);
    next.assign(particles.size(), -1); 

    for (size_t i = 0; i < particles.size(); ++i) {
        int cell = get_cell_index(particles[i].position.x, particles[i].position.y);
        next[i] = head[cell];
        head[cell] = static_cast<int>(i);
    }
}

std::vector<int> CellIndexMethod::get_neighbors(const std::vector<Particle>& particles, int particle_id) const {
    std::vector<int> neighbors;
    neighbors.reserve(16); 

    const auto& p1 = particles[particle_id];
    int center_cell = get_cell_index(p1.position.x, p1.position.y);
    int center_row = center_cell / M;
    int center_col = center_cell % M;

    // El threshold base para esta partícula específica
    double threshold_base = rc + p1.radius;

    for (int d_row = -1; d_row <= 1; ++d_row) {
        for (int d_col = -1; d_col <= 1; ++d_col) {
            
            int row = center_row + d_row;
            int col = center_col + d_col;

            // Manejo del flag de condiciones periódicas
            if (periodic) {
                row = wrap(row);
                col = wrap(col);
            } else {
                // Si no es periódico y nos salimos de la caja, ignoramos esta celda
                if (row < 0 || row >= M || col < 0 || col >= M) continue;
            }

            int cell = row * M + col;
            int current = head[cell];
            
            while (current != -1) {
                if (current != particle_id) { 
                    const auto& p2 = particles[current];
                    
                    double dx = p2.position.x - p1.position.x;
                    double dy = p2.position.y - p1.position.y;

                    if (periodic) {
                        if (dx > L / 2.0) dx -= L;
                        else if (dx < -L / 2.0) dx += L;
                        if (dy > L / 2.0) dy -= L;
                        else if (dy < -L / 2.0) dy += L;
                    }
                    
                    double threshold = threshold_base + p2.radius;

                    if (dx * dx + dy * dy <= threshold * threshold) {
                        neighbors.push_back(current);
                    }
                }
                current = next[current];
            }
        }
    }
    return neighbors;
}

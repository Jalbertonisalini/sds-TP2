#pragma once
#include <vector>
#include <cmath>
#include <algorithm>

// ÚNICA implementación del CIM usada por el punto g) (comparación de tiempos contra
// el TP1). Tanto el benchmark del TP1 (cim_bench) como el modo --cim-timing del
// simulador de TP2 llaman a ESTA MISMA función, de modo que ambas series miden un
// kernel byte-por-byte idéntico; lo único que difiere es la geometría de la caja
// (L y M) y el tipo de partícula (que se adapta con accessors inline).
//
// Algoritmo: grilla MxM con 4 direcciones vecinas + celda propia (simetría: cada par
// se evalúa una sola vez) sobre arrays planos head/next tipo lista enlazada, con
// contenedores REUTILIZADOS entre llamadas (resize si hace falta + clear; sin allocs
// dentro del pase). -----------------------------------------------------------------
// PBC con dx -= L*round(dx/L), y distancia por sqrt(dx^2+dy^2) - ra - rb <= rc.
//
// `Acc` debe exponer px(p), py(p), pradius(p), pid(p) (accessors inline, ver
// abajo: shared_particle_accessors). `neighbors` es el resultado global por partícula
// (válido hasta la próxima llamada).
template <typename ParticleList, typename Acc>
void shared_build_all_neighbors(const ParticleList& particles, double L, int M, double rc,
                                bool periodic, const Acc& acc,
                                std::vector<std::vector<int>>& neighbors) {
    int N = static_cast<int>(particles.size());

    std::vector<int> head(static_cast<size_t>(M) * M, -1);
    std::vector<int> next(N, -1);

    double cell_size = L / M;
    for (const auto& p : particles) {
        int cx = std::min(M - 1, std::max(0, static_cast<int>(acc.px(p) / cell_size)));
        int cy = std::min(M - 1, std::max(0, static_cast<int>(acc.py(p) / cell_size)));
        int cell = cy * M + cx;
        next[acc.pid(p)] = head[cell];
        head[cell] = acc.pid(p);
    }

    if (neighbors.size() != static_cast<size_t>(N)) neighbors.resize(N);
    for (auto& n : neighbors) n.clear();

    const int dirs[4][2] = {{0, 1}, {1, 1}, {1, 0}, {1, -1}};

    auto try_pair = [&](const auto& a, const auto& b) {
        double dx = acc.px(b) - acc.px(a);
        double dy = acc.py(b) - acc.py(a);
        if (periodic) {
            dx -= L * std::round(dx / L);
            dy -= L * std::round(dy / L);
        }
        double d = std::sqrt(dx * dx + dy * dy) - acc.pradius(a) - acc.pradius(b);
        if (d <= rc) {
            neighbors[acc.pid(a)].push_back(acc.pid(b));
            neighbors[acc.pid(b)].push_back(acc.pid(a));
        }
    };

    for (int cy = 0; cy < M; ++cy) {
        for (int cx = 0; cx < M; ++cx) {
            int cell = cy * M + cx;

            // Pares dentro de la propia celda (cada par una sola vez).
            for (int a = head[cell]; a != -1; a = next[a]) {
                for (int b = next[a]; b != -1; b = next[b]) {
                    try_pair(particles[a], particles[b]);
                }
            }

            for (const auto& d : dirs) {
                int ny = cy + d[0];
                int nx = cx + d[1];
                if (periodic) {
                    ny = ((ny % M) + M) % M;
                    nx = ((nx % M) + M) % M;
                } else if (ny < 0 || ny >= M || nx < 0 || nx >= M) {
                    continue;
                }
                if (ny == cy && nx == cx) continue;  // celda vecina envuelta sobre sí misma (M chico + PBC)

                int ncell = ny * M + nx;
                for (int a = head[cell]; a != -1; a = next[a]) {
                    for (int b = head[ncell]; b != -1; b = next[b]) {
                        try_pair(particles[a], particles[b]);
                    }
                }
            }
        }
    }
}

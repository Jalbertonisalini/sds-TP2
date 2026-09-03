#pragma once
#include <vector>
#include <chrono>
#include "particle.hpp"
#include "welford.hpp"

// Utilidades de SDS-TP1/source/java/CellIndexMethod.java (M óptimo, radio máximo)
// más el harness de benchmark genérico. El kernel del CIM en sí es compartido y
// layout-agnóstico: vive en cell_index_method_shared.hpp y lo usa tanto el benchmark
// del TP1 como el --cim-timing del TP2 (ver punto g).
namespace cim_tp1 {

double max_radius(const std::vector<Particle>& particles);

// Restricción del CIM: cellSize = L/M debe ser mayor que rc + 2*r_max.
int max_allowed_m(double L, double rc, double r_max);

// Mide una corrida (run_once) con el mismo esquema de batching que
// SDS-TP1/source/java/CellIndexMethod.java: warmup_reps lotes sin medir, luego reps
// lotes de batch_size corridas cada uno, promediando tiempo/batch_size por lote.
template <typename RunOnce>
Welford benchmark(RunOnce&& run_once, int warmup_reps, int reps, int batch_size) {
    for (int i = 0; i < warmup_reps; ++i) {
        for (int b = 0; b < batch_size; ++b) run_once();
    }

    Welford stats;
    for (int i = 0; i < reps; ++i) {
        auto start = std::chrono::steady_clock::now();
        for (int b = 0; b < batch_size; ++b) run_once();
        auto elapsed = std::chrono::steady_clock::now() - start;
        double elapsed_ms = std::chrono::duration<double, std::milli>(elapsed).count();
        stats.add(elapsed_ms / batch_size);
    }
    return stats;
}

}  // namespace cim_tp1

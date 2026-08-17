#pragma once
#include <vector>
#include "Particle.hpp"
#include "Config.hpp"

class CellIndexMethod {
private:
    int M;
    double L;
    double rc;
    double r_max;
    bool periodic;
    double cell_size;
    // Arreglos planos para la simulación de listas enlazadas (cache-friendly)
    std::vector<int> head;
    std::vector<int> next;

    [[nodiscard]] int get_cell_index(double x, double y) const;
    [[nodiscard]] int wrap(int index) const;

public:
    explicit CellIndexMethod(const SimulationConfig& config);

    // Reconstruye la grilla espacial (se llama en cada paso de tiempo)
    void build(const std::vector<Particle>& particles);

    // Retorna los IDs de las partículas vecinas dentro del radio de corte
    [[nodiscard]] std::vector<int> get_neighbors(const std::vector<Particle>& particles, int particle_id) const;
};
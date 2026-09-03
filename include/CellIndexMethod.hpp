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
    // Lista global de vecinos para la variante en un solo paso (benchmark)
    std::vector<std::vector<int>> all_neighbors;

    [[nodiscard]] int get_cell_index(double x, double y) const;
    [[nodiscard]] int wrap(int index) const;
    void try_pair(const Particle& a, const Particle& b,
                  std::vector<std::vector<int>>& neighbors) const;

public:
    explicit CellIndexMethod(const SimulationConfig& config);

    // Reconstruye la grilla espacial (se llama en cada paso de tiempo)
    void build(const std::vector<Particle>& particles);

    // Retorna los IDs de las partículas vecinas dentro del radio de corte
    [[nodiscard]] std::vector<int> get_neighbors(const std::vector<Particle>& particles, int particle_id) const;

    // Construye la grilla y la lista global de vecinos de todas las partículas en
    // un solo recorrido (usa la simetría de 4 direcciones, cada par una sola vez).
    // Resulta en los mismos vecinos que get_neighbors() para cada partícula.
    void build_all_neighbors(const std::vector<Particle>& particles);

    // Acceso a la lista global construida por build_all_neighbors().
    [[nodiscard]] const std::vector<std::vector<int>>& get_all_neighbors() const;
};
#pragma once
#include <vector>
#include <random>
#include "Particle.hpp"
#include "Config.hpp"
#include "CellIndexMethod.hpp"

class SimulationEngine {
private:
    SimulationConfig config;
    CellIndexMethod cim;
    std::vector<Particle> particles;
    
    // Motor de aleatoriedad
    std::mt19937 gen;
    std::uniform_real_distribution<double> noise_dist;

    // Reglas de evolución
    void update_vicsek(std::vector<Particle>& next_state);
    void update_voter(std::vector<Particle>& next_state);

public:
    SimulationEngine(const SimulationConfig& cfg, const std::vector<Particle>& initial_state,
                     unsigned int seed = 42);

    // Avanza la simulación un paso temporal (t -> t+1)
    void step();

    // Devuelve el estado actual para poder guardarlo
    const std::vector<Particle>& get_particles() const;

    // Polarización instantánea va = |<(cos θ, sin θ)>| sobre las partículas
    double polarizacion() const;

    // Construye el CIM para el estado actual y devuelve la fracción del cluster más grande
    double compute_largest_cluster_fraction();

    // Devuelve la fracción del cluster más grande (asume CIM ya construido)
    double largest_cluster_fraction() const;

    // Un pase completo del CIM (build + consulta de vecinos de todas las partículas),
    // sin timing propio, para benchmarking externo (ver --cim-timing en main.cpp).
    void run_cim_pass();
};
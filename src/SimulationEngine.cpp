#include "SimulationEngine.hpp"
#include <cmath>
#include <algorithm>
#include <queue>

SimulationEngine::SimulationEngine(const SimulationConfig& cfg, const std::vector<Particle>& initial_state,
                                   unsigned int seed)
    : config(cfg), cim(cfg), particles(initial_state), gen(seed) {
    
    // El ruido se define típicamente en el intervalo [-eta/2, eta/2]
    noise_dist = std::uniform_real_distribution<double>(-config.eta / 2.0, config.eta / 2.0);
}

const std::vector<Particle>& SimulationEngine::get_particles() const {
    return particles;
}

// Mismo criterio que python/polarizacion.py: va = |promedio de vectores unitarios|
double SimulationEngine::polarizacion() const {
    double ux = 0.0;
    double uy = 0.0;
    for (const auto& p : particles) {
        ux += std::cos(p.angle);
        uy += std::sin(p.angle);
    }
    double n = static_cast<double>(particles.size());
    return std::hypot(ux / n, uy / n);
}

void SimulationEngine::step() {
    std::vector<Particle> next_state = particles; // Copia inicial para el doble buffer
    cim.build(particles);

    if (config.model == ModelType::Standard) {
        update_vicsek(next_state);
    } else {
        update_voter(next_state);
    }

    particles = std::move(next_state); // Swap eficiente
}

void SimulationEngine::update_vicsek(std::vector<Particle>& next_state) {
    for (size_t i = 0; i < particles.size(); ++i) {
        auto neighbors = cim.get_neighbors(particles, i);
        
        double sin_sum = std::sin(particles[i].angle);
        double cos_sum = std::cos(particles[i].angle);

        for (int neighbor_id : neighbors) {
            sin_sum += std::sin(particles[neighbor_id].angle);
            cos_sum += std::cos(particles[neighbor_id].angle);
        }

        // Promedio de direcciones + ruido
        double avg_angle = std::atan2(sin_sum, cos_sum);
        next_state[i].angle = avg_angle + noise_dist(gen);

        // Actualización de posición (Euler)
        next_state[i].position.x += config.velocity * std::cos(next_state[i].angle);
        next_state[i].position.y += config.velocity * std::sin(next_state[i].angle);

        // Condiciones periódicas
        if (next_state[i].position.x >= config.L) next_state[i].position.x -= config.L;
        if (next_state[i].position.x < 0)         next_state[i].position.x += config.L;
        if (next_state[i].position.y >= config.L) next_state[i].position.y -= config.L;
        if (next_state[i].position.y < 0)         next_state[i].position.y += config.L;
    }
}

void SimulationEngine::update_voter(std::vector<Particle>& next_state) {
    for (size_t i = 0; i < particles.size(); ++i) {
        auto neighbors = cim.get_neighbors(particles, i);

        // Sin vecinos: la partícula se copia a sí misma (único fallback)
        if (neighbors.empty()) {
            neighbors.push_back(i);
        }

        // Selección de un agente al azar
        std::uniform_int_distribution<int> neighbor_dist(0, neighbors.size() - 1);
        int chosen_idx = neighbors[neighbor_dist(gen)];

        // Copia de dirección + ruido (envuelto a [-pi, pi] para evitar drift sin límite)
        double copied_angle = particles[chosen_idx].angle + noise_dist(gen);
        next_state[i].angle = std::atan2(std::sin(copied_angle), std::cos(copied_angle));

        // Actualización de posición (Euler)
        next_state[i].position.x += config.velocity * std::cos(next_state[i].angle);
        next_state[i].position.y += config.velocity * std::sin(next_state[i].angle);

        // Condiciones periódicas
        if (next_state[i].position.x >= config.L) next_state[i].position.x -= config.L;
        if (next_state[i].position.x < 0)         next_state[i].position.x += config.L;
        if (next_state[i].position.y >= config.L) next_state[i].position.y -= config.L;
        if (next_state[i].position.y < 0)         next_state[i].position.y += config.L;
    }
}

double SimulationEngine::largest_cluster_fraction() const {
    int N = static_cast<int>(particles.size());
    std::vector<bool> visited(N, false);
    int max_cluster = 0;

    for (int i = 0; i < N; ++i) {
        if (visited[i]) continue;

        int cluster_size = 0;
        std::queue<int> q;
        q.push(i);
        visited[i] = true;

        while (!q.empty()) {
            int current = q.front();
            q.pop();
            cluster_size++;

            auto neighbors = cim.get_neighbors(particles, current);
            for (int neighbor : neighbors) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    q.push(neighbor);
                }
            }
        }

        max_cluster = std::max(max_cluster, cluster_size);
    }

    return static_cast<double>(max_cluster) / static_cast<double>(N);
}

double SimulationEngine::compute_largest_cluster_fraction() {
    cim.build(particles);
    return largest_cluster_fraction();
}
#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include "Particle.hpp"
#include "Config.hpp"
#include "SimulationEngine.hpp"
#include "OutputWriter.hpp"

// Función para generar partículas evitando que nazcan pegadas
std::vector<Particle> generate_particles(const SimulationConfig& config, int N, bool allow_overlap) {
    std::vector<Particle> particles;
    particles.reserve(N);
    
    std::mt19937 gen(1234);
    std::uniform_real_distribution<double> pos_dist(0.0, config.L);
    std::uniform_real_distribution<double> angle_dist(-M_PI, M_PI);
    
    double min_dist_sq = 0.01; // Tolerancia mínima si no se permite overlap

    while (particles.size() < static_cast<size_t>(N)) {
        Vec2 candidate_pos = {pos_dist(gen), pos_dist(gen)};
        bool valid = true;

        if (!allow_overlap) {
            for (const auto& p : particles) {
                double dx = candidate_pos.x - p.position.x;
                double dy = candidate_pos.y - p.position.y;
                
                // Evaluar distancia considerando topología periódica
                if (dx > config.L / 2.0) dx -= config.L;
                else if (dx < -config.L / 2.0) dx += config.L;
                if (dy > config.L / 2.0) dy -= config.L;
                else if (dy < -config.L / 2.0) dy += config.L;

                if (dx * dx + dy * dy < min_dist_sq) {
                    valid = false;
                    break;
                }
            }
        }

        if (valid) {
            int id = particles.size();
            particles.push_back({id, candidate_pos, angle_dist(gen), 0.0}); // radio = 0.0
        }
    }
    return particles;
}

int main() {
    SimulationConfig config;
    config.L = 10.0;           // Caja cuadrada[cite: 1]
    config.density = 4;      // Seleccionamos rho = 4 para esta corrida[cite: 1]
    config.rc = 1.0;
    config.r_max = 0.0;        // Partículas off-lattice puntuales
    config.eta = 0.5;          // Ruido de prueba
    config.velocity = 0.03;
    config.iterations = 10000;
    config.model = ModelType::Voter; // Cambiar a Voter para el otro escenario[cite: 1]

    bool allow_overlap = false; // Flag requerido
    
    int N = static_cast<int>(config.density * config.L * config.L);
    std::cout << "Generando " << N << " particulas (rho=" << config.density << ")...\n";
    
    auto initial_state = generate_particles(config, N, allow_overlap);
    SimulationEngine engine(config, initial_state);
    
    OutputWriter writer("evolucion_dinamica.csv");
    writer.save_step(0, engine.get_particles());

    std::cout << "Iniciando simulacion...\n";
    for (int t = 1; t <= config.iterations; ++t) {
        engine.step();
        writer.save_step(t, engine.get_particles());
        
        if (t % 100 == 0) {
            std::cout << "Progreso: Paso " << t << " / " << config.iterations << "\n";
        }
    }
    
    std::cout << "Simulacion finalizada. Datos exportados.\n";
    return 0;
}
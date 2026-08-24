#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <string>
#include "Particle.hpp"
#include "Config.hpp"
#include "SimulationEngine.hpp"
#include "OutputWriter.hpp"

// Función para generar partículas evitando que nazcan pegadas
std::vector<Particle> generate_particles(const SimulationConfig& config, int N, bool allow_overlap, unsigned int seed) {
    std::vector<Particle> particles;
    particles.reserve(N);
    
    std::mt19937 gen(seed);
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

void imprimir_uso(const char* programa) {
    std::cout << "Uso: " << programa << " [opciones]\n"
              << "Sin opciones corre la configuración por defecto y vuelca la trayectoria completa.\n\n"
              << "  --density <rho>     Densidad de partículas (default 4)\n"
              << "  --eta <eta>         Amplitud del ruido (default 0.5)\n"
              << "  --iterations <n>    Cantidad de pasos (default 10000)\n"
              << "  --model <modelo>    standard | voter (default voter)\n"
              << "  --seed <semilla>    Semilla de aleatoriedad (default 42)\n"
              << "  --output <ruta>     CSV compacto Time,Polarization,S (un valor por paso)\n"
              << "  -h, --help          Mostrar esta ayuda\n";
}

int main(int argc, char* argv[]) {
    SimulationConfig config;
    config.L = 10.0;
    config.density = 4;
    config.rc = 1.0;
    config.r_max = 0.0;        // Partículas off-lattice puntuales
    config.eta = 0.5;          // Ruido de prueba
    config.velocity = 0.03;
    config.iterations = 20000;
    config.model = ModelType::Standard; // Cambiar a Voter para el otro escenario[cite: 1]

    bool allow_overlap = false; // Flag requerido
    unsigned int seed = 42;
    std::string output_path;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            imprimir_uso(argv[0]);
            return 0;
        }

        if (i + 1 >= argc) {
            std::cerr << "Error: " << arg << " requiere un valor.\n";
            imprimir_uso(argv[0]);
            return 1;
        }
        std::string valor = argv[++i];

        if (arg == "--density") {
            config.density = std::stod(valor);
        } else if (arg == "--eta") {
            config.eta = std::stod(valor);
        } else if (arg == "--iterations") {
            config.iterations = std::stoi(valor);
        } else if (arg == "--model") {
            if (valor == "standard") {
                config.model = ModelType::Standard;
            } else if (valor == "voter") {
                config.model = ModelType::Voter;
            } else {
                std::cerr << "Error: modelo desconocido '" << valor << "'.\n";
                imprimir_uso(argv[0]);
                return 1;
            }
        } else if (arg == "--seed") {
            seed = static_cast<unsigned int>(std::stoul(valor));
        } else if (arg == "--output") {
            output_path = valor;
        } else {
            std::cerr << "Error: opción desconocida '" << arg << "'.\n";
            imprimir_uso(argv[0]);
            return 1;
        }
    }

    int N = static_cast<int>(config.density * config.L * config.L);
    std::cout << "Generando " << N << " particulas (rho=" << config.density
              << ", eta=" << config.eta
              << ", modelo=" << (config.model == ModelType::Standard ? "standard" : "voter")
              << ")...\n";
    
    auto initial_state = generate_particles(config, N, allow_overlap, seed);
    SimulationEngine engine(config, initial_state, seed);

    std::cout << "Iniciando simulacion...\n";

    if (!output_path.empty()) {
        // Modo experimento: serie temporal compacta de polarización y clusters
        OutputWriter writer(output_path, "Time,Polarization,S");
        writer.save_scalar_2(0, engine.polarizacion(), engine.compute_largest_cluster_fraction());

        for (int t = 1; t <= config.iterations; ++t) {
            engine.step();
            writer.save_scalar_2(t, engine.polarizacion(), engine.largest_cluster_fraction());

            if (t % 100 == 0) {
                std::cout << "Progreso: Paso " << t << " / " << config.iterations << "\n";
            }
        }

        std::cout << "Simulacion finalizada. Polarizacion final: "
                  << engine.polarizacion() << ", Cluster mas grande: "
                  << engine.largest_cluster_fraction() << "\n";
        std::cout << "Serie temporal guardada en " << output_path << "\n";
    } else {
        // Modo original: volcado completo de trayectorias
        OutputWriter writer("evolucion_dinamica.csv");
        writer.save_step(0, engine.get_particles());

        for (int t = 1; t <= config.iterations; ++t) {
            engine.step();
            writer.save_step(t, engine.get_particles());
            
            if (t % 100 == 0) {
                std::cout << "Progreso: Paso " << t << " / " << config.iterations << "\n";
            }
        }
        
        std::cout << "Simulacion finalizada. Datos exportados.\n";
    }
    return 0;
}

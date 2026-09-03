#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <string>
#include <chrono>
#include <fstream>
#include "Particle.hpp"
#include "Config.hpp"
#include "SimulationEngine.hpp"
#include "OutputWriter.hpp"
#include "cell_index_method_shared.hpp"

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

// Accessors para el Particle de TP2 (Vec2 position + radius): alimentan el kernel
// CIM compartido (layout-agnóstico) que usa también el benchmark del TP1, de modo
// que el --cim-timing del punto g) mide exactamente el mismo código que el TP1.
struct Tp2Accessor {
    static double px(const Particle& p) { return p.position.x; }
    static double py(const Particle& p) { return p.position.y; }
    static double pradius(const Particle& p) { return p.radius; }
    static int pid(const Particle& p) { return p.id; }
};

void imprimir_uso(const char* programa) {
    std::cout << "Uso: " << programa << " [opciones]\n"
              << "Sin opciones corre la configuración por defecto y vuelca la trayectoria completa.\n\n"
              << "  --density <rho>     Densidad de partículas (default 4)\n"
              << "  --n <N>             Cantidad de partículas (reemplaza density*L*L; sirve para\n"
              << "                      usar los mismos N que el benchmark del TP1, ver punto g)\n"
              << "  --eta <eta>         Amplitud del ruido (default 0.5)\n"
              << "  --iterations <n>    Cantidad de pasos (default 10000)\n"
              << "  --model <modelo>    standard | voter (default voter)\n"
              << "  --seed <semilla>    Semilla de aleatoriedad (default 42)\n"
              << "  --output <ruta>     CSV compacto Time,Polarization,S (un valor por paso)\n"
              << "  --cim-timing <ruta> Mide tiempo de CIM (build + vecinos) sobre config. inicial,\n"
              << "                      agrega una fila a <ruta> (no corre la simulación)\n"
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
    int N_override = -1;        // Si se pasa --n, se usa en vez de density*L*L
    std::string output_path;
    std::string cim_timing_path;

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
        } else if (arg == "--n") {
            N_override = std::stoi(valor);
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
        } else if (arg == "--cim-timing") {
            cim_timing_path = valor;
        } else {
            std::cerr << "Error: opción desconocida '" << arg << "'.\n";
            imprimir_uso(argv[0]);
            return 1;
        }
    }

    int N = N_override >= 0 ? N_override
                            : static_cast<int>(config.density * config.L * config.L);
    std::cout << "Generando " << N << " particulas (rho=" << config.density
              << ", eta=" << config.eta
              << ", modelo=" << (config.model == ModelType::Standard ? "standard" : "voter")
              << ")...\n";
    
    auto initial_state = generate_particles(config, N, allow_overlap, seed);
    SimulationEngine engine(config, initial_state, seed);

    if (!cim_timing_path.empty()) {
        // Benchmark del CIM (punto g): usa el MISMO kernel compartido que el TP1
        // (cell_index_method_shared.hpp, layout-agnóstico) con la geometría de TP2
        // (L=10, M óptimo = floor(L/(rc+2*r_max))), sin evolucionar la simulación.
        // Mismo esquema de batching que SDS-TP1/source/java/NBenchmark.java, para
        // poder comparar directo con esos tiempos.
        int M = static_cast<int>(std::floor(config.L / (config.rc + 2.0 * config.r_max)));
        std::vector<std::vector<int>> neighbors;

        auto run_pass = [&]() {
            shared_build_all_neighbors(initial_state, config.L, M, config.rc, config.periodic,
                                       Tp2Accessor{}, neighbors);
        };

        int batch_size = 100;
        int samples = (N <= 200 ? 300000 : 3000) / batch_size;

        for (int i = 0; i < samples; ++i) {
            for (int b = 0; b < batch_size; ++b) run_pass();
        }

        double mean = 0.0, m2 = 0.0;
        for (int i = 1; i <= samples; ++i) {
            auto start = std::chrono::steady_clock::now();
            for (int b = 0; b < batch_size; ++b) run_pass();
            double ms = std::chrono::duration<double, std::milli>(
                            std::chrono::steady_clock::now() - start).count() / batch_size;
            double delta = ms - mean;
            mean += delta / i;
            m2 += delta * (ms - mean);
        }
        double stddev = samples > 1 ? std::sqrt(m2 / (samples - 1)) : 0.0;

        bool write_header;
        {
            std::ifstream check(cim_timing_path);
            write_header = !check.good() || check.peek() == std::ifstream::traits_type::eof();
        }
        std::ofstream out(cim_timing_path, std::ios::app);
        if (write_header) out << "regimen,N,L,M,rho,time_mean_ms,time_std_ms,reps,batch\n";
        out << "tp2," << N << "," << config.L << "," << M << ","
            << (N / (config.L * config.L)) << "," << mean << "," << stddev << ","
            << samples << "," << batch_size << "\n";

        std::cout << "CIM: N=" << N << "  L=" << config.L << "  M=" << M
                  << "  tiempo=" << mean << "±" << stddev
                  << " ms  (batch=" << batch_size << ", muestras=" << samples << ")\n";
        std::cout << "Guardado en " << cim_timing_path << "\n";
        return 0;
    }

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

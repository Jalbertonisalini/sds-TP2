#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include "cell_index_method.hpp"
#include "cell_index_method_shared.hpp"
#include "particle.hpp"
#include "welford.hpp"

// Benchmark del CIM del TP1 (Java) portado a C++. Usa la MISMA implementación del
// kernel que el --cim-timing del TP2 (cell_index_method_shared.hpp), de modo que la
// comparación del punto g) mida un kernel byte-por-byte idéntico; solo difiere la
// geometría de la caja (L y M). Ver cell_index_method_shared.hpp.
// Uso: cim_bench <N> <L> <rc> <periodic> <regimen> [csv] [forceM1] [static_path] [dynamic_path]
//
// forceM1=true fuerza M=1: una sola celda, o sea TODOS los pares evaluados una vez.
// Eso es exactamente fuerza bruta O(N^2), medida con el mismo kernel y el mismo
// esquema de batching que el CIM, que es lo que pide la comparacion del punto g).
//
// Lee los mismos input/static.txt e input/dynamic.txt generados por
// SDS-TP1/source/python/generate_input.py (no se regenera acá), con el mismo esquema
// de batching que NBenchmark.java, para poder comparar tiempos contra SDS-TP1.

namespace {

// Accessors para el Particle de TP1 (x, y, vx, vy, radius): me permiten alimentar el
// kernel compartido (layout-agnóstico) con este tipo.
struct Tp1Accessor {
    static double px(const Particle& p) { return p.x; }
    static double py(const Particle& p) { return p.y; }
    static double pradius(const Particle& p) { return p.radius; }
    static int pid(const Particle& p) { return p.id; }
};

std::vector<Particle> read_particles(int N, const std::string& static_path, const std::string& dynamic_path) {
    std::vector<double> radii(N);
    {
        std::ifstream in(static_path);
        if (!in) throw std::runtime_error("no se pudo abrir " + static_path);
        int file_n;
        in >> file_n;
        if (file_n != N) {
            throw std::runtime_error(static_path + " declara N=" + std::to_string(file_n) +
                                      " pero se pidió N=" + std::to_string(N));
        }
        std::string discard_line;
        std::getline(in, discard_line);  // resto de la línea de N
        std::getline(in, discard_line);  // línea de L, no se usa acá (se pasa como argumento aparte)
        for (int i = 0; i < N; ++i) {
            std::string line;
            std::getline(in, line);
            // Cada línea trae radio + una columna extra que TP1 ignora (mismo criterio
            // que StringTokenizer(line).nextToken() en InputParser.java).
            std::istringstream tokenizer(line);
            tokenizer >> radii[i];
        }
    }

    std::vector<Particle> particles;
    particles.reserve(N);
    {
        std::ifstream in(dynamic_path);
        if (!in) throw std::runtime_error("no se pudo abrir " + dynamic_path);
        std::string t0_line;
        std::getline(in, t0_line);  // encabezado t0
        for (int i = 0; i < N; ++i) {
            double x, y, vx, vy;
            in >> x >> y >> vx >> vy;
            particles.push_back({i, x, y, vx, vy, radii[i]});
        }
    }
    return particles;
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 6) {
        std::cerr << "Uso: " << argv[0]
                  << " <N> <L> <rc> <periodic> <regimen> [csv] [forceM1] [static_path] [dynamic_path]\n";
        return 1;
    }

    int N = std::stoi(argv[1]);
    double L = std::stod(argv[2]);
    double rc = std::stod(argv[3]);
    std::string periodic_str = argv[4];
    bool pbc = (periodic_str == "true");
    std::string regimen = argv[5];
    std::string csv_path = argc > 6 ? argv[6] : "output/n_benchmark.csv";
    bool force_m1 = argc > 7 && std::string(argv[7]) == "true";
    std::string static_path = argc > 8 ? argv[8] : "input/static.txt";
    std::string dynamic_path = argc > 9 ? argv[9] : "input/dynamic.txt";

    auto particles = read_particles(N, static_path, dynamic_path);

    double r_max = cim_tp1::max_radius(particles);
    int M = force_m1 ? 1 : cim_tp1::max_allowed_m(L, rc, r_max);
    if (M < 1) {
        std::cerr << "Error: máximo permitido de M menor a 1\n";
        return 1;
    }

    // Mismo esquema de batching para CIM (M optimo) y fuerza bruta (M=1): las cuatro
    // series del punto g) tienen que ser comparables entre si, no solo de a pares.
    int batch_size = 100;
    int samples = (N <= 200 ? 300000 : 3000) / batch_size;

    std::vector<std::vector<int>> neighbors;
    Welford stats = cim_tp1::benchmark(
        [&]() { shared_build_all_neighbors(particles, L, M, rc, pbc, Tp1Accessor{}, neighbors); },
        samples, samples, batch_size);

    bool write_header = true;
    {
        std::ifstream check(csv_path);
        write_header = !check.good() || check.peek() == std::ifstream::traits_type::eof();
    }
    std::ofstream out(csv_path, std::ios::app);
    if (write_header) {
        out << "regimen,N,L,M,time_mean_ms,time_std_ms,reps,batch\n";
    }
    out << regimen << "," << N << "," << L << "," << M << "," << stats.mean() << "," << stats.std() << ","
        << samples << "," << batch_size << "\n";

    std::cout << "regimen=" << regimen << "  N=" << N << "  L=" << L << "  M=" << M << "  CIM=" << stats.mean()
              << "±" << stats.std() << " ms  (batch=" << batch_size << ", muestras=" << samples << ")\n";

    return 0;
}

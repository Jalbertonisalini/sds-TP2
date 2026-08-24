#pragma once
#include <string>
#include <fstream>
#include <vector>
#include "Particle.hpp"

class OutputWriter {
private:
    std::ofstream file;

public:
    // Constructor: abre el archivo dinámico y escribe los encabezados
    explicit OutputWriter(const std::string& filename);

    // Serie temporal escalar (ej. polarización): encabezado personalizado
    OutputWriter(const std::string& filename, const std::string& header);
    
    // Destructor: se encarga de cerrar el archivo automáticamente (RAII)
    ~OutputWriter();

    // Volcar el estado de un instante de tiempo t
    void save_step(int time_step, const std::vector<Particle>& particles);

    // Volcar dos valores escalares del instante t (serie temporal)
    void save_scalar_2(int time_step, double v1, double v2);

    // Métodos estáticos (opcionales, para fotos estáticas o debug)
    static void save_positions(const std::string& filename, const std::vector<Particle>& particles);
    static void save_neighbors(const std::string& filename, const std::vector<std::vector<int>>& all_neighbors);
};
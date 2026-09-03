#include "OutputWriter.hpp"
#include <stdexcept>

// Inicialización de la simulación dinámica
OutputWriter::OutputWriter(const std::string& filename) {
    file.open(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Error: No se pudo abrir el archivo de salida " + filename);
    }
    // Escribimos los encabezados del CSV
    file << "Time,ID,X,Y,Angle,Radius\n";
}

// Serie temporal escalar con encabezado a medida (ej. "Time,Polarization")
OutputWriter::OutputWriter(const std::string& filename, const std::string& header) {
    file.open(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Error: No se pudo abrir el archivo de salida " + filename);
    }
    file << header << "\n";
}

// Cierre seguro
OutputWriter::~OutputWriter() {
    if (file.is_open()) {
        file.close();
    }
}

// Escritura de cada paso temporal
void OutputWriter::save_step(int time_step, const std::vector<Particle>& particles) {
    for (const auto& p : particles) {
        file << time_step << ","
             << p.id << ","
             << p.position.x << ","
             << p.position.y << ","
             << p.angle << ","
             << p.radius << "\n";
    }
}

// Escritura de dos valores escalares por paso temporal
void OutputWriter::save_scalar_2(int time_step, double v1, double v2) {
    file << time_step << "," << v1 << "," << v2 << "\n";
}

// --- Métodos estáticos auxiliares ---

void OutputWriter::save_positions(const std::string& filename, const std::vector<Particle>& particles) {
    std::ofstream out_file(filename);
    if (!out_file.is_open()) throw std::runtime_error("Error al abrir " + filename);
    
    out_file << "ID,X,Y,Radius\n";
    for (const auto& p : particles) {
        out_file << p.id << "," << p.position.x << "," << p.position.y << "," << p.radius << "\n";
    }
}
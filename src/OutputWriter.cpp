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

// Escritura de un valor escalar por paso temporal
void OutputWriter::save_scalar(int time_step, double value) {
    file << time_step << "," << value << "\n";
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

void OutputWriter::save_neighbors(const std::string& filename, const std::vector<std::vector<int>>& all_neighbors) {
    std::ofstream out_file(filename);
    if (!out_file.is_open()) throw std::runtime_error("Error al abrir " + filename);
    
    for (size_t i = 0; i < all_neighbors.size(); ++i) {
        out_file << i << " [";
        for (size_t j = 0; j < all_neighbors[i].size(); ++j) {
            out_file << all_neighbors[i][j];
            if (j < all_neighbors[i].size() - 1) out_file << ", ";
        }
        out_file << "]\n";
    }
}
#pragma once

enum class ModelType {
    Standard, // Modelo de Vicsek que promedia direcciones
    Voter     // Modelo que copia la dirección de un vecino al azar
};

struct SimulationConfig {
    double L = 10.0;
    double density = 4;
    double eta = 0.5;
    double rc = 1.0;
    double r_max = 0.0;
    bool periodic = true;
    double velocity = 0.03;
    int iterations = 20000;
    ModelType model = ModelType::Voter;
};
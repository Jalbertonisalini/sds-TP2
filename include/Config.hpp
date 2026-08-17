#pragma once

enum class ModelType {
    Standard, // Modelo de Vicsek que promedia direcciones
    Voter     // Modelo que copia la dirección de un vecino al azar
};

struct SimulationConfig {
    double L = 10.0;           // Lado de la caja
    double density = 2.0;      // Densidades a estudiar
    double eta = 0.1;          // Ruido
    double rc = 1.0;
    double r_max = 0.0;        // Radio máximo para calcular celdas
    bool periodic = true;      // Toggle de condiciones periódicas
    double velocity = 0.03;
    int iterations = 1000;
    ModelType model = ModelType::Standard;
};
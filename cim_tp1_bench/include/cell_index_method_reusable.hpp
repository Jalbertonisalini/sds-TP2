#pragma once
#include <vector>
#include "particle.hpp"

// Algoritmo de CellIndexMethod.java (grilla M x M, 4 direcciones vecinas + celda
// propia, cada par se evalúa una sola vez), pero con la estructura de datos que
// resultó más útil en C++ (misma idea que src/CellIndexMethod.cpp de TP2): dos
// arrays planos head/next tipo lista enlazada, reservados una vez y reutilizados
// entre llamadas, en vez de un vector<vector<int>> por celda (que era la traducción
// literal del List<List<Integer>> del Java original). Sin allocs dentro de run().
class CellIndexMethodReusable {
public:
    // Devuelve una referencia a los vecinos por partícula (válida hasta la próxima
    // llamada a run) — evita también la copia del resultado en cada corrida.
    const std::vector<std::vector<int>>& run(const std::vector<Particle>& particles, double L, int M, double rc,
                                              bool pbc);

private:
    std::vector<int> head_;               // head_[celda] = id de la primera partícula en esa celda, o -1
    std::vector<int> next_;               // next_[id] = siguiente partícula en la misma celda, o -1
    std::vector<std::vector<int>> neighbors_;
};

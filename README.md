# TP2 - Autómata Off-Lattice

Repositorio para el TP2 de la materia **Simulación de Sistemas** (ITBA).

Simulación de un modelo de enjambre tipo Vicsek usando un Autómata Celular Off-Lattice con método de celdas para búsqueda eficiente de vecinos.

> **Nota:** El modelo Voter no está implementado aún.

## Requisitos

- **C++17** (o superior)
- **CMake** >= 3.15
- **Python 3.x** (para visualización)

### Dependencias de Python

```bash
pip install -r python/requirements.txt
```

## Compilación

Desde la raíz del proyecto:

```bash
mkdir -p build && cd build
cmake ..
make
```

Esto genera el ejecutable `build/simulador`.

## Ejecución

### Simulación

```bash
cd build
./simulador
```

Ejecuta 10.000 pasos de simulación y genera el archivo `evolucion_dinamica.csv`.

### Visualización

```bash
cd python
python animar_simulacion.py
```

Lee el CSV generado y muestra una animación de las partículas con matplotlib.

## Parámetros de simulación

Los parámetros están definidos en `src/main.cpp`:

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `L` | 10.0 | Lado de la caja cuadrada |
| `density` | 8 | Densidad de partículas (N = density × L²) |
| `rc` | 1.0 | Radio de interacción |
| `r_max` | 0.0 | Radio máximo de partículas (puntuales) |
| `eta` | 0.5 | Amplitud del ruido |
| `velocity` | 0.03 | Velocidad de las partículas |
| `iterations` | 10000 | Cantidad de pasos |
| `model` | `Standard` | Modelo: `Standard` (Vicsek) |

## Estructura del proyecto

```
sds-TP2/
├── CMakeLists.txt
├── include/
│   ├── CellIndexMethod.hpp
│   ├── Config.hpp
│   ├── OutputWriter.hpp
│   ├── Particle.hpp
│   ├── SimulationEngine.hpp
│   └── Vec2.hpp
├── src/
│   ├── main.cpp
│   ├── CellIndexMethod.cpp
│   ├── OutputWriter.cpp
│   └── SimulationEngine.cpp
├── python/
│   ├── animar_simulacion.py
│   └── requirements.txt
├── build/
│   └── simulador
└── docs/
    └── TP2_Enunciado.pdf
```

## Output

El archivo `evolucion_dinamica.csv` tiene las columnas:

```
Time, ID, X, Y, Angle, Radius
```

Cada fila representa el estado de una partícula en un instante de tiempo.

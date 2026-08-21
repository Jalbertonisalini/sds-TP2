# TP2 - Autómata Off-Lattice

Repositorio para el TP2 de la materia **Simulación de Sistemas** (ITBA).

Simulación de un modelo de enjambre tipo Vicsek usando un Autómata Celular Off-Lattice con método de celdas para búsqueda eficiente de vecinos.

> **Nota:** El modelo Voter está implementado (`ModelType::Voter`). Cada partícula copia la dirección de un vecino elegido al azar dentro de su radio de interacción; si no tiene vecinos, conserva su propia dirección (más ruido).

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

Sin opciones, ejecuta 10.000 pasos con la configuración por defecto y genera el archivo `evolucion_dinamica.csv` (trayectoria completa). Los parámetros pueden sobrescribirse por línea de comandos:

```bash
./simulador --model standard --density 4 --eta 0.6 --iterations 10000 --output resultados/mi_corrida.csv
```

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--density` | 4 | Densidad de partículas (N = density × L²) |
| `--eta` | 0.5 | Amplitud del ruido |
| `--iterations` | 10000 | Cantidad de pasos |
| `--model` | `voter` | Modelo de interacción: `standard` (Vicsek) o `voter` |
| `--seed` | 42 | Semilla de aleatoriedad (condición inicial y ruido) |
| `--output` | *(vacío)* | Si se indica, en vez de la trayectoria completa escribe un CSV compacto `Time,Polarization` con un valor por paso |

Los parámetros fijos (`L = 10`, `rc = 1.0`, `velocity = 0.03`) están definidos en `src/main.cpp`.

### Visualización

```bash
cd python
python animar_simulacion.py
```

Lee el CSV generado y muestra una animación de las partículas con matplotlib.

### Análisis: Polarización

```bash
cd python
python polarizacion.py
```

Lee el CSV generado y calcula la polarización `va(t) = |<vector velocidad unitario>|` promediada sobre las partículas en cada timestep. Grafica la evolución temporal, detecta automáticamente el inicio del régimen estacionario (MSER sobre promedios por bloque) y reporta `<va>` con su desvío en ese tramo. Guarda el gráfico en `python/output/polarizacion_vs_tiempo.png`.

### Experimento: Ruido en Vicsek

Dos estudios del efecto del ruido η sobre la polarización (ρ = 4, modelo Standard), cada uno con sus propios resultados:

**a) Comparación de 3 ruidos** — una corrida por nivel de ruido (η = 0.6, 2.2 y 5.3); cada caso guarda su serie temporal `va(t)` en `build/resultados/` y luego se combinan en un único gráfico comparativo (`python/output/polarizacion_comparacion.png`):

```bash
cd python
python correr_ruido.py                 # corre los 3 casos
python polarizacion_comparacion.py     # grafica las 3 curvas juntas
```

Se puede correr un subconjunto: `python correr_ruido.py 0.6 2.2`.

**b) Barrido η = 0 → 5** — curva de polarización estacionaria vs ruido con barras de error. Para cada η del barrido (definido en `RANGO_RUIDO` al inicio de `correr_ruido.py`) se genera una serie `va(t)`, se detecta el inicio del régimen estacionario (MSER, reutilizando la lógica de `polarizacion.py`) y se calcula `⟨va⟩ ± σ` sobre esa ventana. Resultados en `build/resultados/barrido_ruido/`:

```bash
cd python
python correr_ruido.py --directorio barrido_ruido          # barrido completo (resume: saltea los que ya existen)
python polarizacion_vs_ruido.py                            # resumen CSV + gráfico con barras de error
```

Opciones útiles de `correr_ruido.py`:

| Opción | Descripción |
|--------|-------------|
| `valores_eta...` | Corre sólo esos valores (ej: `0.6 2.2 5.3`) |
| `--rango IN FIN PASO` | Usa otro rango en vez de `RANGO_RUIDO` |
| `--modelo MOD` | Modelo de interacción: `standard` (default) o `voter` |
| `--pasos N` | Pasos por corrida (default 20000) |
| `--directorio NOM` | Guarda los resultados en `build/resultados/NOM/` |
| `--forzar` | Re-corre aunque el CSV ya exista |

Salidas del estudio b): `resumen_polarizacion_vs_eta.csv` (columnas `eta, va_media, va_std, inicio_estacionario, pasos_totales`) y el gráfico `python/output/polarizacion_vs_eta.png`.

**Repetir el barrido con el modelo Voter**: cada modelo se aísla en su propio directorio para no mezclar resultados:

```bash
cd python
python correr_ruido.py --modelo voter --directorio barrido_ruido_voter
python polarizacion_vs_ruido.py --directorio barrido_ruido_voter \
    --salida polarizacion_vs_eta_voter.png \
    --titulo "Polarización estacionaria $\\langle v_a \\rangle$ vs ruido $\\eta$ (modelo Voter)"
```

`polarizacion_vs_ruido.py` acepta además `--titulo` para personalizar el título del gráfico.

## Parámetros de simulación

Los valores por defecto están definidos en `src/main.cpp` y pueden sobrescribirse con las opciones CLI de la sección Ejecución:

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `L` | 10.0 | Lado de la caja cuadrada (fijo) |
| `density` | 4 | Densidad de partículas (N = density × L²) |
| `rc` | 1.0 | Radio de interacción (fijo) |
| `r_max` | 0.0 | Radio máximo de partículas (puntuales) |
| `eta` | 0.5 | Amplitud del ruido |
| `velocity` | 0.03 | Velocidad de las partículas (fija) |
| `iterations` | 10000 | Cantidad de pasos |
| `model` | `Voter` | Modelo: `standard` (Vicsek) o `voter` |
| `seed` | 42 | Semilla de aleatoriedad |

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
│   ├── polarizacion.py
│   ├── correr_ruido.py
│   ├── polarizacion_comparacion.py
│   ├── polarizacion_vs_ruido.py
│   └── requirements.txt
├── build/
│   ├── simulador
│   └── resultados/          # Series de polarización por experimento
└── docs/
    └── TP2_Enunciado.md
```

## Output

El archivo `evolucion_dinamica.csv` tiene las columnas:

```
Time, ID, X, Y, Angle, Radius
```

Cada fila representa el estado de una partícula en un instante de tiempo.

Los CSV de experimento (`build/resultados/*.csv`) tienen en cambio un único valor por paso:

```
Time, Polarization
```

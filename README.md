# TP2 - Autómata Off-Lattice

Repositorio para el TP2 de la materia **Simulación de Sistemas** (ITBA).

Simulación de un modelo de enjambre tipo Vicsek usando un Autómata Celular Off-Lattice con método de celdas para búsqueda eficiente de vecinos.

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

Sin opciones, ejecuta 20.000 pasos con la configuración por defecto y genera `evolucion_dinamica.csv` (trayectoria completa). Los parámetros pueden sobrescribirse:

```bash
./simulador --model standard --density 4 --eta 0.6 --iterations 20000 --output resultados/mi_corrida.csv
```

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--density` | 4 | Densidad de partículas (N = density × L²) |
| `--eta` | 0.5 | Amplitud del ruido |
| `--iterations` | 20000 | Cantidad de pasos |
| `--model` | `voter` | Modelo: `standard` (Vicsek) o `voter` |
| `--seed` | 42 | Semilla de aleatoriedad |
| `--output` | *(vacío)* | CSV compacto `Time,Polarization,S` (un valor por paso) |

### Barrido de ruido

`run.py` ejecuta el binario `./simulador` por cada valor de η, generando un CSV por caso en `build/resultados/`.

```bash
cd python

# Un solo η
python run.py 0.6 --pasos 20000

# Varios η específicos
python run.py 0.6 2.2 5.3 --pasos 20000

# Barrido completo η = 0 → 5 con paso 0.25
python run.py --rango 0.0 5.0 0.25 --pasos 20000

# Barrido con modelo Standard y densidad 1
python run.py --rango 0.0 5.0 0.25 --modelo standard --density 1 --pasos 20000

# Guardar en subdirectorio (ej: para comparar modelos)
python run.py --rango 0.0 5.0 0.25 --directorio barrido_voter

# Re-corre aunque los CSVs ya existan
python run.py --rango 0.0 5.0 0.25 --forzar
```

Opciones de `run.py`:

| Opción | Descripción |
|--------|-------------|
| `valores_eta...` | Corre sólo esos valores (ej: `0.6 2.2 5.3`) |
| `--rango IN FIN PASO` | Rango de ruidos |
| `--density N` | Densidad |
| `--pasos N` | Pasos por corrida |
| `--modelo MOD` | `standard` o `voter` |
| `--directorio NOM` | Subdirectorio en `build/resultados/` |
| `--forzar` | Re-corre aunque el CSV ya exista |

### Gráficos

Todos los scripts de gráficos están en `python/plot/`. Los de tiempo usan `--input` con la ruta al CSV. Los de barrido usan `--directorio` con la carpeta de resultados.

**Evolución temporal** (para un caso individual):

```bash
cd python
python plot/polarizacion_vs_tiempo.py --input ../build/resultados/ruido_eta0.6.csv
python plot/clusters_vs_tiempo.py --input ../build/resultados/ruido_eta0.6.csv
```

**Barrido vs η** (para un directorio con múltiples η):

```bash
cd python
python plot/polarizacion_vs_eta.py
python plot/clusters_vs_eta.py
python plot/polarizacion_vs_S.py
```

`polarizacion_vs_eta.py` acepta `--directorio` repetible: cada aparición agrega una línea (una densidad) al mismo gráfico, con error bars. Sin `--directorio` grafica `rho4` por defecto.

```bash
python plot/polarizacion_vs_eta.py --directorio rho4                       # solo rho4 (default)
python plot/polarizacion_vs_eta.py --directorio rho2 --directorio rho4 --directorio rho8   # las 3 densidades superpuestas
python plot/polarizacion_vs_eta.py --directorio barrido_voter --titulo "Modelo Voter"
```

**Comparación de ruidos** (superponer curvas):

```bash
cd python
python plot/comparacion_ruido.py 0.6 2.2 5.3
```

**Animación** (requiere CSV de trayectoria completa):

```bash
cd python
python plot/animacion.py --input ../build/evolucion_dinamica.csv
```

Los gráficos se guardan en `python/output/`.

## Parámetros de simulación

Los parámetros fijos (`L = 10`, `rc = 1.0`, `velocity = 0.03`) están en `src/main.cpp` y `python/config.py`.

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `L` | 10.0 | Lado de la caja cuadrada |
| `density` | 4 | Densidad de partículas |
| `rc` | 1.0 | Radio de interacción |
| `eta` | 0.5 | Amplitud del ruido |
| `velocity` | 0.03 | Velocidad de las partículas |
| `iterations` | 20000 | Cantidad de pasos |
| `model` | `voter` | Modelo: `standard` o `voter` |
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
│   ├── config.py                    # Constantes compartidas
│   ├── utils.py                     # MSER, carga de archivos, utilidades
│   ├── run.py                       # Barrido de simulaciones
│   ├── plot/
│   │   ├── polarizacion_vs_tiempo.py    # (a) va(t)
│   │   ├── clusters_vs_tiempo.py        # (d) S(t)
│   │   ├── polarizacion_vs_eta.py       # (c) <va> ± σ vs η
│   │   ├── clusters_vs_eta.py           # (d) <S> ± σ vs η
│   │   ├── polarizacion_vs_S.py         # (e) va vs S scatter
│   │   ├── comparacion_ruido.py         # Comparación 3 ruidos
│   │   └── animacion.py                 # Animación de partículas
│   └── requirements.txt
├── build/
│   ├── simulador
│   └── resultados/          # CSVs de experimentos
└── docs/
    └── TP2_Enunciado.md
```

## Formatos de CSV

**Trayectoria completa** (`evolucion_dinamica.csv`):
```
Time,ID,X,Y,Angle,Radius
```

**Serie temporal compacta** (`build/resultados/ruido_eta*.csv`):
```
Time,Polarization,S
```

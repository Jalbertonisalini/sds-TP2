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

**Evolución temporal con 3 ruidos (punto b)** — `plot/new/`:

Los scripts nuevos viven en `python/plot/new/` para que puedas revisarlos y luego borrar los viejos. `evolucion_va_ruidos.py` superpone las curvas `va(t)` de 3 ruidos en una sola figura, marcando el inicio del estado estacionario con una línea vertical por curva. Sigue el formato de GuiaPresentaciones (sin título dentro de la figura, ejes en palabras, fuente ≥ 20).

```bash
cd python
python plot/new/evolucion_va_ruidos.py                                            # estándar (default) → standard/rho4
python plot/new/evolucion_va_ruidos.py --directorio voter/rho4                    # modelo votante (se deduce de la ruta)
```

Los `t_inicio` (instante donde comienza el estacionario) salen de `plot/new/tinicios.json` según modelo+densidad+η. Se pueden pasar manualmente por argumento para sobrescribirlos puntualmente (`eta:tinicio`):

```bash
python plot/new/evolucion_va_ruidos.py --directorio voter/rho4 0.05:1500 0.1:2000 0.5:0 --salida evolucion_va_voter.png
```

**Polarización media vs ruido (punto c)** — `plot/new/`:

`polarizacion_vs_eta.py` grafica `⟨va⟩ ± std` en función del ruido para un (o varios) directorios/densidades. La media y el desvío se calculan **desde** `t_inicio` (de `tinicios.json`), igual criterio que en (b) — sin métodos matemáticos. La leyenda muestra la **densidad** (`ρ = 2/4/8`). Sigue el formato de la guía (error bars + marcadores, ejes en palabras, fuente ≥ 20).

```bash
# 3 densidades superpuestas (una curva por densidad) para Vicsek y voter
python plot/new/polarizacion_vs_eta.py --directorio standard/rho2 --directorio standard/rho4 --directorio standard/rho8
python plot/new/polarizacion_vs_eta.py --directorio voter/rho2 --directorio voter/rho4 --directorio voter/rho8
python plot/new/polarizacion_vs_eta.py                                            # default standard/rho4
```

| Opción (b y c) | Descripción |
|--------|-------------|
| `--modelo MOD` | `standard` \| `voter`. **Opcional**: se deduce automáticamente del prefijo del directorio |
| `--directorio NOM` | Subdirectorio en `build/resultados/` (ej: `standard/rho4`, `voter/rho8`); repetible en c) |
| `--salida ARCHIVO.png` | Archivo de salida |
| `eta:tinicio` (solo b) | Sobrescribe el t_inicio de un ruido puntual |
| `--eta VALOR` (solo d-1) | Ruido de la curva S(t) (default: primer `b` del modelo) |
| `--etas V1 ...` (solo e) | Ruidos representativos de va-vs-S (default: lista `e` de tinicios.json) |

**Clusters (punto d)** — `plot/new/`:

El observable **S** (fracción de partículas en el cluster más grande) ya está en los CSVs (`Time,Polarization,S`); no hace falta simular de nuevo. `clusters_vs_tiempo.py` (d-1) grafica `S(t)` con una curva por `--directorio` — superponés la densidad alta (S≈1 siempre) con las bajas (1/π...) obligatorias. `clusters_vs_eta.py` (d-2) grafica `⟨S⟩ ± std` vs η (una curva por densidad, repetible), con el mismo criterio de estacionario que (c). Mismo formato de guía (sin título, ejes en palabras, fuente ≥ 20, error bars + marcadores).

```bash
# d-1: evolución S(t) — densidad alta + bajas
python plot/new/clusters_vs_tiempo.py --directorio standard/rho8 --directorio standard/rho0.318 --eta 0.5
# d-2: ⟨S⟩ ± std vs η — 3 densidades (o cualquier combinación)
python plot/new/clusters_vs_eta.py --directorio standard/rho2 --directorio standard/rho4 --directorio standard/rho8
python plot/new/clusters_vs_eta.py --directorio voter/rho2 --directorio voter/rho4 --directorio voter/rho8
```

**Polarización vs componente gigante (punto e)** — `plot/new/`:

`polarizacion_vs_S.py` grafica `⟨va⟩ vs ⟨S⟩` con **error bars en ambos ejes** (σ_S en x, σ_va en y), desde la ventana estacionaria. Solo usa **algunos ruidos representativos** (lista `"e"` de `tinicios.json`, sobrescribible con `--etas`), una serie por densidad. Sigue la guía (sin título, ejes en palabras, fuente ≥ 20, error bars + marcadores).

```bash
# Bajas (obligatorias) — donde va y S varían juntos
python plot/new/polarizacion_vs_S.py --directorio standard/rho0.318 --directorio standard/rho0.159 --directorio standard/rho0.106
python plot/new/polarizacion_vs_S.py --directorio voter/rho0.318 --directorio voter/rho0.159 --directorio voter/rho0.106
# Densidad alta + una baja
python plot/new/polarizacion_vs_S.py --directorio standard/rho8 --directorio standard/rho4 --directorio standard/rho0.318 --directorio standard/rho0.106
```

**Config de t_inicio (`plot/new/tinicios.json`):**

Define dónde comienza el estado estacionario (por inspección visual) por **modelo + densidad + η**. Es la única fuente de verdad para b) y c): no hay que tocar código al cambiar de modelo/densidad, solo este archivo.

```json
{
  "standard": { "b": [0.5, 1.5, 3.5], "e": [0, 0.5, 1, 2, 3, 4, 5],
                "2": { "0.5": 0, ... }, "4": { "0.5": 0, ... }, "8": { "0.5": 0, ... } },
  "voter":    { "b": [0.05, 0.1, 0.5], "e": [0, 0.05, 0.2, 0.5, 0.8, 1],
                "2": { "0.05": 0, ... }, "4": { "0.05": 0, ... }, "8": { "0.05": 0, ... } }
}
```
- `b`: lista de ruidos representativos del punto b).
- `e`: lista de ruidos representativos (pocos puntos) del punto e).
- clave `"<densidad>"` (ej. `"4"`): tabla `{eta: t_inicio}` para ese modelo y densidad.
- Un η que falte en la tabla usa `t_inicio = 0`.

**Generar los datos (simulaciones)** — organización por modelo → densidad. `run.py` genera el barrido en `build/resultados/<modelo>/rho<densidad>/`:

```bash
cd python
# Vicsek, 3 densidades (ruido 0 → 5)
python run.py --rango 0 5 0.25 --density 2 --directorio standard/rho2 --modelo standard
python run.py --rango 0 5 0.25 --density 4 --directorio standard/rho4 --modelo standard
python run.py --rango 0 5 0.25 --density 8 --directorio standard/rho8 --modelo standard
# Voter, 3 densidades (ruido 0 → 1, transición del votante a η bajos)
python run.py --rango 0 1 0.05 --density 2 --directorio voter/rho2 --modelo voter
python run.py --rango 0 1 0.05 --density 4 --directorio voter/rho4 --modelo voter
python run.py --rango 0 1 0.05 --density 8 --directorio voter/rho8 --modelo voter
```

> Nota: las densidades altas (ρ=8, N=800 partículas) tardan más por corrida.

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

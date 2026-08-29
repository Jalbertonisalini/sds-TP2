# Guía de experimentos — Punto b) y c)

Cómo correr las simulaciones y graficar los puntos **b)** y **c)**. Todos los comandos
se ejecutan desde `python/` y usan el entorno virtual (`./.venv/bin/python`).

```bash
cd python
```

Los scripts de graficado viven en `python/plot/new/`. Salen de:
- `evolucion_va_ruidos.py` → punto b)
- `polarizacion_vs_eta.py` → punto c)
- `tinicios.json` → dónde comienza el estacionario (por modelo + densidad + η)
- `config_util.py` → helper compartido

---

## Organización de los datos (`build/resultados/`)

Los barridos se guardan como `<modelo>/rho<densidad>/`:

```
build/resultados/
├── standard/rho2, rho4, rho8      # Vicsek
└── voter/rho2, rho4, rho8         # votante
```

- El **modelo** se deduce automáticamente del prefijo (`standard/...` o `voter/...`).
- La **densidad** se deduce del `rhoN` (y es la que se muestra en la leyenda de c)).

---

## 1) Generar las simulaciones (`run.py`)

```bash
# Vicsek, 3 densidades (ruido 0 → 5, paso 0.25)
./.venv/bin/python run.py --rango 0 5 0.25 --density 2 --directorio standard/rho2 --modelo standard
./.venv/bin/python run.py --rango 0 5 0.25 --density 4 --directorio standard/rho4 --modelo standard
./.venv/bin/python run.py --rango 0 5 0.25 --density 8 --directorio standard/rho8 --modelo standard

# Votante, 3 densidades (ruido 0 → 1, paso 0.05 — transición del voter a η bajos)
./.venv/bin/python run.py --rango 0 1 0.05 --density 2 --directorio voter/rho2 --modelo voter
./.venv/bin/python run.py --rango 0 1 0.05 --density 4 --directorio voter/rho4 --modelo voter
./.venv/bin/python run.py --rango 0 1 0.05 --density 8 --directorio voter/rho8 --modelo voter
```

> ρ=8 (N=800) tarda más por corrida.

---

## 2) Punto b) — evolución temporal `va(t)` con 3 ruidos

Muestra `va(t)` de los **3 ruidos representativos** (campo `"b"` de `tinicios.json`),
con una línea vertical en el inicio del estacionario de cada curva.

```bash
# Vicsek, densidad por defecto (standard/rho4)
./.venv/bin/python plot/new/evolucion_va_ruidos.py

# Otra densidad / modelo (el modelo se deduce de la ruta)
./.venv/bin/python plot/new/evolucion_va_ruidos.py --directorio standard/rho8
./.venv/bin/python plot/new/evolucion_va_ruidos.py --directorio voter/rho4

# Sobrescribir el t_inicio de ruidos puntuales (arg eta:tinicio)
./.venv/bin/python plot/new/evolucion_va_ruidos.py --directorio voter/rho4 0.05:1500 0.1:2000 0.5:0

# Renombrar salida
./.venv/bin/python plot/new/evolucion_va_ruidos.py --directorio voter/rho4 --salida b_voter.png
```

b) siempre muestra **3 curvas** (los ruidos `b` de ese modelo). La densidad se elige con
`--directorio`; no admite superponer densidades.

---

## 3) Punto c) — polarización media vs ruido `⟨va⟩ ± std`

Grafica una curva por `--directorio`. La leyenda muestra la **densidad** real (`ρ = 2/4/8`).

```bash
# Una sola densidad (una curva)
./.venv/bin/python plot/new/polarizacion_vs_eta.py --directorio standard/rho4
./.venv/bin/python plot/new/polarizacion_vs_eta.py --directorio voter/rho2
./.venv/bin/python plot/new/polarizacion_vs_eta.py          # default: standard/rho4

# 3 densidades superpuestas (una curva por densidad)
./.venv/bin/python plot/new/polarizacion_vs_eta.py --directorio standard/rho2 --directorio standard/rho4 --directorio standard/rho8 --salida c_standard_3dens.png
./.venv/bin/python plot/new/polarizacion_vs_eta.py --directorio voter/rho2 --directorio voter/rho4 --directorio voter/rho8 --salida c_voter_3dens.png

# Cualquier combinación de curvas
./.venv/bin/python plot/new/polarizacion_vs_eta.py --directorio standard/rho2 --directorio standard/rho8
```

---

## 4) Punto d) — Clusters (fracción S del cluster más grande)

El observable **S** (fracción de partículas en el cluster más grande, conectividad por rc)
ya está guardado en cada CSV de simulación (`Time,Polarization,S`) — no hace falta
simular nada nuevo. Dos scripts en `plot/new/`:

**d-1 — evolución de S(t)** (`clusters_vs_tiempo.py`): una curva S(t) por `--directorio`,
con línea vertical del inicio del estacionario. Permite superponer una densidad alta
(S≈1 siempre) con las bajas (1/π ...) que son obligatorias de mostrar.

```bash
# Alta + una baja (η=0.5)
./.venv/bin/python plot/new/clusters_vs_tiempo.py --directorio standard/rho8 --directorio standard/rho0.318 --eta 0.5
# Alta + las 3 bajas
./.venv/bin/python plot/new/clusters_vs_tiempo.py --directorio standard/rho8 --directorio standard/rho0.318 --directorio standard/rho0.159 --directorio standard/rho0.106 --eta 0.5
# Voter (modelo se deduce de la ruta), default eta = primer 'b' del modelo
./.venv/bin/python plot/new/clusters_vs_tiempo.py --directorio voter/rho8 --directorio voter/rho0.318 --eta 0.1
./.venv/bin/python plot/new/clusters_vs_tiempo.py          # default standard/rho4
```

**d-2 — ⟨S⟩ ± std vs η** (`clusters_vs_eta.py`): equivalente a c) pero con la columna S.
`--directorio` repetible → grafícás la combinación de densidades que quieras (una
curva por densidad). La media/desvío se calculan desde `t_inicio` (de `tinicios.json`).

```bash
# 3 densidades por modelo
./.venv/bin/python plot/new/clusters_vs_eta.py --directorio standard/rho2 --directorio standard/rho4 --directorio standard/rho8
./.venv/bin/python plot/new/clusters_vs_eta.py --directorio voter/rho2 --directorio voter/rho4 --directorio voter/rho8
# Con las bajas (cualquier combinación)
./.venv/bin/python plot/new/clusters_vs_eta.py --directorio standard/rho0.318 --directorio standard/rho0.159 --directorio standard/rho0.106
./.venv/bin/python plot/new/clusters_vs_eta.py          # default standard/rho4
```

> La leyenda muestra la densidad real: `ρ = 8`, `ρ = 1/π`, `ρ = 1/(2π)`, `ρ = 1/(3π)`.

## 5) Punto e) — Polarización vs componente gigante (va vs S)

`polarizacion_vs_S.py` grafica **⟨va⟩ vs ⟨S⟩** con **error bars en ambos ejes**
(x = σ_S, y = σ_va), ambos calculados en la ventana estacionaria (desde `t_inicio`).
Solo usa **algunos ruidos representativos** (no todo el barrido): la lista `"e"` de
`tinicios.json` (standard `[0,0.5,1,2,3,4,5]`, voter `[0,0.05,0.2,0.5,0.8,1]`),
sobrescribible con `--etas`. Una serie por densidad (color), leyenda con la densidad real.

```bash
# Bajas (obligatorias) — es donde va y S varían juntos y el scatter se extiende
./.venv/bin/python plot/new/polarizacion_vs_S.py --directorio standard/rho0.318 --directorio standard/rho0.159 --directorio standard/rho0.106
./.venv/bin/python plot/new/polarizacion_vs_S.py --directorio voter/rho0.318 --directorio voter/rho0.159 --directorio voter/rho0.106
# Densidad alta + bajas de una
./.venv/bin/python plot/new/polarizacion_vs_S.py --directorio standard/rho8 --directorio standard/rho4 --directorio standard/rho0.318 --directorio standard/rho0.106
# Ruidos representativos a mano
./.venv/bin/python plot/new/polarizacion_vs_S.py --directorio standard/rho0.318 --etas 0 1 2 3 4 5
./.venv/bin/python plot/new/polarizacion_vs_S.py          # default standard/rho4
```

> A densidades altas (ρ=4/8) S≈1 para todo η → los puntos se agrupan en vertical
> (hay componente gigante casi siempre); en las bajas va y S caen juntos con η.

## Opciones comunes

| Opción | Descripción |
|--------|-------------|
| `--modelo MOD` | `standard` \| `voter`. **Opcional**: se deduce del prefijo del directorio |
| `--directorio NOM` | Subdirectorio en `build/resultados/` (ej: `standard/rho4`, `voter/rho8`) |
| `--salida ARCHIVO.png` | Nombre/path del PNG (sin path → `python/output/`) |
| `eta:tinicio` (solo b) | Sobrescribe el t_inicio de un ruido puntual |
| `--eta VALOR` (solo d-1) | Ruido de la curva S(t) (default: primer `b` del modelo) |
| `--etas V1 V2 ...` (solo e) | Ruidos representativos de va-vs-S (default: lista `e` de tinicios.json) |

## Salida de los gráficos

- Sin `--salida` → `python/output/` con el nombre por defecto.
- `--salida mi_nombre.png` → `python/output/mi_nombre.png`.
- `--salida /ruta/absoluta.png` → exactamente ahí.

## Config del estacionario (`plot/new/tinicios.json`)

`t_inicio` (criterio por inspección visual, sin método matemático) por **modelo + densidad + η**.
Es la única fuente de verdad para b) y c). Si un η falta en la tabla, usa `t_inicio = 0`.

```json
{
  "standard": { "b": [0.5, 1.5, 3.5],
                "2": { "0.5": 0, ... }, "4": { "0.5": 0, ... }, "8": { "0.5": 0, ... } },
  "voter":    { "b": [0.05, 0.1, 0.5],
                "2": { "0.05": 0, ... }, "4": { "0.05": 0, ... }, "8": { "0.05": 0, ... } }
}
```

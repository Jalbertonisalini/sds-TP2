# Parámetros de los experimentos

Documento que acompaña a las figuras de `entrega/`. Las figuras **no llevan título ni
leyenda** (según GuiaPresentaciones), así que acá se detallan las condiciones de
simulación y qué muestra cada una.

---

## 1. Parámetros fijos del simulador

| Parámetro | Valor |
|-----------|-------|
| Caja | L = 10 (lado), condiciones periódicas |
| Radio de interacción | rc = 1.0 |
| Velocidad de las partículas | v = 0.03 |
| Ruido | angular, uniforme en `[−η/2, +η/2]` |
| Pasos por corrida | 20000 (t = 0 … 20000) |
| Semilla | fija `42` |
| Corridas por (modelo, ρ, η) | **1** (una sola realización; sin promediar semillas) |

## 2. Modelos

- **standard (Vicsek)**: cada partícula adopta el **promedio** de las direcciones de
  sus vecinos (dentro de rc) más el ruido η.
- **voter**: cada partícula **copia la dirección de un vecino elegido al azar** más el
  ruido η (envuelto a `[−π, π]`).

## 3. Densidades → número de partículas N

N = int(ρ · L²), con L = 10 → N = int(ρ · 100):

| Densidad ρ | N |
|-----------|----|
| 2 | 200 |
| 4 | 400 |
| 8 | 800 |
| 1/π ≈ 0.318 | 31 |
| 1/(2π) ≈ 0.159 | 15 |
| 1/(3π) ≈ 0.106 | 10 |

## 4. Barridos de ruido η

- **standard**: η ∈ {0, 0.25, 0.5, …, 5.0} (21 valores, paso 0.25).
- **voter**: η ∈ {0, 0.05, 0.1, …, 1.0} (21 valores, paso 0.05).

## 5. Observables (por paso, guardados en cada CSV `Time,Polarization,S`)

- **Polarización** `va = |Σ u_i| / N` (módulo del promedio de vectores unitarios).
- **S** = fracción de partículas en el **cluster más grande** (componente conexa por rc) = tamaño_cluster/N.

## 6. Criterio de estacionario (promediado)

La media y el desvío de cada observable se calculan **desde el instante `t_inicio`**
hasta el final (20000), donde `t_inicio` es el comienzo del estado estacionario
(file: `python/plot/new/tinicios.json`, fijado **por inspección visual**, sin método matemático).

> **Nota:** `t_inicio` se puede ajustar manualmente en `tinicios.json` si se observa
> algo distinto. La media y el desvío se recalculan **desde ese instante**, sin tocar
> código. Si un η no tiene entrada, se usa `t_inicio = 0` (promedio sobre toda la serie).

Valores no nulos actuales por (modelo, densidad, η):

| Modelo | Densidad | η | t_inicio |
|--------|----------|----|----------|
| standard | 4 | 1.0 | 1000 |
| standard | 4 | 1.5 | 8000 |
| voter | 0.318 (1/π) | 0.1 | 2000 |

El resto usa `t_inicio = 0`.

## 7. Figuras y qué muestran

> Las **barras de error** son la fluctuación temporal del observable dentro del estado
> estacionario de la **única** corrida (no dispersión entre réplicas). En la figura e)
> las barras se recortan al dominio físico [0, 1] (una fracción no puede superar 1).

### b) Evolución temporal de la polarización `va(t)` — 3 ruidos representativos

Curvas `va(t)` para 3 ruidos, con la línea vertical del inicio del estacionario de cada una.

| Archivo | Modelo | Densidad | Ruidos (η) |
|---------|--------|----------|------------|
| `evolucion_va_ruidos.png` | standard | 4 | 0.5, 1.5, 3.5 |
| `evolucion_va_voter.png` | voter | 4 | 0.05, 0.1, 0.5 |

### c) Polarización media vs ruido `⟨va⟩ ± σ` (todo el barrido)

Una curva por densidad.

| Archivo | Modelo | Densidades |
|---------|--------|------------|
| `c_standard_3dens.png` | standard | 2, 4, 8 |
| `c_voter_3dens.png` | voter | 2, 4, 8 |
| `c_standard_lowdens.png` | standard | 1/π (0.318), 1/(2π) (0.159), 1/(3π) (0.106) |
| `c_voter_lowdens.png` | voter | 1/π (0.318), 1/(2π) (0.159), 1/(3π) (0.106) |

### d-1) Evolución de la fracción del cluster más grande `S(t)`

Curvas `S(t)` para ρ=8 (donde hay componente gigante casi siempre) y ρ=0.318 (1/π, baja).
Con la línea vertical del inicio del estacionario.

| Archivo | Modelo | Densidades | η |
|---------|--------|------------|----|
| `d1_standard_8_vs_low.png` | standard | 8 y 0.318 | 0.5 |
| `d1_voter_8_vs_low.png` | voter | 8 y 0.318 | 0.1 |

### d-2) Fracción del cluster más grande media vs ruido `⟨S⟩ ± σ` (todo el barrido)

| Archivo | Modelo | Densidades |
|---------|--------|------------|
| `d2_standard_8_vs_low.png` | standard | 8 y 0.318 |
| `d2_voter_8_vs_low.png` | voter | 8 y 0.318 |

### e) Polarización vs componente gigante `⟨va⟩ vs ⟨S⟩`

Puntos representativos (no todo el barrido) con **desvío en ambos ejes** (σ en x = ⟨S⟩,
σ en y = ⟨va⟩), una serie por densidad. Ruidos representativos de la lista `e`:

- standard: η ∈ {0, 1, 2, 5}
- voter: η ∈ {0.05, 0.4, 1}

| Archivo | Modelo | Densidades |
|---------|--------|------------|
| `e_standard_8_vs_low.png` | standard | 8 y 0.318 |
| `e_voter_8_vs_low.png` | voter | 8 y 0.318 |

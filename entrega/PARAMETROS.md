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
| standard | 4 | 0.5 | 500 |
| standard | 4 | 1.0 | 1000 |
| standard | 4 | 1.5 | 8000 |
| standard | 4 | 3.5 | 500 |
| standard | 8 | 0.5 | 500 |
| standard | 2 | 0.5 | 500 |
| standard | 0.318 (1/π) | 0.5 | 1000 |
| voter | 2 | 0.1 | 1000 |
| voter | 4 | 0.05 | 1000 |
| voter | 4 | 0.1 | 1500 |
| voter | 4 | 0.5 | 500 |
| voter | 8 | 0.1 | 3000 |
| voter | 0.318 (1/π) | 0.1 | 2000 |

El resto usa `t_inicio = 0`. Las filas nuevas (todas menos las 3 originales) se agregaron
al sumar las figuras "4 vs low" y las versiones a 30000 pasos — mismo criterio visual,
mismo valor para ambas duraciones (el tiempo de relajación es una propiedad física, no
depende de cuánto dure la corrida completa).

## 7. Figuras y qué muestran

> Las **barras de error** son la fluctuación temporal del observable dentro del estado
> estacionario de la **única** corrida (no dispersión entre réplicas). Se recortan al
> dominio físico [0, 1] (una fracción/polarización no puede superar 1) en **todas** las
> figuras con barras (c, d-2, e) — antes solo se recortaba en algunas y se veían barras
> pasándose de 1 (ej. la versión vieja de `c/c_voter_lowdens.png`); ya está corregido en
> `polarizacion_vs_eta.py` también.
>
> En las figuras con ruido η de 0 a 5 (modelo **standard**), se agregaron líneas grises
> punteadas verticales en η = 0.5, 1.5, 2.5, 3.5, 4.5 como referencia, con el valor
> numérico también en gris debajo del eje. No aplica al modelo voter (rango de η
> distinto, 0 a 1).
>
> Todas las figuras originales (20000 pasos) se conservaron sin tocar. Las nuevas
> variantes —con densidad **2 o 4 vs low** (además de 8 vs low) y/o **30000 pasos**
> (además de 20000)— se agregaron con nombres nuevos, listadas junto a cada figura
> original. `b/evolucion_va_voter_30000.png` muestra solo η = 0.05 y 0.5 (se sacó 0.1 a
> pedido); `c/c_voter_lowdens_30000.png` muestra solo 1/π y 1/(3π) (se sacó 1/(2π)).

### b) Evolución temporal de la polarización `va(t)` — 3 ruidos representativos

Curvas `va(t)` para 3 ruidos, con la línea vertical del inicio del estacionario de cada una.

| Archivo | Modelo | Densidad | Ruidos (η) | Pasos |
|---------|--------|----------|------------|-------|
| `b/evolucion_va_ruidos.png` | standard | 4 | 0.5, 1.5, 3.5 | 20000 |
| `b/evolucion_va_voter.png` | voter | 4 | 0.05, 0.1, 0.5 | 20000 |
| `b/evolucion_va_ruidos_30000.png` | standard | 4 | 0.5, 1.5, 3.5 | 30000 |
| `b/evolucion_va_voter_30000.png` | voter | 4 | 0.05, 0.5 | 30000 |

### c) Polarización media vs ruido `⟨va⟩ ± σ` (todo el barrido)

Una curva por densidad.

| Archivo | Modelo | Densidades | Pasos |
|---------|--------|------------|-------|
| `c/c_standard_3dens.png` | standard | 2, 4, 8 | 20000 |
| `c/c_voter_3dens.png` | voter | 2, 4, 8 | 20000 |
| `c/c_standard_lowdens.png` | standard | 1/π (0.318), 1/(2π) (0.159), 1/(3π) (0.106) | 20000 |
| `c/c_voter_lowdens.png` | voter | 1/π (0.318), 1/(2π) (0.159), 1/(3π) (0.106) | 20000 |
| `c/c_standard_3dens_30000.png` | standard | 2, 4, 8 | 30000 |
| `c/c_voter_3dens_30000.png` | voter | 2, 4, 8 | 30000 |
| `c/c_standard_lowdens_30000.png` | standard | 1/π, 1/(2π), 1/(3π) | 30000 |
| `c/c_voter_lowdens_30000.png` | voter | 1/π, 1/(3π) | 30000 |

### d-1) Evolución de la fracción del cluster más grande `S(t)`

Curvas `S(t)` para una densidad alta (8, 4 o 2) y ρ=0.318 (1/π, baja). Con la línea
vertical del inicio del estacionario.

| Archivo | Modelo | Densidades | η | Pasos |
|---------|--------|------------|----|-------|
| `d1/d1_standard_8_vs_low.png` | standard | 8 y 0.318 | 0.5 | 20000 |
| `d1/d1_voter_8_vs_low.png` | voter | 8 y 0.318 | 0.1 | 20000 |
| `d1/d1_standard_4_vs_low.png` | standard | 4 y 0.318 | 0.5 | 20000 |
| `d1/d1_voter_4_vs_low.png` | voter | 4 y 0.318 | 0.1 | 20000 |
| `d1/d1_standard_2_vs_low.png` | standard | 2 y 0.318 | 0.5 | 20000 |
| `d1/d1_voter_2_vs_low.png` | voter | 2 y 0.318 | 0.1 | 20000 |
| `d1/d1_standard_8_vs_low_30000.png` | standard | 8 y 0.318 | 0.5 | 30000 |
| `d1/d1_standard_4_vs_low_30000.png` | standard | 4 y 0.318 | 0.5 | 30000 |
| `d1/d1_standard_2_vs_low_30000.png` | standard | 2 y 0.318 | 0.5 | 30000 |
| `d1/d1_voter_8_vs_low_30000.png` | voter | 8 y 0.318 | 0.1 | 30000 |
| `d1/d1_voter_4_vs_low_30000.png` | voter | 4 y 0.318 | 0.1 | 30000 |
| `d1/d1_voter_2_vs_low_30000.png` | voter | 2 y 0.318 | 0.1 | 30000 |

### d-2) Fracción del cluster más grande media vs ruido `⟨S⟩ ± σ` (todo el barrido)

| Archivo | Modelo | Densidades | Pasos |
|---------|--------|------------|-------|
| `d2/d2_standard_8_vs_low.png` | standard | 8 y 0.318 | 20000 |
| `d2/d2_voter_8_vs_low.png` | voter | 8 y 0.318 | 20000 |
| `d2/d2_standard_4_vs_low.png` | standard | 4 y 0.318 | 20000 |
| `d2/d2_voter_4_vs_low.png` | voter | 4 y 0.318 | 20000 |
| `d2/d2_standard_2_vs_low.png` | standard | 2 y 0.318 | 20000 |
| `d2/d2_voter_2_vs_low.png` | voter | 2 y 0.318 | 20000 |
| `d2/d2_standard_8_vs_low_30000.png` | standard | 8 y 0.318 | 30000 |
| `d2/d2_standard_4_vs_low_30000.png` | standard | 4 y 0.318 | 30000 |
| `d2/d2_standard_2_vs_low_30000.png` | standard | 2 y 0.318 | 30000 |
| `d2/d2_voter_8_vs_low_30000.png` | voter | 8 y 0.318 | 30000 |
| `d2/d2_voter_4_vs_low_30000.png` | voter | 4 y 0.318 | 30000 |
| `d2/d2_voter_2_vs_low_30000.png` | voter | 2 y 0.318 | 30000 |

### e) Polarización vs componente gigante `⟨va⟩ vs ⟨S⟩`

Puntos representativos (no todo el barrido) con **desvío en ambos ejes** (σ en x = ⟨S⟩,
σ en y = ⟨va⟩), una serie por densidad. Ruidos representativos de la lista `e`:

- standard: η ∈ {0, 1, 2, 5}
- voter: η ∈ {0.05, 0.4, 1}

| Archivo | Modelo | Densidades | Pasos |
|---------|--------|------------|-------|
| `e/e_standard_8_vs_low.png` | standard | 8 y 0.318 | 20000 |
| `e/e_voter_8_vs_low.png` | voter | 8 y 0.318 | 20000 |
| `e/e_standard_4_vs_low.png` | standard | 4 y 0.318 | 20000 |
| `e/e_voter_4_vs_low.png` | voter | 4 y 0.318 | 20000 |
| `e/e_standard_2_vs_low.png` | standard | 2 y 0.318 | 20000 |
| `e/e_voter_2_vs_low.png` | voter | 2 y 0.318 | 20000 |
| `e/e_standard_8_vs_low_30000.png` | standard | 8 y 0.318 | 30000 |
| `e/e_standard_4_vs_low_30000.png` | standard | 4 y 0.318 | 30000 |
| `e/e_standard_2_vs_low_30000.png` | standard | 2 y 0.318 | 30000 |
| `e/e_voter_8_vs_low_30000.png` | voter | 8 y 0.318 | 30000 |
| `e/e_voter_4_vs_low_30000.png` | voter | 4 y 0.318 | 30000 |
| `e/e_voter_2_vs_low_30000.png` | voter | 2 y 0.318 | 30000 |

### g) Tiempos de ejecución del CIM vs TP1

`g/g_cim_vs_tp1.png` — tiempo de un pase completo del CIM (armar grilla + resolver
vecinos de todas las partículas, sobre una configuración estática, sin evolucionar la
simulación) en función de N, comparando el CIM a la misma **cantidad de partículas**
que el barrido del TP1, dos series.

**Ambas series miden el MISMO kernel compartido** (`cim_tp1_bench/include/
cell_index_method_shared.hpp`): algoritmo del CIM de `SDS-TP1/source/java/
CellIndexMethod.java` (grilla M×M, 4 direcciones vecinas + celda propia, cada par
evaluado una sola vez), con arrays planos `head`/`next` reutilizados entre corridas
(sin `unordered_set` ni contenedores nuevos por llamada). La única diferencia entre
las series es la geometría de la caja (L y M):

- **TP1**: L=20, M=13 (barrido original de TP1, Tarea 4.1), rc=1, PBC.
- **TP2**: L=10, M=10 (óptimo, `floor(L/(rc+2·r_max))`), rc=1, PBC.

Ambas series con el mismo esquema de medición que `NBenchmark.java` (TP1): lotes
(batch) de 100 corridas por toma de tiempo, muestras adaptativas (3000 lotes si
N≤200, 30 si N>200), media y desvío sobre esas muestras.

Se comparan a igual N (no a igual densidad): el tiempo del CIM escala con la cantidad
de partículas, así que a igual densidad en cajas distintas (L=20 vs L=10) TP1 tendría
4× las partículas para la misma ρ, ocultando el costo real por partícula. La diferencia
(ambas usan el mismo código) queda entonces explicada solo por la geometría: distinta
cantidad de celdas (169 vs 100) y distinto tamaño de celda (1.54 vs 1.0), que cambian
cuántos pares por celda se evalúan para un mismo N.

| Serie | N medidos |
|-------|-----------|
| TP1 | 10, 25, 50, 100, 200, 350, 400, 500, 650, 800, 900, 1000 (barrido original de TP1, Tarea 4.1) |
| TP2 | 10, 25, 50, 100, 200, 350, 400, 500, 650, 800, 900, 1000 (los mismos N) |

> El CIM no depende del modelo (standard/voter comparten build + búsqueda de
> vecinos), así que alcanza con una corrida por N.

import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR

# Punto g): tiempos de ejecución del CIM en función de N, comparando:
#   - TP1: algoritmo del CIM de TP1 (Java) portado a C++, pensado desde el diseño
#     para C++ (estructuras reutilizadas entre corridas, ver
#     cim_tp1_bench/include/cell_index_method_reusable.hpp)
#   - TP2: CIM real de TP2 (arrays planos, build/resultados/cim_timing_tp2.csv)
# Log-log porque N y tiempo abarcan ~2 décadas cada uno.

FUENTE = 20
TAM_FIG = (13, 6)
COLORES = ["#1f77b4", "#ff7f0e", "#2ca02c"]

PUERTO_CSV = Path(__file__).resolve().parent.parent.parent.parent.parent / "sds-TP2" / "cim_tp1_bench" / "output" / "n_benchmark_cpp.csv"
TP2_CSV = RESULTADOS / "cim_timing_tp2.csv"

SERIES = [
    ("TP1", PUERTO_CSV, "libre_cpp"),
    ("TP2", TP2_CSV, "tp2"),
]


def leer_serie(ruta, regimen):
    ns, medias, stds = [], [], []
    with open(ruta) as f:
        for row in csv.DictReader(f):
            if row["regimen"] != regimen:
                continue
            ns.append(int(row["N"]))
            medias.append(float(row["time_mean_ms"]))
            stds.append(float(row["time_std_ms"]))
    orden = sorted(range(len(ns)), key=lambda i: ns[i])
    return [ns[i] for i in orden], [medias[i] for i in orden], [stds[i] for i in orden]


def graficar(archivo_salida=None):
    fig, ax = plt.subplots(figsize=TAM_FIG)
    fig.subplots_adjust(bottom=0.16, left=0.10)

    for (etiqueta, ruta, regimen), color in zip(SERIES, COLORES):
        if not ruta.exists():
            print(f"Aviso: falta {ruta}, se omite '{etiqueta}'")
            continue
        ns, medias, stds = leer_serie(ruta, regimen)
        ax.errorbar(ns, medias, yerr=stds, fmt="o-", capsize=3, linewidth=1.6,
                    markersize=6, color=color, label=etiqueta)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Partículas", fontsize=FUENTE)
    ax.set_ylabel("tiempo (ms)", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.legend(loc="upper left", fontsize=FUENTE - 4)
    ax.grid(alpha=0.3, which="both")

    # Líneas punteadas bajando desde los N de TP2 (las densidades reales del TP:
    # rho=2,4,8 -> 200,400,800, y las bajas en fracciones de pi -> 10,15,31) para
    # ubicarlas sobre la escala logarítmica sin reemplazar los ticks de potencias de 10.
    if TP2_CSV.exists():
        ns_tp2, _, _ = leer_serie(TP2_CSV, "tp2")
        trans = ax.get_xaxis_transform()
        for n in ns_tp2:
            if math.log10(n) % 1 == 0:
                continue  # coincide con un tick de potencia de 10 (ej. 10), ya está marcado
            ax.axvline(n, color="gray", linestyle=":", linewidth=1, alpha=0.6)
            ax.text(n, -0.03, str(n), transform=trans, ha="center", va="top", fontsize=FUENTE - 8, color="gray")

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "g_cim_vs_tp1.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


if __name__ == "__main__":
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    graficar(salida)

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR

# Punto g): tiempos de ejecución del CIM en función del NÚMERO DE PARTÍCULAS (N),
# comparando el CIM a los mismos N que el barrido del TP1:
#   - TP1: algoritmo del CIM de TP1 (Java) portado a C++, L=20 (M=13, ver
#     cim_tp1_bench/output/n_benchmark_cpp.csv)
#   - TP2: CIM real de TP2 (L=10, M optimo, build/resultados/cim_timing_tp2.csv)
# Ambas series miden el MISMO kernel compartido (cim_tp1_bench/include/
# cell_index_method_shared.hpp); solo difiere la geometría de la caja (L, M).
# Ambos conjuntos comparten los mismos valores de N, así que se superponen en el eje x.
# Se compara a igual N (no a igual densidad) porque el tiempo del CIM escala con la
# cantidad de partículas; a igual densidad en cajas distintas (L=20 vs L=10) TP1
# tendría 4x particulas, que escondería el costo real.
# Escala doble logarítmica porque N y tiempo abarcan varios ordenes de magnitud.

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
    """Devuelve (ns, medias, stds) ordenados por N desde las columnas del CSV."""
    ns, medias, stds = [], [], []
    with open(ruta) as f:
        for row in csv.DictReader(f):
            if row["regimen"] != regimen:
                continue
            ns.append(float(row["N"]))
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

    # Estilo de los gráficos d2: línea vertical punteada gris de referencia y valor
    # gris rotulado en el borde inferior del eje, en algunos N representativos.
    etiquetar_ns = {25, 50, 200, 350, 500, 650, 800}
    trans = ax.get_xaxis_transform()
    for n in etiquetar_ns:
        ax.axvline(n, color="gray", linestyle=":", linewidth=1, alpha=0.6)
        ax.text(n, -0.06, str(int(n)), transform=trans, ha="center", va="top",
                fontsize=FUENTE - 8, color="gray")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Partículas", fontsize=FUENTE)
    ax.set_ylabel("tiempo (ms)", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.legend(loc="upper left", fontsize=FUENTE - 4)
    ax.grid(alpha=0.3, which="both")

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "g_cim_vs_tp1.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


if __name__ == "__main__":
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    graficar(salida)

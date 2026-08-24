import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import detectar_inicio_estacionario
from config import OUTPUT_DIR


def graficar(archivo_csv, archivo_salida=None):
    df = pd.read_csv(archivo_csv)
    t = df["Time"].to_numpy()
    S = df["S"].to_numpy()

    idx_inicio, hay_transiente = detectar_inicio_estacionario(t, S)
    S_media = S[idx_inicio:].mean()
    S_std = S[idx_inicio:].std()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, S, color="#1f77b4", linewidth=0.8, label="$S(t)$")

    if hay_transiente:
        t_inicio = t[idx_inicio]
        ax.axvline(t_inicio, color="red", linestyle="--", linewidth=1.2,
                   label=f"Inicio estacionario (t={t_inicio})")

    ax.axhline(S_media, color="green", linestyle=":", linewidth=1,
               label=f"$\\langle S \\rangle$ = {S_media:.3f} ± {S_std:.3f}")

    ax.set_xlabel("Tiempo (pasos)")
    ax.set_ylabel("Fracción del cluster más grande $S$")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"Evolución de $S$ — {Path(archivo_csv).stem}")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    fig.tight_layout()

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "clusters_vs_tiempo.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")
    print(f"S = {S_media:.4f} ± {S_std:.4f}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("Uso: python plot/clusters_vs_tiempo.py --input ARCHIVO_CSV [--salida archivo.png]")
        sys.exit(0)

    archivo = None
    salida = None
    i = 0
    while i < len(args):
        if args[i] == "--input":
            i += 1
            archivo = args[i]
        elif args[i] == "--salida":
            i += 1
            salida = args[i]
        elif not args[i].startswith("-"):
            archivo = args[i]
        i += 1

    if not archivo:
        print("Error: falta --input ARCHIVO_CSV")
        sys.exit(1)
    graficar(archivo, salida)

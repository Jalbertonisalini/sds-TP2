import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RESULTADOS, OUTPUT_DIR


def graficar(archivos_eta, archivo_salida=None):
    """graficar: dict {eta: ruta_csv}"""
    fig, ax = plt.subplots(figsize=(10, 5))

    for eta, ruta in sorted(archivos_eta.items()):
        df = pd.read_csv(ruta)
        t = df["Time"].to_numpy()
        va = df["Polarization"].to_numpy()
        ax.plot(t, va, linewidth=0.8, label=f"$\\eta={eta}$")

    ax.set_xlabel("Tiempo (pasos)")
    ax.set_ylabel("Polarización $v_a$")
    ax.set_ylim(0, 1.05)
    ax.set_title("Comparación de polarización para distintos ruidos")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "comparacion_ruido.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("Uso: python plot/comparacion_ruido.py eta1 eta2 eta3 [--directorio DIR]")
        sys.exit(0)

    if not args:
        print("Error: pasá al menos un valor de eta")
        sys.exit(1)

    etas = []
    directorio = RESULTADOS
    i = 0
    while i < len(args):
        if args[i] == "--directorio":
            i += 1
            directorio = RESULTADOS / args[i]
        elif not args[i].startswith("-"):
            etas.append(float(args[i]))
        i += 1

    archivos = {}
    for eta in etas:
        ruta = directorio / f"ruido_eta{eta}.csv"
        if not ruta.exists():
            print(f"Error: No existe {ruta}")
            sys.exit(1)
        archivos[eta] = ruta

    graficar(archivos)

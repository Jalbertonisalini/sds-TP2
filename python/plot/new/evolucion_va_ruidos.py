import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR


# (eta, t_inicio) por defecto para el modelo estándar.
# t_inicio se determina por inspección visual (sin método matemático):
# es el instante en que la curva deja de tender y fluctúa alrededor de
# un valor constante.
DEFAULT_CASOS = [
    (0.5, 4000),
    (2.0, 5000),
    (5.0, 0),
]

FUENTE = 20
TAM_FIG = (13, 6)


def graficar(casos, archivo_salida=None):
    """casos: lista de (eta, t_inicio). Dibuja va(t) para cada eta con una
    linea vertical en el inicio del estacionario."""
    fig, ax = plt.subplots(figsize=TAM_FIG)
    fig.subplots_adjust(bottom=0.16, left=0.10)

    colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for (eta, t_inicio), color in zip(casos, colores):
        ruta = RESULTADOS / f"ruido_eta{eta}.csv"
        df = pd.read_csv(ruta)
        t = df["Time"].to_numpy()
        va = df["Polarization"].to_numpy()
        ax.plot(t, va, color=color, linewidth=1.8, label=f"$\\eta={eta}$")
        ax.axvline(t_inicio, color=color, linestyle="--", linewidth=1.6, alpha=0.7)

    ax.set_xlabel("Pasos", fontsize=FUENTE)
    ax.set_ylabel("Va", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right", fontsize=FUENTE)
    ax.grid(alpha=0.3)

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "evolucion_va_ruidos.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


def imprimir_uso():
    print(
        "Uso: python plot/new/evolucion_va_ruidos.py [eta:tinicio ...] [opciones]\n"
        "Sin argumentos usa los defaults (standard): "
        + " ".join(f"{eta}:{tin}" for eta, tin in DEFAULT_CASOS)
        + "\n\n"
        "  eta:tinicio     Ruido eta y tiempo de inicio del estacionario (repetible).\n"
        "                  t_inicio se fija por inspección visual: cuando la curva\n"
        "                  deja de tender y fluctúa alrededor de un valor constante.\n"
        "  --directorio NOM  Subdirectorio en build/resultados (default: raíz)\n"
        "  --salida ARCHIVO.png  Archivo de salida\n"
        "  -h, --help       Mostrar esta ayuda"
    )


def parsear_args(argv):
    casos = []
    directorio = ""
    salida = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            imprimir_uso()
            sys.exit(0)
        elif arg == "--directorio":
            i += 1
            directorio = argv[i]
        elif arg == "--salida":
            i += 1
            salida = argv[i]
        elif arg.startswith("-"):
            raise ValueError(f"opción desconocida: {arg}")
        elif ":" in arg:
            eta_str, tin_str = arg.split(":")
            casos.append((float(eta_str), int(tin_str)))
        else:
            casos.append((float(arg), 0))
        i += 1

    if not casos:
        casos = list(DEFAULT_CASOS)

    return casos, directorio, salida


if __name__ == "__main__":
    global RESULTADOS
    try:
        casos, directorio, salida = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    if directorio:
        RESULTADOS = RESULTADOS / directorio

    archivo_salida = (OUTPUT_DIR / salida) if (salida and "/" not in salida) else salida
    graficar(casos, archivo_salida)

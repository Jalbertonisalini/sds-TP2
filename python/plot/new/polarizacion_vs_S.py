import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR
from config_util import (t_inicio_para, densidad_de_directorio, cargar_tinicios,
                         modelo_de_directorio, etiqueta_densidad, etas_e_para)


FUENTE = 20
TAM_FIG = (13, 6)


def resumir_etas(directorio, modelo, etas):
    """Para cada eta representativo, media y desvio de va y S en el estacionario
    (desde t_inicio). Devuelve listas paralelas para graficar con errorbars."""
    tinicios = cargar_tinicios()
    densidad = densidad_de_directorio(directorio)

    xs, xs_err, ys, ys_err = [], [], [], []
    for eta in etas:
        ruta = RESULTADOS / directorio / f"ruido_eta{float(eta)}.csv"
        if not ruta.exists():
            print(f"Error: no existe {ruta}")
            sys.exit(1)
        df = pd.read_csv(ruta)
        t = df["Time"].to_numpy()
        t_inicio = t_inicio_para(modelo, densidad, eta, tinicios)
        idx = int((t >= t_inicio).argmax()) if len(t) else 0
        va = df["Polarization"].to_numpy()[idx:]
        S = df["S"].to_numpy()[idx:]
        xs.append(S.mean())
        xs_err.append(S.std())
        ys.append(va.mean())
        ys_err.append(va.std())
    return xs, xs_err, ys, ys_err


def clamp_err(centers, errs, lo=0.0, hi=1.0):
    """Recorta barras de error simétricas al dominio físico [lo, hi] (fracciones).
    Devuelve (err_inferior, err_superior) asimétricos para que las barras no
    sobrepasen lo/hi (ej. x > 1 en una fracción, que es imposible)."""
    lo_err, hi_err = [], []
    for x, e in zip(centers, errs):
        lo_err.append(max(0.0, min(e, x - lo)))
        hi_err.append(max(0.0, min(e, hi - x)))
    return lo_err, hi_err


def graficar(directorios, modelo, etas, archivo_salida=None):
    fig, ax = plt.subplots(figsize=TAM_FIG)
    fig.subplots_adjust(bottom=0.16, left=0.14)

    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for directorio, color in zip(directorios, colores):
        xs, xs_err, ys, ys_err = resumir_etas(directorio, modelo, etas)
        x_lo, x_hi = clamp_err(xs, xs_err)
        y_lo, y_hi = clamp_err(ys, ys_err)
        ax.errorbar(
            xs, ys, xerr=[x_lo, x_hi], yerr=[y_lo, y_hi],
            fmt="o-", capsize=3, linewidth=1.2, markersize=5, color=color,
            label=f"$\\rho={etiqueta_densidad(densidad_de_directorio(directorio))}$",
        )

    ax.set_xlabel("Fracción de la componente gigante", fontsize=FUENTE)
    ax.set_ylabel("Polarización", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best", fontsize=FUENTE)
    ax.grid(alpha=0.3)

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "polarizacion_vs_S.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


def imprimir_uso():
    print(
        "Uso: python plot/new/polarizacion_vs_S.py [opciones]\n"
        "Sin --directorio grafica standard/rho4 (default).\n\n"
        "  --directorio NOM   build/resultados/NOM/ (repetible: una serie por densidad)\n"
        "                     Ej: standard/rho2 standard/rho8 voter/rho0.318\n"
        "  --modelo MOD       standard | voter (default: se deduce de la ruta)\n"
        "  --etas V1 V2 ...   Ruidos representativos (default: lista 'e' de tinicios.json)\n"
        "  --salida ARCHIVO.png  Grafico de salida\n"
        "  -h, --help         Mostrar esta ayuda"
    )


def parsear_args(argv):
    directorios = []
    modelo = "standard"
    modelo_dado = False
    etas = None
    salida = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            imprimir_uso()
            sys.exit(0)
        elif arg == "--directorio":
            i += 1
            directorios.append(argv[i])
        elif arg == "--modelo":
            i += 1
            modelo = argv[i]
            modelo_dado = True
        elif arg == "--etas":
            rest = argv[i + 1:]
            etas = []
            for a in rest:
                if a.startswith("-"):
                    break
                etas.append(float(a))
            i += len(etas)
        elif arg == "--salida":
            i += 1
            salida = argv[i]
        else:
            raise ValueError(f"opción desconocida: {arg}")
        i += 1

    if not directorios:
        directorios = ["standard/rho4"]

    if not modelo_dado:
        derivado = modelo_de_directorio(directorios[0])
        if derivado:
            modelo = derivado

    if etas is None:
        tinicios = cargar_tinicios()
        etas = etas_e_para(modelo, tinicios)

    return directorios, modelo, etas, salida


if __name__ == "__main__":
    try:
        directorios, modelo, etas, salida = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    archivo_salida = (OUTPUT_DIR / salida) if (salida and "/" not in salida) else salida
    graficar(directorios, modelo, etas, archivo_salida)

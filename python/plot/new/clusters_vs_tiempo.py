import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR

from config_util import (t_inicio_para, densidad_de_directorio, cargar_tinicios,
                         modelo_de_directorio, etiqueta_densidad)


FUENTE = 20
TAM_FIG = (13, 6)


def graficar(directorios, modelo, eta, archivo_salida=None):
    """Dibuja S(t) del cluster mas grande para cada directorio/densidad.
    Acepta varias densidades (una curva S(t) por directorio) para mostrar densidades
    altas y bajas juntas. Linea vertical en el inicio del estacionario por curva."""
    fig, ax = plt.subplots(figsize=TAM_FIG)
    fig.subplots_adjust(bottom=0.16, left=0.10)

    tinicios = cargar_tinicios()
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for directorio, color in zip(directorios, colores):
        densidad = densidad_de_directorio(directorio)
        ruta = RESULTADOS / directorio / f"ruido_eta{float(eta)}.csv"
        if not ruta.exists():
            print(f"Error: no existe {ruta}")
            sys.exit(1)
        df = pd.read_csv(ruta)
        t = df["Time"].to_numpy()
        S = df["S"].to_numpy()

        t_inicio = t_inicio_para(modelo, densidad, eta, tinicios)
        ax.plot(t, S, color=color, linewidth=1.8,
                label=f"$\\rho={etiqueta_densidad(densidad)}$")
        ax.axvline(t_inicio, color=color, linestyle="--", linewidth=1.6, alpha=0.7)

    ax.set_xlabel("Pasos", fontsize=FUENTE)
    ax.set_ylabel("Fracción del cluster más grande", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best", fontsize=FUENTE)
    ax.grid(alpha=0.3)

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "clusters_vs_tiempo.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


def imprimir_uso():
    print(
        "Uso: python plot/new/clusters_vs_tiempo.py [opciones]\n"
        "Sin --directorio grafica standard/rho4 (default).\n\n"
        "  --directorio NOM   build/resultados/NOM/ (repetible: una curva S(t) por densidad)\n"
        "                     Ej: standard/rho8 standard/rho0.318\n"
        "  --modelo MOD       standard | voter (default: se deduce de la ruta)\n"
        "  --eta VALOR        Ruido de la curva (default: primer 'b' del modelo en tinicios.json)\n"
        "  --salida ARCHIVO.png  Grafico de salida\n"
        "  -h, --help         Mostrar esta ayuda"
    )


def parsear_args(argv):
    directorios = []
    modelo = "standard"
    modelo_dado = False
    eta = None
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
        elif arg == "--eta":
            i += 1
            eta = float(argv[i])
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

    if eta is None:
        tinicios = cargar_tinicios()
        eta = tinicios[modelo]["b"][0]

    return directorios, modelo, eta, salida


if __name__ == "__main__":
    try:
        directorios, modelo, eta, salida = parsear_args(sys.argv[1:])
    except (ValueError, IndexError, KeyError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    archivo_salida = (OUTPUT_DIR / salida) if (salida and "/" not in salida) else salida
    graficar(directorios, modelo, eta, archivo_salida)

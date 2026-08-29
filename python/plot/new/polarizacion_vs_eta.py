import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR
from utils import cargar_archivos_barrido
from config_util import (t_inicio_para, densidad_de_directorio, cargar_tinicios,
                         modelo_de_directorio, etiqueta_densidad)


FUENTE = 20
TAM_FIG = (13, 6)


def resumir_directorio(directorio, modelo):
    """Media y desvio de la polarizacion en el estacionario para cada eta,
    usando t_inicio desde tinicios.json (criterio de inspeccion visual)."""
    archivos = cargar_archivos_barrido(directorio)
    if not archivos:
        print(f"Error: No hay ruido_eta*.csv en {directorio}")
        sys.exit(1)

    densidad = densidad_de_directorio(directorio)
    tinicios = cargar_tinicios()

    filas = []
    for ruta, eta in archivos:
        df = pd.read_csv(ruta)
        t = df["Time"].to_numpy()
        va = df["Polarization"].to_numpy()
        t_inicio = t_inicio_para(modelo, densidad, eta, tinicios)
        idx = int((t >= t_inicio).argmax()) if len(t) else 0
        tramo = va[idx:]
        filas.append({
            "eta": eta,
            "va_media": tramo.mean(),
            "va_std": tramo.std(),
            "inicio_estacionario": t[idx] if len(t) else 0,
        })
    return pd.DataFrame(filas)


def graficar(directorios, modelo, archivo_salida=None):
    fig, ax = plt.subplots(figsize=TAM_FIG)
    fig.subplots_adjust(bottom=0.16, left=0.10)

    colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for directorio, color in zip(directorios, colores):
        resumen = resumir_directorio(directorio, modelo)
        ax.errorbar(
            resumen["eta"], resumen["va_media"], yerr=resumen["va_std"],
            fmt="o-", capsize=3, linewidth=1.2, markersize=5, color=color,
            label=f"$\\rho={etiqueta_densidad(densidad_de_directorio(directorio))}$",
        )

    ax.set_xlabel("Ruido", fontsize=FUENTE)
    ax.set_ylabel("Va", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best", fontsize=FUENTE)
    ax.grid(alpha=0.3)

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "polarizacion_vs_eta.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


def imprimir_uso():
    print(
        "Uso: python plot/new/polarizacion_vs_eta.py [opciones]\n"
        "Sin --directorio grafica standard/rho4 (default).\n\n"
        "  --directorio NOM     Lee build/resultados/NOM/ (repetible: una linea por densidad)\n"
        "                       Ej: standard/rho2 standard/rho4 standard/rho8 (o voter/rhoN)\n"
        "  --modelo MOD         standard | voter (default: se deduce de la ruta del directorio)\n"
        "  --salida ARCHIVO.png Gráfico de salida\n"
        "  -h, --help           Mostrar esta ayuda"
    )


def parsear_args(argv):
    directorios = []
    modelo = "standard"
    modelo_dado = False
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

    return directorios, modelo, salida


if __name__ == "__main__":
    try:
        directorios, modelo, salida = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    directorios_full = [RESULTADOS / d for d in directorios]
    archivo_salida = (OUTPUT_DIR / salida) if (salida and "/" not in salida) else salida
    graficar(directorios_full, modelo, archivo_salida)

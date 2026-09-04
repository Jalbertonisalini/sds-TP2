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
    """Media y desvio de S (fraccion del cluster mas grande) en el estacionario
    para cada eta, usando t_inicio desde tinicios.json (criterio visual)."""
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
        S = df["S"].to_numpy()
        t_inicio = t_inicio_para(modelo, densidad, eta, tinicios)
        idx = int((t >= t_inicio).argmax()) if len(t) else 0
        tramo = S[idx:]
        filas.append({
            "eta": eta,
            "S_media": tramo.mean(),
            "S_std": tramo.std(),
            "inicio_estacionario": t[idx] if len(t) else 0,
        })
    return pd.DataFrame(filas)


def clamp_err(centers, errs, lo=0.0, hi=1.0):
    """Recorta barras de error simétricas al dominio físico [lo, hi] (fracciones).
    Devuelve (err_inferior, err_superior) asimétricos para que las barras no
    sobrepasen lo/hi (ej. y > 1 en una fracción, que es imposible)."""
    lo_err, hi_err = [], []
    for x, e in zip(centers, errs):
        lo_err.append(max(0.0, min(e, x - lo)))
        hi_err.append(max(0.0, min(e, hi - x)))
    return lo_err, hi_err


def graficar(directorios, modelo, archivo_salida=None):
    fig, ax = plt.subplots(figsize=TAM_FIG)
    fig.subplots_adjust(bottom=0.16, left=0.10)

    colores = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for directorio, color in zip(directorios, colores):
        resumen = resumir_directorio(directorio, modelo)
        lo_err, hi_err = clamp_err(resumen["S_media"], resumen["S_std"])
        ax.errorbar(
            resumen["eta"], resumen["S_media"], yerr=[lo_err, hi_err],
            fmt="o-", capsize=3, linewidth=1.2, markersize=5, color=color,
            label=f"$\\rho={etiqueta_densidad(densidad_de_directorio(directorio), unidad=r'm^{-2}')}$",
        )

    refs = {
        "standard": (0.5, 1.5, 2.5, 3.5, 4.5),
        "voter": (0.1, 0.3, 0.5, 0.7, 0.9),
    }.get(modelo)
    if refs:
        trans = ax.get_xaxis_transform()
        for eta_ref in refs:
            ax.axvline(eta_ref, color="gray", linestyle=":", linewidth=1, alpha=0.6)
            ax.text(eta_ref, -0.03, str(eta_ref), transform=trans, ha="center", va="top",
                    fontsize=FUENTE - 8, color="gray")

    ax.set_xlabel("Ruido", fontsize=FUENTE)
    ax.set_ylabel("Fracción del cluster más grande", fontsize=FUENTE)
    ax.tick_params(labelsize=FUENTE)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best", fontsize=FUENTE)
    ax.grid(alpha=0.3)

    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "clusters_vs_eta.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")


def imprimir_uso():
    print(
        "Uso: python plot/new/clusters_vs_eta.py [opciones]\n"
        "Sin --directorio grafica standard/rho4 (default).\n\n"
        "  --directorio NOM   build/resultados/NOM/ (repetible: una linea por densidad)\n"
        "                     Ej: standard/rho2 standard/rho4 standard/rho8 (o voter/rhoN)\n"
        "  --modelo MOD       standard | voter (default: se deduce de la ruta del directorio)\n"
        "  --salida ARCHIVO.png  Grafico de salida\n"
        "  -h, --help         Mostrar esta ayuda"
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

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import RESULTADOS, OUTPUT_DIR

from config_util import (t_inicio_para, densidad_de_directorio, cargar_tinicios,
                         etas_b_para, densidades_de_modelo, modelo_de_directorio)


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
    ax.set_ylabel("Polarización", fontsize=FUENTE)
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
        "Sin eta:tinicio usa las de tinicios.json para el modelo/densidad.\n\n"
        "  eta:tinicio     Override puntual: ruido y tiempo de inicio del estacionario\n"
        "                  (repetible). t_inicio se fija por inspeccion visual.\n"
        "  --modelo MOD    standard | voter (default standard)\n"
        "  --directorio NOM  Subdirectorio en build/resultados, ej: standard/rho4, voter/rho4\n"
        "                  (default <modelo>/rho4)\n"
        "  --salida ARCHIVO.png  Archivo de salida\n"
        "  -h, --help       Mostrar esta ayuda"
    )


def parsear_args(argv):
    overrides = []
    modelo = "standard"
    modelo_dado = False
    directorio = ""
    salida = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            imprimir_uso()
            sys.exit(0)
        elif arg == "--modelo":
            i += 1
            modelo = argv[i]
            modelo_dado = True
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
            overrides.append((float(eta_str), int(tin_str)))
        else:
            raise ValueError(f"formato invalido: {arg} (usar eta:tinicio)")
        i += 1

    if not modelo_dado and directorio:
        derivado = modelo_de_directorio(directorio)
        if derivado:
            modelo = derivado

    densidad = densidad_de_directorio(directorio) if directorio else None
    tinicios = cargar_tinicios()

    if densidad is None:
        dens = "4" if "4" in tinicios[modelo] else densidades_de_modelo(modelo, tinicios)[0]
        densidad = dens
        directorio = f"{modelo}/rho{dens}"

    if overrides:
        casos = overrides
    else:
        casos = []
        for eta in etas_b_para(modelo, tinicios):
            casos.append((eta, t_inicio_para(modelo, densidad, eta, tinicios)))

    return casos, directorio, salida


if __name__ == "__main__":
    global RESULTADOS
    try:
        casos, directorio, salida = parsear_args(sys.argv[1:])
    except (ValueError, IndexError, KeyError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    if directorio:
        RESULTADOS = RESULTADOS / directorio

    archivo_salida = (OUTPUT_DIR / salida) if (salida and "/" not in salida) else salida
    graficar(casos, archivo_salida)

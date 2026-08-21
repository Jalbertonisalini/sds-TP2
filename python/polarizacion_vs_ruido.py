import re
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from polarizacion import detectar_inicio_estacionario


DIRECTORIO_ACTUAL = Path(__file__).parent
DIRECTORIO_BASE_RESULTADOS = DIRECTORIO_ACTUAL.parent / "build" / "resultados"
DIRECTORIO_SALIDA = DIRECTORIO_ACTUAL / "output"

DIRECTORIO_DEFECTO = "barrido_ruido"
GRAFICO_DEFECTO = "polarizacion_vs_eta.png"
TITULO_DEFECTO = "Polarización estacionaria $\\langle v_a \\rangle$ en función del ruido $\\eta$"

PATRON_ARCHIVO = re.compile(r"^ruido_eta([\d.]+)\.csv$")


def imprimir_uso():
    print(
        "Uso: python polarizacion_vs_ruido.py [opciones]\n\n"
        f"  --directorio NOM     Lee las series de build/resultados/NOM/ (default {DIRECTORIO_DEFECTO})\n"
        f"  --salida ARCHIVO.png Gráfico de salida (default {GRAFICO_DEFECTO})\n"
        "  --titulo TEXTO       Título del gráfico (usa LaTeX para símbolos)\n"
        "  -h, --help           Mostrar esta ayuda"
    )


def parsear_args(argv):
    directorio = DIRECTORIO_DEFECTO
    salida = GRAFICO_DEFECTO
    titulo = TITULO_DEFECTO

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
        elif arg == "--titulo":
            i += 1
            titulo = argv[i]
        else:
            raise ValueError(f"opción desconocida: {arg}")
        i += 1

    return directorio, salida, titulo


def extraer_eta(ruta):
    coincidencia = PATRON_ARCHIVO.match(ruta.name)
    return float(coincidencia.group(1)) if coincidencia else None


def resumir_caso(ruta, eta):
    """Media y desvío estándar de va(t) en la ventana estacionaria (corte por MSER)."""
    df = pd.read_csv(ruta)
    t = df["Time"].to_numpy()
    va = df["Polarization"].to_numpy()

    idx_inicio, hay_transiente = detectar_inicio_estacionario(t, va)
    tramo = va[idx_inicio:]

    return {
        "eta": eta,
        "va_media": tramo.mean(),
        "va_std": tramo.std(),
        "inicio_estacionario": int(t[idx_inicio]),
        "pasos_totales": int(t[-1]),
    }


def graficar(resumen, titulo, archivo_salida):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.errorbar(
        resumen["eta"], resumen["va_media"], yerr=resumen["va_std"],
        fmt="o-", capsize=3, linewidth=1, markersize=4,
        label="$\\langle v_a \\rangle \\pm \\sigma$",
    )

    ax.set_xlabel("Ruido $\\eta$")
    ax.set_ylabel("Polarización media $\\langle v_a \\rangle$")
    ax.set_ylim(0, 1.05)
    ax.set_title(titulo)
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico guardado en {archivo_salida}")

    plt.show()


if __name__ == "__main__":
    try:
        directorio, salida, titulo = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    directorio_resultados = DIRECTORIO_BASE_RESULTADOS / directorio
    if not directorio_resultados.exists():
        raise SystemExit(
            f"Error: No existe {directorio_resultados}.\n"
            "Corré primero: python correr_ruido.py --directorio " + directorio
        )

    archivos = []
    for ruta in sorted(directorio_resultados.glob("ruido_eta*.csv")):
        eta = extraer_eta(ruta)
        if eta is not None:
            archivos.append((ruta, eta))
    archivos.sort(key=lambda par: par[1])

    if not archivos:
        raise SystemExit(f"Error: No hay series ruido_eta*.csv en {directorio_resultados}")

    print(f"Procesando {len(archivos)} casos de {archivos[0][1]} a {archivos[-1][1]}...")
    filas = [resumir_caso(ruta, eta) for ruta, eta in archivos]

    resumen = pd.DataFrame(filas)

    archivo_resumen = directorio_resultados / "resumen_polarizacion_vs_eta.csv"
    resumen.to_csv(archivo_resumen, index=False)
    print(f"Resumen guardado en {archivo_resumen}")
    print(resumen.to_string(index=False))

    DIRECTORIO_SALIDA.mkdir(exist_ok=True)
    graficar(resumen, titulo, DIRECTORIO_SALIDA / salida)

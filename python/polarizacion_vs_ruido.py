import re
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from polarizacion import detectar_inicio_estacionario


DIRECTORIO_ACTUAL = Path(__file__).parent
DIRECTORIO_RESULTADOS = DIRECTORIO_ACTUAL.parent / "build" / "resultados" / "barrido_ruido"
DIRECTORIO_SALIDA = DIRECTORIO_ACTUAL / "output"

ARCHIVO_RESUMEN = DIRECTORIO_RESULTADOS / "resumen_polarizacion_vs_eta.csv"
ARCHIVO_GRAFICO = DIRECTORIO_SALIDA / "polarizacion_vs_eta.png"

PATRON_ARCHIVO = re.compile(r"^ruido_eta([\d.]+)\.csv$")


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


def graficar(resumen, archivo_salida):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.errorbar(
        resumen["eta"], resumen["va_media"], yerr=resumen["va_std"],
        fmt="o-", capsize=3, linewidth=1, markersize=4,
        label="$\\langle v_a \\rangle \\pm \\sigma$",
    )

    ax.set_xlabel("Ruido $\\eta$")
    ax.set_ylabel("Polarización media $\\langle v_a \\rangle$")
    ax.set_ylim(0, 1.05)
    ax.set_title("Polarización estacionaria $\\langle v_a \\rangle$ en función del ruido $\\eta$")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico guardado en {archivo_salida}")

    plt.show()


if __name__ == "__main__":
    if not DIRECTORIO_RESULTADOS.exists():
        raise SystemExit(
            f"Error: No existe {DIRECTORIO_RESULTADOS}.\n"
            "Corré primero: python correr_ruido.py --directorio barrido_ruido"
        )

    archivos = []
    for ruta in sorted(DIRECTORIO_RESULTADOS.glob("ruido_eta*.csv")):
        eta = extraer_eta(ruta)
        if eta is not None:
            archivos.append((ruta, eta))
    archivos.sort(key=lambda par: par[1])

    if not archivos:
        raise SystemExit(f"Error: No hay series ruido_eta*.csv en {DIRECTORIO_RESULTADOS}")

    print(f"Procesando {len(archivos)} casos de {archivos[0][1]} a {archivos[-1][1]}...")
    filas = [resumir_caso(ruta, eta) for ruta, eta in archivos]

    resumen = pd.DataFrame(filas)
    resumen.to_csv(ARCHIVO_RESUMEN, index=False)
    print(f"Resumen guardado en {ARCHIVO_RESUMEN}")
    print(resumen.to_string(index=False))

    DIRECTORIO_SALIDA.mkdir(exist_ok=True)
    graficar(resumen, ARCHIVO_GRAFICO)

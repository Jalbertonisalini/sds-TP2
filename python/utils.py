import re
import sys
import numpy as np
import pandas as pd
from pathlib import Path

from config import RESULTADOS


PATRON_ETA = re.compile(r"^ruido_eta([\d.]+)\.csv$")


# --- MSER ---

def promedios_por_bloque(va, tam_bloque):
    n_bloques = len(va) // tam_bloque
    bloques = va[: n_bloques * tam_bloque].reshape(n_bloques, tam_bloque)
    return bloques.mean(axis=1)


def _mser(bloques, fraccion_max_descartada):
    k = len(bloques)
    d_max = int(k * fraccion_max_descartada)

    suf_sum = np.cumsum(bloques[::-1])[::-1]
    suf_sum_sq = np.cumsum((bloques ** 2)[::-1])[::-1]
    n_d = np.arange(k, 0, -1)

    media_d = suf_sum / n_d
    mse_d = (suf_sum_sq - n_d * media_d ** 2) / (n_d ** 2)

    d_estrella = int(np.argmin(mse_d[: d_max + 1]))
    return d_estrella, mse_d


def detectar_inicio_estacionario(t, va, tam_bloque=100,
                                  fraccion_max_descartada=0.5,
                                  razon_minima=3.0):
    bloques = promedios_por_bloque(va, tam_bloque)
    d_estrella, mse_d = _mser(bloques, fraccion_max_descartada)

    if mse_d[d_estrella] <= 0:
        hay_transiente = d_estrella > 0
    else:
        hay_transiente = (mse_d[0] / mse_d[d_estrella]) >= razon_minima

    if not hay_transiente:
        return 0, False

    idx_inicio = min(d_estrella * tam_bloque, len(t) - 1)
    return idx_inicio, True


# --- Carga de archivos ---

def extraer_eta(ruta):
    coincidencia = PATRON_ETA.match(ruta.name)
    return float(coincidencia.group(1)) if coincidencia else None


def cargar_archivos_barrido(directorio):
    """Carga todos los ruido_eta*.csv de un directorio, devuelve [(ruta, eta)] ordenados."""
    archivos = []
    for ruta in sorted(Path(directorio).glob("ruido_eta*.csv")):
        eta = extraer_eta(ruta)
        if eta is not None:
            archivos.append((ruta, eta))
    archivos.sort(key=lambda par: par[1])
    return archivos


# --- Resumen de casos ---

def resumir_caso(ruta, eta, columnas=None):
    """
    Calcula media y desvío de columnas en la ventana estacionaria.
    columnas: lista de nombres de columna (default: ["Polarization", "S"])
    """
    if columnas is None:
        columnas = ["Polarization", "S"]

    df = pd.read_csv(ruta)
    t = df["Time"].to_numpy()

    idx_inicio, _ = detectar_inicio_estacionario(t, df["Polarization"].to_numpy())

    resultado = {"eta": eta, "inicio_estacionario": int(t[idx_inicio])}
    for col in columnas:
        tramo = df[col].to_numpy()[idx_inicio:]
        resultado[f"{col}_media"] = tramo.mean()
        resultado[f"{col}_std"] = tramo.std()

    return resultado


# --- Argumentos CLI para scripts de barrido ---

def parsear_args_barrido(argv, directorio_default="", salida_default="salida.png",
                         titulo_default=""):
    directorio = directorio_default
    salida = salida_default
    titulo = titulo_default

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            return None
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

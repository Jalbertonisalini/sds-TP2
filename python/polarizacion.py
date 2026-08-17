import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def calcular_polarizacion(archivo_csv):
    """va(t) = |<vector velocidad unitario>| promediado sobre las N partículas, por timestep."""
    df = pd.read_csv(archivo_csv, usecols=["Time", "Angle"])

    ux = np.cos(df["Angle"])
    uy = np.sin(df["Angle"])
    df = df.assign(ux=ux, uy=uy)

    promedios = df.groupby("Time")[["ux", "uy"]].mean()
    va = np.hypot(promedios["ux"], promedios["uy"])

    return va.index.to_numpy(), va.to_numpy()


def _promedios_por_bloque(va, tam_bloque):
    n_bloques = len(va) // tam_bloque
    bloques = va[: n_bloques * tam_bloque].reshape(n_bloques, tam_bloque)
    return bloques.mean(axis=1)


def _mser(bloques, fraccion_max_descartada):
    """
    MSER, Marginal Standard Error Rule (White, 1997): para cada posible punto
    de corte d, MSE(d) es el error cuadrático medio del estimador de la media
    usando solo bloques[d:]. Se calcula para todo d de una sola pasada con
    sumas por sufijo (acumulando desde el final hacia el principio).
    """
    k = len(bloques)
    d_max = int(k * fraccion_max_descartada)

    suf_sum = np.cumsum(bloques[::-1])[::-1]          # suf_sum[d]    = sum(bloques[d:])
    suf_sum_sq = np.cumsum((bloques ** 2)[::-1])[::-1]  # suf_sum_sq[d] = sum(bloques[d:]**2)
    n_d = np.arange(k, 0, -1)                           # n_d[d]        = k - d

    media_d = suf_sum / n_d
    mse_d = (suf_sum_sq - n_d * media_d ** 2) / (n_d ** 2)

    d_estrella = int(np.argmin(mse_d[: d_max + 1]))
    return d_estrella, mse_d


def detectar_inicio_estacionario(t, va, tam_bloque=100, fraccion_max_descartada=0.5, razon_minima=3.0):
    """
    va(t) fluctúa fuerte incluso en estado estacionario (N finito): no hay un
    valor fijo al que converger, así que comparar la serie cruda o su media
    móvil contra un umbral fijo no distingue "transiente real" de ruido de
    largo alcance (se probó y falla). En cambio, usamos MSER:

    1. Partimos va(t) en bloques de tam_bloque pasos (reduce autocorrelación).
    2. Para cada posible punto de corte d, calculamos el error cuadrático
       medio de usar solo bloques[d:] como estimador de la media. El d que
       lo minimiza es el que mejor balancea "sacar el transiente" contra "no
       tirar datos válidos de más". Nunca se descarta más de
       fraccion_max_descartada del total (evita la solución degenerada de
       quedarse con casi ningún dato al final).
    3. Si ese mínimo no mejora el MSE de no truncar nada (d=0) por al menos
       un factor razon_minima, concluimos que no hay un transiente real que
       valga la pena recortar: el sistema ya fluctúa en régimen estacionario
       desde el inicio del run.

    Devuelve (idx_inicio, hay_transiente).
    """
    bloques = _promedios_por_bloque(va, tam_bloque)
    d_estrella, mse_d = _mser(bloques, fraccion_max_descartada)

    if mse_d[d_estrella] <= 0:
        hay_transiente = d_estrella > 0
    else:
        hay_transiente = (mse_d[0] / mse_d[d_estrella]) >= razon_minima

    if not hay_transiente:
        return 0, False

    idx_inicio = min(d_estrella * tam_bloque, len(t) - 1)
    return idx_inicio, True


def graficar(t, va, idx_inicio, hay_transiente, titulo, archivo_salida):
    va_media = va[idx_inicio:].mean()
    va_std = va[idx_inicio:].std()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, va, color="#1f77b4", linewidth=0.8, label="$v_a(t)$")

    if hay_transiente:
        t_inicio = t[idx_inicio]
        ax.axvline(t_inicio, color="red", linestyle="--", linewidth=1.2,
                   label=f"Inicio estacionario (t={t_inicio})")
        estado_txt = f"Estado estacionario desde t={t_inicio} -> va = {va_media:.4f} ± {va_std:.4f}"
    else:
        estado_txt = f"Sin transiente detectado (estacionario desde t=0) -> va = {va_media:.4f} ± {va_std:.4f}"

    ax.axhline(va_media, color="green", linestyle=":", linewidth=1,
               label=f"$\\langle v_a \\rangle$ = {va_media:.3f} ± {va_std:.3f}")

    ax.set_xlabel("Tiempo (pasos)")
    ax.set_ylabel("Polarización $v_a$")
    ax.set_ylim(0, 1.05)
    ax.set_title(titulo)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico guardado en {archivo_salida}")
    print(estado_txt)

    plt.show()


if __name__ == "__main__":
    DIRECTORIO_ACTUAL = Path(__file__).parent
    ARCHIVO_CSV = DIRECTORIO_ACTUAL.parent / "build" / "evolucion_dinamica.csv"
    DIRECTORIO_SALIDA = DIRECTORIO_ACTUAL / "output"
    DIRECTORIO_SALIDA.mkdir(exist_ok=True)
    ARCHIVO_SALIDA = DIRECTORIO_SALIDA / "polarizacion_vs_tiempo.png"

    if not ARCHIVO_CSV.exists():
        print(f"Error: No se encontró el archivo {ARCHIVO_CSV}.")
    else:
        t, va = calcular_polarizacion(ARCHIVO_CSV)
        idx_inicio, hay_transiente = detectar_inicio_estacionario(t, va)
        graficar(t, va, idx_inicio, hay_transiente,
                 "Evolución temporal de la polarización $v_a$",
                 ARCHIVO_SALIDA)

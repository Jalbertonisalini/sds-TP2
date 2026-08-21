from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DIRECTORIO_ACTUAL = Path(__file__).parent
DIRECTORIO_RESULTADOS = DIRECTORIO_ACTUAL.parent / "build" / "resultados"
DIRECTORIO_SALIDA = DIRECTORIO_ACTUAL / "output"

CASOS = [
    ("ruido_eta0.6.csv", "$\\eta$ = 0.6"),
    ("ruido_eta2.2.csv", "$\\eta$ = 2.2"),
    ("ruido_eta5.3.csv", "$\\eta$ = 5.3"),
]


def graficar(casos, archivo_salida):
    """Combina las series de polarización de cada caso en un único gráfico comparativo."""
    fig, ax = plt.subplots(figsize=(10, 5))

    for archivo, etiqueta in casos:
        ruta = DIRECTORIO_RESULTADOS / archivo
        if not ruta.exists():
            print(f"Aviso: No se encontró {ruta}. Corré primero python correr_ruido.py")
            continue
        df = pd.read_csv(ruta)
        ax.plot(df["Time"], df["Polarization"], linewidth=0.8, label=etiqueta)

    ax.set_xlabel("Tiempo (pasos)")
    ax.set_ylabel("Polarización $v_a$")
    ax.set_ylim(0, 1.05)
    ax.set_title("Efecto del ruido $\\eta$ sobre la polarización $v_a(t)$ (modelo Standard)")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico guardado en {archivo_salida}")

    plt.show()


if __name__ == "__main__":
    DIRECTORIO_SALIDA.mkdir(exist_ok=True)
    ARCHIVO_SALIDA = DIRECTORIO_SALIDA / "polarizacion_comparacion.png"
    graficar(CASOS, ARCHIVO_SALIDA)

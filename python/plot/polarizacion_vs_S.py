import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import cargar_archivos_barrido, resumir_caso, parsear_args_barrido
from config import OUTPUT_DIR, RESULTADOS


def graficar(directorio, archivo_salida=None, titulo=""):
    archivos = cargar_archivos_barrido(directorio)
    if not archivos:
        print(f"Error: No hay ruido_eta*.csv en {directorio}")
        sys.exit(1)

    print(f"Procesando {len(archivos)} casos...")
    filas = [resumir_caso(ruta, eta, ["Polarization", "S"]) for ruta, eta in archivos]
    resumen = pd.DataFrame(filas)
    resumen.rename(columns={"Polarization_media": "va_media", "Polarization_std": "va_std"}, inplace=True)

    resumen_path = Path(directorio) / "resumen_polarizacion_vs_clusters.csv"
    resumen.to_csv(resumen_path, index=False)
    print(f"Resumen: {resumen_path}")

    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(resumen["S_media"], resumen["va_media"],
                    c=resumen["eta"], cmap="viridis", s=60,
                    edgecolors="black", linewidths=0.5, zorder=3)

    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("Ruido $\\eta$")

    for _, row in resumen.iterrows():
        ax.annotate(f'{row["eta"]:.1f}',
                    (row["S_media"], row["va_media"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=7)

    ax.set_xlabel("Fracción de la componente gigante $\\langle S \\rangle$")
    ax.set_ylabel("Polarización $\\langle v_a \\rangle$")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_title(titulo or "Polarización vs componente gigante")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "polarizacion_vs_S.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")

    plt.show()


if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("Uso: python plot/polarizacion_vs_S.py --directorio DIR [--salida archivo.png]")
        sys.exit(0)

    resultado = parsear_args_barrido(args)
    if resultado is None:
        print("Uso: python plot/polarizacion_vs_S.py --directorio DIR [--salida archivo.png]")
        sys.exit(1)

    directorio, salida, titulo = resultado
    directorio_full = RESULTADOS / directorio if directorio else RESULTADOS
    graficar(directorio_full, None if salida == "salida.png" else (OUTPUT_DIR / salida if "/" not in salida else salida), titulo)

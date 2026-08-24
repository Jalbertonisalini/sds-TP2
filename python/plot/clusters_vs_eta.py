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
    filas = [resumir_caso(ruta, eta, ["S"]) for ruta, eta in archivos]
    resumen = pd.DataFrame(filas)

    resumen.rename(columns={"S_media": "S_media", "S_std": "S_std"}, inplace=True)

    resumen_path = Path(directorio) / "resumen_clusters_vs_eta.csv"
    resumen.to_csv(resumen_path, index=False)
    print(f"Resumen: {resumen_path}")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.errorbar(resumen["eta"], resumen["S_media"], yerr=resumen["S_std"],
                fmt="o-", capsize=3, linewidth=1, markersize=4,
                label="$\\langle S \\rangle \\pm \\sigma$")

    ax.set_xlabel("Ruido $\\eta$")
    ax.set_ylabel("Fracción del cluster más grande $\\langle S \\rangle$")
    ax.set_ylim(0, 1.05)
    ax.set_title(titulo or "Cluster más grande vs ruido")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "clusters_vs_eta.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")

    plt.show()


if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("Uso: python plot/clusters_vs_eta.py --directorio DIR [--salida archivo.png]")
        sys.exit(0)

    resultado = parsear_args_barrido(args)
    if resultado is None:
        print("Uso: python plot/clusters_vs_eta.py --directorio DIR [--salida archivo.png]")
        sys.exit(1)

    directorio, salida, titulo = resultado
    directorio_full = RESULTADOS / directorio if directorio else RESULTADOS
    graficar(directorio_full, None if salida == "salida.png" else (OUTPUT_DIR / salida if "/" not in salida else salida), titulo)

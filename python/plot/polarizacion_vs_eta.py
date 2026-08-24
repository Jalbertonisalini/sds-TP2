import re
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import cargar_archivos_barrido, resumir_caso
from config import OUTPUT_DIR, RESULTADOS


DIRECTORIOS_DEFECTO = ["rho4"]  # una densidad por directorio (ver run.py --directorio)
PATRON_DIRECTORIO_RHO = re.compile(r"^rho([\d.]+)$")


def etiqueta_para(directorio):
    """Deriva una etiqueta legible ('$\\rho=4$') a partir del nombre del directorio."""
    coincidencia = PATRON_DIRECTORIO_RHO.match(Path(directorio).name)
    if coincidencia:
        return f"$\\rho={coincidencia.group(1)}$"
    return Path(directorio).name


def resumir_directorio(directorio):
    archivos = cargar_archivos_barrido(directorio)
    if not archivos:
        print(f"Error: No hay ruido_eta*.csv en {directorio}")
        sys.exit(1)

    print(f"[{Path(directorio).name}] Procesando {len(archivos)} casos...")
    filas = [resumir_caso(ruta, eta, ["Polarization"]) for ruta, eta in archivos]
    resumen = pd.DataFrame(filas)
    resumen.rename(columns={"Polarization_media": "va_media", "Polarization_std": "va_std"}, inplace=True)

    resumen_path = Path(directorio) / "resumen_polarizacion_vs_eta.csv"
    resumen.to_csv(resumen_path, index=False)
    print(f"[{Path(directorio).name}] Resumen: {resumen_path}")

    return resumen


def graficar(directorios, archivo_salida=None, titulo=""):
    """directorios: lista de rutas, una curva (con etiqueta) por directorio."""
    fig, ax = plt.subplots(figsize=(10, 5))

    for directorio in directorios:
        resumen = resumir_directorio(directorio)
        ax.errorbar(
            resumen["eta"], resumen["va_media"], yerr=resumen["va_std"],
            fmt="o-", capsize=3, linewidth=1, markersize=4,
            label=etiqueta_para(directorio),
        )

    ax.set_xlabel("Ruido $\\eta$")
    ax.set_ylabel("Polarización media $\\langle v_a \\rangle$")
    ax.set_ylim(0, 1.05)
    ax.set_title(titulo or "Polarización estacionaria vs ruido")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    if archivo_salida is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        archivo_salida = OUTPUT_DIR / "polarizacion_vs_eta.png"
    fig.savefig(archivo_salida, dpi=150)
    print(f"Gráfico: {archivo_salida}")

    plt.show()


def imprimir_uso():
    print(
        "Uso: python plot/polarizacion_vs_eta.py [opciones]\n"
        "Sin --directorio grafica rho4 (default).\n\n"
        "  --directorio NOM     Lee build/resultados/NOM/ (repetible: una línea por aparición)\n"
        "  --salida ARCHIVO.png Gráfico de salida\n"
        "  --titulo TEXTO       Título del gráfico\n"
        "  -h, --help           Mostrar esta ayuda"
    )


def parsear_args(argv):
    directorios = []
    salida = None
    titulo = ""

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            imprimir_uso()
            sys.exit(0)
        elif arg == "--directorio":
            i += 1
            directorios.append(argv[i])
        elif arg == "--salida":
            i += 1
            salida = argv[i]
        elif arg == "--titulo":
            i += 1
            titulo = argv[i]
        else:
            raise ValueError(f"opción desconocida: {arg}")
        i += 1

    if not directorios:
        directorios = list(DIRECTORIOS_DEFECTO)

    return directorios, salida, titulo


if __name__ == "__main__":
    try:
        directorios, salida, titulo = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    directorios_full = [RESULTADOS / d for d in directorios]
    archivo_salida = (OUTPUT_DIR / salida) if (salida and "/" not in salida) else salida
    graficar(directorios_full, archivo_salida, titulo)

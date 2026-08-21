import subprocess
import sys
from pathlib import Path


RUTA_RAIZ = Path(__file__).resolve().parent.parent
RUTA_SIMULADOR = RUTA_RAIZ / "build" / "simulador"
DIRECTORIO_RESULTADOS = RUTA_RAIZ / "build" / "resultados"

DENSIDAD = 4
ITERACIONES = 20000
MODELO = "standard"

VALORES_RUIDO = [0.6, 2.2, 5.3]


def correr_caso(eta):
    """Corre una simulación con el ruido dado y guarda su serie temporal de polarización."""
    DIRECTORIO_RESULTADOS.mkdir(parents=True, exist_ok=True)
    archivo_salida = DIRECTORIO_RESULTADOS / f"ruido_eta{eta}.csv"

    comando = [
        str(RUTA_SIMULADOR),
        "--model", MODELO,
        "--density", str(DENSIDAD),
        "--eta", str(eta),
        "--iterations", str(ITERACIONES),
        "--output", str(archivo_salida),
    ]
    subprocess.run(comando, check=True)
    return archivo_salida


if __name__ == "__main__":
    if not RUTA_SIMULADOR.exists():
        sys.exit(
            f"Error: No se encontró el simulador en {RUTA_SIMULADOR}.\n"
            "Compilá primero: mkdir -p build && cd build && cmake .. && make"
        )

    for eta in VALORES_RUIDO:
        print(f"\n=== Caso eta={eta} ===")
        archivo = correr_caso(eta)
        print(f"Resultado guardado en {archivo}")

    print(f"\nExperimento completo: resultados en {DIRECTORIO_RESULTADOS}")

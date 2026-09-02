import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import SIMULADOR, RESULTADOS
from config_util import FRACCIONES_DENSIDAD

# Corre --cim-timing del simulador para las 3 densidades del TP (N = rho * L^2 con
# L=10 -> 200, 400, 800) más las densidades "bajas" en fracciones de pi que ya usa
# el proyecto (FRACCIONES_DENSIDAD, ej. c_standard_lowdens.png) -> N chicos, para tener
# más puntos en la curva del punto g). El CIM no depende del modelo
# (standard/voter comparten build+vecinos), así que alcanza con una corrida por
# densidad.

DENSIDADES = (2, 4, 8) + tuple(frac for frac, _ in FRACCIONES_DENSIDAD)


def main():
    csv_path = RESULTADOS / "cim_timing_tp2.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.unlink(missing_ok=True)

    for rho in DENSIDADES:
        subprocess.run(
            [str(SIMULADOR), "--density", str(rho), "--model", "standard", "--cim-timing", str(csv_path)],
            check=True,
        )

    print(f"Listo: {csv_path}")


if __name__ == "__main__":
    main()

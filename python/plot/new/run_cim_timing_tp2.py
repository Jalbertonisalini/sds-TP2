import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import SIMULADOR, RESULTADOS

# Corre --cim-timing del simulador para los mismos N que usa el barrido del TP1
# (cim_tp1_bench/run_sweep.py, N_VALUES con L=20), para que el punto g) compare el
# CIM a cantidades de partículas similares a las estudiadas en el TP1 (enunciado:
# "número de partículas similar a las estudiadas en el TP1"). El CIM no depende del
# modelo (standard/voter comparten build+vecinos), así que alcanza con una corrida
# por N.
#
# Se usa --n (cantidad exacta de partículas) en vez de --density, porque varios de
# los N del TP1 (ej. 25, 350, 500, 650, 900, 1000) no salen de density*L*L con L=10.

N_VALUES = [10, 25, 50, 100, 200, 350, 400, 500, 650, 800, 900, 1000]


def main():
    csv_path = RESULTADOS / "cim_timing_tp2.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.unlink(missing_ok=True)

    for n in N_VALUES:
        subprocess.run(
            [str(SIMULADOR), "--n", str(n), "--model", "standard", "--cim-timing", str(csv_path)],
            check=True,
        )

    print(f"Listo: {csv_path}")


if __name__ == "__main__":
    main()

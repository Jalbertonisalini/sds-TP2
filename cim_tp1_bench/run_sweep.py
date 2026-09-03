#!/usr/bin/env python3
"""Corre el mismo barrido de N que SDS-TP1 (Tarea 4.1, régimen "libre", L=20,
rc=1, PBC), pero con el CIM de TP1 portado a C++ (cim_bench), que usa el mismo
kernel compartido que el --cim-timing del TP2 (cell_index_method_shared.hpp, ver
punto g), para comparar tiempos contra SDS-TP1/output/tarea4/n_benchmark.csv.

Reutiliza SDS-TP1/source/python/generate_input.py para generar los mismos
inputs (mismo seed) que usó el benchmark original en Java.
"""
import argparse
import csv
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TP1 = AQUI.parent.parent / "SDS-TP1"
BINARIO = AQUI / "build" / "cim_bench"

# Mismos N que SDS-TP1/output/tarea4/n_benchmark.csv (regimen "libre"), más 400
# para cubrir rho=4 del TP2 (N = rho * L^2 con L=10 -> 200, 400, 800).
N_VALUES = [10, 25, 50, 100, 200, 350, 400, 500, 650, 800, 900, 1000]

L = 20.0
RC = 1.0
SEED = 42


def limpiar_csv(csv_path, regimen):
    if not csv_path.exists():
        return
    with open(csv_path) as f:
        keep = [row for row in csv.DictReader(f) if row["regimen"] != regimen]
    with open(csv_path, "w", newline="") as f:
        if keep:
            writer = csv.DictWriter(f, fieldnames=keep[0].keys())
            writer.writeheader()
            writer.writerows(keep)
        else:
            csv_path.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=AQUI / "output" / "n_benchmark_cpp.csv")
    parser.add_argument("--regimen", default="libre_cpp")
    args = parser.parse_args()

    if not BINARIO.exists():
        sys.exit(f"Error: no existe {BINARIO}. Compilar antes: cmake -S . -B build && cmake --build build")

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    limpiar_csv(args.csv, args.regimen)

    static_path = TP1 / "input" / "static.txt"
    dynamic_path = TP1 / "input" / "dynamic.txt"

    for n in N_VALUES:
        subprocess.run(
            [sys.executable, str(TP1 / "source" / "python" / "generate_input.py"),
             "--n", str(n), "--l", str(L), "--seed", str(SEED)],
            cwd=TP1, check=True,
        )
        subprocess.run(
            [str(BINARIO), str(n), str(L), str(RC), "true", args.regimen,
             str(args.csv), "false", str(static_path), str(dynamic_path)],
            check=True,
        )

    print(f"Listo: {args.csv}")


if __name__ == "__main__":
    main()

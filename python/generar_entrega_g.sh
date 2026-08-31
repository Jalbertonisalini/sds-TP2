#!/bin/bash
set -e
cd "$(dirname "$0")"
E=../entrega

# --- c) 30000 pasos ---
python3 plot/new/polarizacion_vs_eta.py --directorio standard_30000/rho2 --directorio standard_30000/rho4 --directorio standard_30000/rho8 --modelo standard --salida $E/c_standard_3dens_30000.png
python3 plot/new/polarizacion_vs_eta.py --directorio standard_30000/rho0.106 --directorio standard_30000/rho0.159 --directorio standard_30000/rho0.318 --modelo standard --salida $E/c_standard_lowdens_30000.png
python3 plot/new/polarizacion_vs_eta.py --directorio voter_30000/rho2 --directorio voter_30000/rho4 --directorio voter_30000/rho8 --modelo voter --salida $E/c_voter_3dens_30000.png
python3 plot/new/polarizacion_vs_eta.py --directorio voter_30000/rho0.106 --directorio voter_30000/rho0.159 --directorio voter_30000/rho0.318 --modelo voter --salida $E/c_voter_lowdens_30000.png

# --- d1) evolucion S(t), 4 vs low (20000, nuevo) + 8 vs low y 4 vs low (30000, nuevo) ---
python3 plot/new/clusters_vs_tiempo.py --directorio standard/rho4 --directorio standard/rho0.318 --modelo standard --eta 0.5 --salida $E/d1_standard_4_vs_low.png
python3 plot/new/clusters_vs_tiempo.py --directorio voter/rho4 --directorio voter/rho0.318 --modelo voter --eta 0.1 --salida $E/d1_voter_4_vs_low.png
python3 plot/new/clusters_vs_tiempo.py --directorio standard_30000/rho8 --directorio standard_30000/rho0.318 --modelo standard --eta 0.5 --salida $E/d1_standard_8_vs_low_30000.png
python3 plot/new/clusters_vs_tiempo.py --directorio standard_30000/rho4 --directorio standard_30000/rho0.318 --modelo standard --eta 0.5 --salida $E/d1_standard_4_vs_low_30000.png
python3 plot/new/clusters_vs_tiempo.py --directorio voter_30000/rho8 --directorio voter_30000/rho0.318 --modelo voter --eta 0.1 --salida $E/d1_voter_8_vs_low_30000.png
python3 plot/new/clusters_vs_tiempo.py --directorio voter_30000/rho4 --directorio voter_30000/rho0.318 --modelo voter --eta 0.1 --salida $E/d1_voter_4_vs_low_30000.png

# --- d2) <S> vs eta, 4 vs low (20000, nuevo) + 8 vs low y 4 vs low (30000, nuevo) ---
python3 plot/new/clusters_vs_eta.py --directorio standard/rho4 --directorio standard/rho0.318 --modelo standard --salida $E/d2_standard_4_vs_low.png
python3 plot/new/clusters_vs_eta.py --directorio voter/rho4 --directorio voter/rho0.318 --modelo voter --salida $E/d2_voter_4_vs_low.png
python3 plot/new/clusters_vs_eta.py --directorio standard_30000/rho8 --directorio standard_30000/rho0.318 --modelo standard --salida $E/d2_standard_8_vs_low_30000.png
python3 plot/new/clusters_vs_eta.py --directorio standard_30000/rho4 --directorio standard_30000/rho0.318 --modelo standard --salida $E/d2_standard_4_vs_low_30000.png
python3 plot/new/clusters_vs_eta.py --directorio voter_30000/rho8 --directorio voter_30000/rho0.318 --modelo voter --salida $E/d2_voter_8_vs_low_30000.png
python3 plot/new/clusters_vs_eta.py --directorio voter_30000/rho4 --directorio voter_30000/rho0.318 --modelo voter --salida $E/d2_voter_4_vs_low_30000.png

# --- e) va vs S, 4 vs low (20000, nuevo) + 8 vs low y 4 vs low (30000, nuevo) ---
python3 plot/new/polarizacion_vs_S.py --directorio standard/rho4 --directorio standard/rho0.318 --modelo standard --salida $E/e_standard_4_vs_low.png
python3 plot/new/polarizacion_vs_S.py --directorio voter/rho4 --directorio voter/rho0.318 --modelo voter --salida $E/e_voter_4_vs_low.png
python3 plot/new/polarizacion_vs_S.py --directorio standard_30000/rho8 --directorio standard_30000/rho0.318 --modelo standard --salida $E/e_standard_8_vs_low_30000.png
python3 plot/new/polarizacion_vs_S.py --directorio standard_30000/rho4 --directorio standard_30000/rho0.318 --modelo standard --salida $E/e_standard_4_vs_low_30000.png
python3 plot/new/polarizacion_vs_S.py --directorio voter_30000/rho8 --directorio voter_30000/rho0.318 --modelo voter --salida $E/e_voter_8_vs_low_30000.png
python3 plot/new/polarizacion_vs_S.py --directorio voter_30000/rho4 --directorio voter_30000/rho0.318 --modelo voter --salida $E/e_voter_4_vs_low_30000.png

# --- b) evolucion va(t), 30000 pasos ---
python3 plot/new/evolucion_va_ruidos.py --directorio standard_30000/rho4 --modelo standard --salida $E/evolucion_va_ruidos_30000.png
python3 plot/new/evolucion_va_ruidos.py --directorio voter_30000/rho4 --modelo voter --salida $E/evolucion_va_voter_30000.png

echo "TODO_LISTO_PLOTS"

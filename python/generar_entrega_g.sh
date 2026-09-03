#!/bin/bash
set -e
cd "$(dirname "$0")"
E=../entrega

# --- c) 30000 pasos ---
python3 plot/new/polarizacion_vs_eta.py --directorio standard_30000/rho2 --directorio standard_30000/rho4 --directorio standard_30000/rho8 --modelo standard --salida $E/c_standard_3dens_30000.png
python3 plot/new/polarizacion_vs_eta.py --directorio standard_30000/rho0.106 --directorio standard_30000/rho0.159 --directorio standard_30000/rho0.318 --modelo standard --salida $E/c_standard_lowdens_30000.png
python3 plot/new/polarizacion_vs_eta.py --directorio voter_30000/rho2 --directorio voter_30000/rho4 --directorio voter_30000/rho8 --modelo voter --salida $E/c_voter_3dens_30000.png
python3 plot/new/polarizacion_vs_eta.py --directorio voter_30000/rho0.106 --directorio voter_30000/rho0.159 --directorio voter_30000/rho0.318 --modelo voter --salida $E/c_voter_lowdens_30000.png

# --- d1) evolucion S(t), 30000 pasos ---
python3 plot/new/clusters_vs_tiempo.py --directorio standard_30000/rho8 --directorio standard_30000/rho0.318 --modelo standard --eta 0.5 --salida $E/d1_standard_8_vs_low_30000.png
python3 plot/new/clusters_vs_tiempo.py --directorio standard_30000/rho4 --directorio standard_30000/rho0.318 --modelo standard --eta 0.5 --salida $E/d1_standard_4_vs_low_30000.png
python3 plot/new/clusters_vs_tiempo.py --directorio voter_30000/rho8 --directorio voter_30000/rho0.318 --modelo voter --eta 0.1 --salida $E/d1_voter_8_vs_low_30000.png
python3 plot/new/clusters_vs_tiempo.py --directorio voter_30000/rho4 --directorio voter_30000/rho0.318 --modelo voter --eta 0.1 --salida $E/d1_voter_4_vs_low_30000.png

# --- d2) <S> vs eta, 30000 pasos ---
python3 plot/new/clusters_vs_eta.py --directorio standard_30000/rho8 --directorio standard_30000/rho0.318 --modelo standard --salida $E/d2_standard_8_vs_low_30000.png
python3 plot/new/clusters_vs_eta.py --directorio standard_30000/rho4 --directorio standard_30000/rho0.318 --modelo standard --salida $E/d2_standard_4_vs_low_30000.png
python3 plot/new/clusters_vs_eta.py --directorio voter_30000/rho8 --directorio voter_30000/rho0.318 --modelo voter --salida $E/d2_voter_8_vs_low_30000.png
python3 plot/new/clusters_vs_eta.py --directorio voter_30000/rho4 --directorio voter_30000/rho0.318 --modelo voter --salida $E/d2_voter_4_vs_low_30000.png

# --- e) va vs S, 30000 pasos ---
# Densidades: 4 curvas (2, 1/(3π), 1/π, 8) a 30000 pasos, sin barras de error en Y.
python3 plot/new/polarizacion_vs_S.py --directorio standard_30000/rho2 --directorio standard_30000/rho0.106 --directorio standard_30000/rho0.318 --directorio standard_30000/rho8 --modelo standard --salida $E/e_standard_4dens_30000.png
python3 plot/new/polarizacion_vs_S.py --directorio voter_30000/rho2 --directorio voter_30000/rho0.106 --directorio voter_30000/rho0.318 --directorio voter_30000/rho8 --modelo voter --salida $E/e_voter_4dens_30000.png

# --- b) evolucion va(t), 30000 pasos ---
python3 plot/new/evolucion_va_ruidos.py --directorio standard_30000/rho4 --modelo standard --salida $E/evolucion_va_ruidos_30000.png
python3 plot/new/evolucion_va_ruidos.py --directorio voter_30000/rho4 --modelo voter --salida $E/evolucion_va_voter_30000.png

echo "TODO_LISTO_PLOTS"

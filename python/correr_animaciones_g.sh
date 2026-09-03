#!/usr/bin/env bash
# Genera las 16 animaciones MP4 (modelo x densidad x eta-bajo/alto).
# Cada animación corre una simulación de trayectorias con muchos pasos y
# reproduce el video acelerado para que dure <= ~20 s.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$AQUI/.." && pwd)"
PY="$AQUI/.venv/bin/python"
SIM="$RAIZ/build/simulador"
ANIM="$AQUI/plot/animar_mp4.py"

RESULT="$RAIZ/build/animaciones"
SALIDA="$RAIZ/entrega/animaciones"
mkdir -p "$RESULT" "$SALIDA"

ITER="${ITER:-5000}"
SEED="${SEED:-42}"

# modelo|densidad_libro|etiqueta_ruta|eta_bajo|eta_alto
COMBOS=(
  "standard 0.106 0.106 0.5 4.0"
  "standard 0.318 0.318 0.5 4.0"
  "standard 2.0 2 0.5 4.0"
  "standard 8.0 8 0.5 4.0"
  "voter 0.106 0.106 0.05 0.5"
  "voter 0.318 0.318 0.05 0.5"
  "voter 2.0 2 0.05 0.5"
  "voter 8.0 8 0.05 0.5"
)

if ! command -v ffprobe >/dev/null 2>&1; then
  echo "Aviso: ffprobe no disponible para verificar duracion."
fi

for combo in "${COMBOS[@]}"; do
  read -r modelo dens_ruta eta_ruta eta_bajo eta_alto <<<"$combo"

  for pareja in "$eta_bajo low" "$eta_alto high"; do
    read -r eta tag <<<"$pareja"

    csv="$RESULT/${modelo}_rho${eta_ruta}_eta${eta}_${tag}.csv"
    mp4="$SALIDA/${modelo}_rho${eta_ruta}_eta${eta}_${tag}.mp4"

    if [[ ! -f "$mp4" || ${FORZAR:-0} == 1 ]]; then
      cwd="$RESULT/${modelo}_rho${eta_ruta}_eta${eta}_${tag}"
      mkdir -p "$cwd"

      echo "=== ${modelo} rho=${dens_ruta} eta=${eta} (${tag}) ==="
      ( cd "$cwd" && "$SIM" --model "$modelo" --density "$dens_ruta" --eta "$eta" \
          --iterations "$ITER" --seed "$SEED" >/dev/null )
      mv -f "$cwd/evolucion_dinamica.csv" "$csv"

      titulo="$modelo  rho=${eta_ruta}  eta=${eta}"
      "$PY" "$ANIM" --input "$csv" --salida "$mp4" --titulo "$titulo"
    else
      echo "[salteado] $mp4"
    fi
  done
done

echo "Listo. Animaciones en $SALIDA"
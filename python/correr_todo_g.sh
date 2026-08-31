#!/bin/bash
set -e
cd "$(dirname "$0")"

densidades=(2 4 8 0.106 0.159 0.318)

for pasos in 20000 30000; do
  for modelo in standard voter; do
    dirmodelo="$modelo"
    if [ "$pasos" = "30000" ]; then dirmodelo="${modelo}_30000"; fi

    rango_args=()
    if [ "$modelo" = "voter" ]; then rango_args=(--rango 0 1 0.05); fi

    for d in "${densidades[@]}"; do
      echo "=== pasos=$pasos modelo=$modelo density=$d ==="
      python3 run.py "${rango_args[@]}" --density "$d" --modelo "$modelo" --pasos "$pasos" --directorio "$dirmodelo/rho$d"
    done
  done
done

echo "TODO_LISTO"

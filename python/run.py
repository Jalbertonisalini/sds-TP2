import subprocess
import sys

from config import (
    SIMULADOR, RESULTADOS, DENSITY_DEFAULT, ETA_DEFAULT,
    ITERATIONS_DEFAULT, MODEL_DEFAULT, SEED_DEFAULT, RANGO_RUIDO,
)


def valores_del_rango(rango):
    inicio, fin, paso = rango
    cantidad = int(round((fin - inicio) / paso))
    return [round(inicio + i * paso, 2) for i in range(cantidad + 1)]


def imprimir_uso():
    print(
        "Uso: python run.py [valores_eta...] [opciones]\n\n"
        "Sin argumentos corre el barrido completo definido en RANGO_RUIDO.\n\n"
        "  valores_eta...       Corre sólo esos valores (ej: 0.6 2.2 5.3)\n"
        f"  --density N          Densidad (default {DENSITY_DEFAULT})\n"
        f"  --rango IN FIN PASO  Rango de ruidos (default {RANGO_RUIDO})\n"
        f"  --pasos N            Pasos por corrida (default {ITERATIONS_DEFAULT})\n"
        f"  --modelo MOD         Modelo: standard | voter (default {MODEL_DEFAULT})\n"
        f"  --seed N             Semilla (default {SEED_DEFAULT})\n"
        "  --directorio NOM     Subdirectorio en build/resultados/ (default: raíz)\n"
        "  --forzar             Re-corre casos cuyo CSV ya exista\n"
        "  -h, --help           Mostrar esta ayuda"
    )


def parsear_args(argv):
    ruidos = []
    rango = None
    pasos = ITERATIONS_DEFAULT
    modelo = MODEL_DEFAULT
    density = DENSITY_DEFAULT
    seed = SEED_DEFAULT
    directorio = ""
    forzar = False

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            imprimir_uso()
            sys.exit(0)
        elif arg == "--pasos":
            i += 1
            pasos = int(argv[i])
        elif arg == "--modelo":
            i += 1
            if argv[i] not in ("standard", "voter"):
                raise ValueError(f"modelo desconocido: {argv[i]} (usar standard o voter)")
            modelo = argv[i]
        elif arg == "--density":
            i += 1
            density = float(argv[i])
        elif arg == "--seed":
            i += 1
            seed = int(argv[i])
        elif arg == "--directorio":
            i += 1
            directorio = argv[i]
        elif arg == "--forzar":
            forzar = True
        elif arg == "--rango":
            rango = tuple(float(x) for x in argv[i + 1 : i + 4])
            if len(rango) != 3:
                raise ValueError("--rango requiere INICIO FIN PASO")
            i += 3
        else:
            ruidos.append(float(arg))
        i += 1

    if not ruidos:
        ruidos = valores_del_rango(rango if rango is not None else RANGO_RUIDO)

    return ruidos, pasos, modelo, density, seed, directorio, forzar


def correr_caso(eta, pasos, modelo, density, seed, directorio_resultados):
    archivo_salida = directorio_resultados / f"ruido_eta{eta}.csv"
    comando = [
        str(SIMULADOR),
        "--model", modelo,
        "--density", str(density),
        "--eta", str(eta),
        "--iterations", str(pasos),
        "--seed", str(seed),
        "--output", str(archivo_salida),
    ]
    subprocess.run(comando, check=True)
    return archivo_salida


if __name__ == "__main__":
    if not SIMULADOR.exists():
        sys.exit(
            f"Error: No se encontró el simulador en {SIMULADOR}.\n"
            "Compilá primero: mkdir -p build && cd build && cmake .. && make"
        )

    try:
        ruidos, pasos, modelo, density, seed, directorio, forzar = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    directorio_resultados = RESULTADOS / directorio
    directorio_resultados.mkdir(parents=True, exist_ok=True)

    print(f"Barrido ({modelo}): eta={ruidos} | density={density} | pasos={pasos} | salida={directorio_resultados}")

    for eta in ruidos:
        archivo = directorio_resultados / f"ruido_eta{eta}.csv"
        if archivo.exists() and not forzar:
            print(f"[salteado] eta={eta}: ya existe {archivo.name} (--forzar para re-correr)")
            continue
        print(f"\n=== eta={eta} ===")
        correr_caso(eta, pasos, modelo, density, seed, directorio_resultados)
        print(f"Guardado en {archivo}")

    print(f"\nListo. Resultados en {directorio_resultados}")

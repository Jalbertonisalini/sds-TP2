import subprocess
import sys
from pathlib import Path


RUTA_RAIZ = Path(__file__).resolve().parent.parent
RUTA_SIMULADOR = RUTA_RAIZ / "build" / "simulador"
DIRECTORIO_BASE_RESULTADOS = RUTA_RAIZ / "build" / "resultados"

DENSIDAD = 4
MODELO = "standard"  # standard | voter

# Definición del barrido: (inicio, fin, paso)
RANGO_RUIDO = (0.0, 5.0, 0.25)
PASOS_DEFECTO = 20000


def valores_del_rango(rango):
    """Genera la lista de ruidos [inicio, fin] espaciados por paso, sin polvo de flotantes."""
    inicio, fin, paso = rango
    cantidad = int(round((fin - inicio) / paso))
    return [round(inicio + i * paso, 2) for i in range(cantidad + 1)]


def imprimir_uso():
    print(
        "Uso: python correr_ruido.py [valores_eta...] [opciones]\n"
        "Sin argumentos corre el barrido completo definido en RANGO_RUIDO.\n\n"
        "  valores_eta...       Corre sólo esos valores (ej: 0.6 2.2 5.3)\n"
        "  --rango IN FIN PASO  Usa otro rango de ruidos en vez de RANGO_RUIDO\n"
        f"  --pasos N            Pasos por corrida (default {PASOS_DEFECTO})\n"
        "  --modelo MOD         Modelo de interacción: standard | voter (default standard)\n"
        "  --directorio NOM     Guarda los resultados en build/resultados/NOM/\n"
        "                       (default: build/resultados/)\n"
        "  --forzar             Re-corre casos cuyo CSV ya exista\n"
        "  -h, --help           Mostrar esta ayuda"
    )


def parsear_args(argv):
    ruidos = []
    rango = None
    pasos = PASOS_DEFECTO
    modelo = MODELO
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

    return ruidos, pasos, modelo, directorio, forzar


def correr_caso(eta, pasos, modelo, directorio_resultados):
    archivo_salida = directorio_resultados / f"ruido_eta{eta}.csv"
    comando = [
        str(RUTA_SIMULADOR),
        "--model", modelo,
        "--density", str(DENSIDAD),
        "--eta", str(eta),
        "--iterations", str(pasos),
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

    try:
        ruidos, pasos, modelo, directorio, forzar = parsear_args(sys.argv[1:])
    except (ValueError, IndexError) as e:
        print(f"Error de argumentos: {e}")
        imprimir_uso()
        sys.exit(1)

    directorio_resultados = DIRECTORIO_BASE_RESULTADOS / directorio
    directorio_resultados.mkdir(parents=True, exist_ok=True)

    print(f"Barrido de ruido ({modelo}): eta={ruidos} | pasos={pasos} | salida={directorio_resultados}")

    for eta in ruidos:
        archivo = directorio_resultados / f"ruido_eta{eta}.csv"
        if archivo.exists() and not forzar:
            print(f"[salteado] eta={eta}: ya existe {archivo.name} (--forzar para re-correr)")
            continue
        print(f"\n=== Caso eta={eta} ===")
        correr_caso(eta, pasos, modelo, directorio_resultados)
        print(f"Resultado guardado en {archivo}")

    print(f"\nExperimento completo: resultados en {directorio_resultados}")

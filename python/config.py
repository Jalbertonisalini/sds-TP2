from pathlib import Path

# --- Parámetros de la caja ---
L = 10.0

# --- Parámetros de partículas ---
RC = 1.0
R_MAX = 0.0
VELOCITY = 0.03
DENSITY_DEFAULT = 4

# --- Defaults de simulación ---
ETA_DEFAULT = 0.5
ITERATIONS_DEFAULT = 20000
MODEL_DEFAULT = "standard"  # standard | voter
SEED_DEFAULT = 42

# --- Barrido de ruido ---
RANGO_RUIDO = (0.0, 5.0, 0.25)

# --- Rutas ---
RAIZ = Path(__file__).resolve().parent.parent
BUILD = RAIZ / "build"
SIMULADOR = BUILD / "simulador"
RESULTADOS = BUILD / "resultados"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

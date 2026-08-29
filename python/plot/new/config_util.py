import json
import math
import re
from pathlib import Path


PATRON_DIRECTORIO_RHO = re.compile(r"^rho([\d.]+)$")
MODELOS = ("standard", "voter")

AQUI = Path(__file__).resolve().parent
TINICIOS_PATH = AQUI / "tinicios.json"


def cargar_tinicios():
    """Devuelve el dict {modelo: {densidad: {eta: t_inicio}}} desde el JSON."""
    with open(TINICIOS_PATH) as f:
        return json.load(f)


def densidad_de_directorio(directorio):
    """Extrae la densidad ('4') del nombre del subdirectorio ('rho4'). Si no
    matchea el patron rhoN, devuelve el nombre tal cual."""
    coincidencia = PATRON_DIRECTORIO_RHO.match(Path(directorio).name)
    if coincidencia:
        return coincidencia.group(1)
    return Path(directorio).name


FRACCIONES_DENSIDAD = [
    (round(1 / (3 * math.pi), 3), r"1/(3\pi)"),
    (round(1 / (2 * math.pi), 3), r"1/(2\pi)"),
    (round(1 / math.pi, 3), r"1/\pi"),
]
EPS_DENSIDAD = 1e-6


def etiqueta_densidad(densidad):
    """Convierte una densidad (string o numero) a su etiqueta de leyenda.
    Las fracciones de pi se muestran como 1/pi, 1/(2pi), etc.; el resto se
    muestra tal cual (2, 4, 8, ...)."""
    try:
        valor = float(densidad)
    except (TypeError, ValueError):
        return str(densidad)
    # El nombre de carpeta usa 3 decimales (round(densidad, 3)); matchea a esa precision.
    valor = round(valor, 3)
    for frac, etiqueta in FRACCIONES_DENSIDAD:
        if abs(valor - frac) < EPS_DENSIDAD:
            return etiqueta
    return str(int(valor)) if float(valor).is_integer() else str(valor)


def modelo_de_directorio(directorio):
    """Devuelve el modelo ('standard'|'voter') si esta al principio de la ruta,
    o None si no es reconocible."""
    prim = Path(directorio).parts[0]
    return prim if prim in MODELOS else None


def densidades_de_modelo(modelo, tinicios=None):
    """Lista de densidades (excluyendo la clave especial 'b') para un modelo."""
    if tinicios is None:
        tinicios = cargar_tinicios()
    return [k for k in tinicios[modelo] if k != "b"]


def etas_b_para(modelo, tinicios=None):
    """Etas representativos del punto b) para un modelo."""
    if tinicios is None:
        tinicios = cargar_tinicios()
    return tinicios[modelo]["b"]


def t_inicio_para(modelo, densidad, eta, tinicios=None, default=0):
    """t_inicio para (modelo, densidad, eta) desde la tabla. Si falta el eta
    devuelve `default` (0) para no cortar la ejecucion."""
    if tinicios is None:
        tinicios = cargar_tinicios()
    try:
        return tinicios[modelo][densidad][str(eta)]
    except KeyError:
        return default

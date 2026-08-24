import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import L


def animar(archivo_csv):
    print("Cargando datos de la simulación...")
    df = pd.read_csv(archivo_csv)

    tiempos = df['Time'].unique()
    tiempos.sort()
    total_frames = len(tiempos)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect('equal')

    ax.set_facecolor('#1e1e1e')
    fig.patch.set_facecolor('#1e1e1e')

    df_t0 = df[df['Time'] == tiempos[0]]
    X0 = df_t0['X'].values
    Y0 = df_t0['Y'].values
    Angulos0 = df_t0['Angle'].values

    U0 = np.cos(Angulos0)
    V0 = np.sin(Angulos0)

    cmap = plt.get_cmap('hsv')
    norm = mcolors.Normalize(vmin=-np.pi, vmax=np.pi)

    Q = ax.quiver(X0, Y0, U0, V0, Angulos0, cmap=cmap, norm=norm,
                  pivot='tail', scale=25, width=0.005, headwidth=4)

    texto_progreso = ax.text(0.03, 0.95, '', transform=ax.transAxes,
                             color='white', fontsize=12, fontweight='bold',
                             bbox=dict(facecolor='black', alpha=0.6, edgecolor='none',
                                       boxstyle='round,pad=0.5'))

    ax.set_title("Autómata Off-Lattice: Dinámica de Bandadas", color='white',
                 fontsize=14, pad=10)

    def update(i):
        frame_time = tiempos[i]
        data = df[df['Time'] == frame_time]

        X = data['X'].values
        Y = data['Y'].values
        Angulos = data['Angle'].values

        U = np.cos(Angulos)
        V = np.sin(Angulos)

        Q.set_offsets(np.c_[X, Y])
        Q.set_UVC(U, V, Angulos)

        porcentaje = (i + 1) / total_frames * 100
        texto_progreso.set_text(f"Paso: {frame_time} | Progreso: {porcentaje:.1f}%")

        return Q, texto_progreso

    print("Generando animación interactiva...")

    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=30, blit=True)

    plt.tight_layout()
    plt.show()
    return ani


if __name__ == "__main__":
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print("Uso: python plot/animacion.py --input ARCHIVO_CSV")
        sys.exit(0)

    archivo = None
    i = 0
    while i < len(args):
        if args[i] == "--input":
            i += 1
            archivo = args[i]
        elif not args[i].startswith("-"):
            archivo = args[i]
        i += 1

    if not archivo:
        print("Error: falta --input ARCHIVO_CSV")
        sys.exit(1)

    animar(archivo)

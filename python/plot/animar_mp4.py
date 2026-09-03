import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import imageio_ffmpeg
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import L

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FPS = 30
DURACION_MAX = 20.0


def elegir_frames(n, max_frames):
    if n <= max_frames:
        return list(range(n))
    paso = n / max_frames
    return [min(int(i * paso), n - 1) for i in range(max_frames)]


def animar(archivo_csv, salida_mp4, titulo="", fps=FPS, dur_max=DURACION_MAX):
    df = pd.read_csv(archivo_csv)
    tiempos = np.sort(df["Time"].unique())
    n = len(tiempos)

    max_frames = int(dur_max * fps)
    frames = elegir_frames(n, max_frames)
    fps_real = len(frames) / min(len(frames) / fps, dur_max)
    if dur_max and len(frames) / fps > dur_max:
        fps_real = len(frames) / dur_max

    dpi = 160  # 8 * 160 = 1280 px
    fig, ax = plt.subplots(figsize=(8, 8), dpi=dpi)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect("equal")
    ax.set_facecolor("#1e1e1e")
    fig.patch.set_facecolor("#1e1e1e")

    # Flecha de tamano fijo, igual al usado en rho=2 (len=0.2475, shaft=0.0707).
    width = 0.007071
    scale = 57.2

    t0 = tiempos[0]
    d0 = df[df["Time"] == t0]
    X0 = d0["X"].to_numpy()
    Y0 = d0["Y"].to_numpy()
    A0 = d0["Angle"].to_numpy()
    U0 = np.cos(A0)
    V0 = np.sin(A0)

    cmap = plt.get_cmap("hsv")
    norm = mcolors.Normalize(vmin=-np.pi, vmax=np.pi)
    Q = ax.quiver(X0, Y0, U0, V0, A0, cmap=cmap, norm=norm,
                  pivot="tail", scale=scale, width=width, headwidth=4)

    # Ejes: etiquetas, caja visible y ticks legibles sobre fondo oscuro.
    ax.set_xlabel("posición X", color="white", fontsize=13)
    ax.set_ylabel("posición Y", color="white", fontsize=13)
    ax.tick_params(axis="both", colors="white", labelsize=10)
    for s in ax.spines.values():
        s.set_color("#c8c8c8")
        s.set_linewidth(1.5)

    texto = ax.text(0.03, 0.95, "", transform=ax.transAxes, color="white",
                    fontsize=12, fontweight="bold",
                    bbox=dict(facecolor="black", alpha=0.6, edgecolor="none",
                              boxstyle="round,pad=0.5"))
    ax.set_title(titulo, color="white", fontsize=14, pad=12)

    def update(i):
        ft = tiempos[frames[i]]
        d = df[df["Time"] == ft]
        X = d["X"].to_numpy()
        Y = d["Y"].to_numpy()
        A = d["Angle"].to_numpy()
        Q.set_offsets(np.c_[X, Y])
        Q.set_UVC(np.cos(A), np.sin(A), A)
        texto.set_text(f"Paso: {ft}")
        return Q, texto

    ani = animation.FuncAnimation(fig, update, frames=len(frames),
                                  interval=1000.0 / fps_real, blit=True)

    from matplotlib.animation import FFMpegWriter
    matplotlib.rcParams["animation.ffmpeg_path"] = FFMPEG
    writer = FFMpegWriter(fps=fps_real, codec="libx264", bitrate=6000,
                          extra_args=["-pix_fmt", "yuv420p"])
    plt.tight_layout()
    ani.save(salida_mp4, writer=writer)
    plt.close(fig)
    print(f"MP4: {salida_mp4}  ({len(frames)} frames, {len(frames)/fps_real:.1f}s)")


def main(argv):
    if "-h" in argv or "--help" in argv:
        print("Uso: python plot/animar_mp4.py --input CSV [--salida MP4] [--titulo T]")
        return
    entrada = None
    salida = None
    titulo = ""
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--input":
            entrada = argv[i + 1]; i += 2
        elif a == "--salida":
            salida = argv[i + 1]; i += 2
        elif a == "--titulo":
            titulo = argv[i + 1]; i += 2
        else:
            i += 1
    if not entrada:
        print("Error: falta --input CSV"); sys.exit(1)
    if salida is None:
        salida = str(Path(entrada).with_suffix(".mp4"))
    animar(entrada, salida, titulo)


if __name__ == "__main__":
    main(sys.argv[1:])
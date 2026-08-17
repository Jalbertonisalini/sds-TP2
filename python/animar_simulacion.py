import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
import matplotlib.colors as mcolors

def animar_simulacion(archivo_csv, L):
    print("Cargando datos de la simulación...")
    df = pd.read_csv(archivo_csv)
    
    tiempos = df['Time'].unique()
    tiempos.sort()
    total_frames = len(tiempos)
    
    # Configurar el lienzo
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect('equal')
    
    # Estética profesional estilo "dark mode"
    ax.set_facecolor('#1e1e1e')
    fig.patch.set_facecolor('#1e1e1e')
    
    # Preparar el frame inicial
    df_t0 = df[df['Time'] == tiempos[0]]
    X0 = df_t0['X'].values
    Y0 = df_t0['Y'].values
    Angulos0 = df_t0['Angle'].values
    
    U0 = np.cos(Angulos0)
    V0 = np.sin(Angulos0)
    
    cmap = plt.get_cmap('hsv')
    norm = mcolors.Normalize(vmin=-np.pi, vmax=np.pi)

    # Gráfico de vectores (Quiver)
    Q = ax.quiver(X0, Y0, U0, V0, Angulos0, cmap=cmap, norm=norm,
                  pivot='tail', scale=25, width=0.005, headwidth=4)

    # --- TEXTO DINÁMICO PARA EL PROGRESO ---
    # Lo ubicamos en la esquina superior izquierda dentro del gráfico
    texto_progreso = ax.text(0.03, 0.95, '', transform=ax.transAxes, 
                             color='white', fontsize=12, fontweight='bold',
                             bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.5'))

    ax.set_title("Autómata Off-Lattice: Dinámica de Bandadas", color='white', fontsize=14, pad=10)

    # Función de actualización
    def update(i):
        frame_time = tiempos[i]
        data = df[df['Time'] == frame_time]
        
        X = data['X'].values
        Y = data['Y'].values
        Angulos = data['Angle'].values
        
        U = np.cos(Angulos)
        V = np.sin(Angulos)
        
        # Actualizamos las posiciones y direcciones de las flechas
        Q.set_offsets(np.c_[X, Y])
        Q.set_UVC(U, V, Angulos)
        
        # Calcular porcentaje de progreso
        porcentaje = (i + 1) / total_frames * 100
        
        # Actualizar el texto en pantalla
        texto_progreso.set_text(f"Paso: {frame_time} | Progreso: {porcentaje:.1f}%")
        
        return Q, texto_progreso

    print("Generando animación interactiva...")
    
    # Crear animación
    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=30, blit=True)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    DIRECTORIO_ACTUAL = Path(__file__).parent
    DIRECTORIO_BUILD = DIRECTORIO_ACTUAL.parent / 'build'
    ARCHIVO_CSV = DIRECTORIO_BUILD / 'evolucion_dinamica.csv'
    
    LADO_CAJA = 10.0
    
    if ARCHIVO_CSV.exists():
        animar_simulacion(ARCHIVO_CSV, LADO_CAJA)
    else:
        print(f"Error: No se encontró el archivo {ARCHIVO_CSV}.")
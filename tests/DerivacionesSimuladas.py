import scipy.io
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

# --- 1. Cargar el archivo .mat ---
mat = scipy.io.loadmat('main.mat')

# --- 2. Acceder a los datos ---
x = mat['val']
print(f"La forma de los datos (shape) es: {x.shape}")

# --- 3. Crear el vector de tiempo ---
duracion_segundos = 10.0
num_muestras = x.shape[1]
Fs = num_muestras / duracion_segundos  # Frecuencia de muestreo
t = np.arange(num_muestras) / Fs
print(f"Frecuencia de muestreo (Fs) calculada: {Fs} Hz")

# --- 4. DISEÑAR Y APLICAR EL FILTRO ---

# Parámetros del filtro (Puedes ajustar 'cutoff_freq' si es necesario)
fs = Fs
cutoff_freq = 45.0  # Frecuencia de corte en Hz
order = 5

# Diseñar el filtro Butterworth
nyquist_freq = 0.5 * fs
normal_cutoff = cutoff_freq / nyquist_freq
b, a = butter(order, normal_cutoff, btype='low', analog=False)

# Aplicar el filtro a todas las señales
x_filtrado = filtfilt(b, a, x, axis=1)

# --- 5. Separar las 6 derivaciones (Datos FILTRADOS) ---
derivI_f   = x_filtrado[0, :]
derivII_f  = x_filtrado[1, :]
derivIII_f = x_filtrado[2, :]
derivIV_f  = x_filtrado[3, :]
derivV_f   = x_filtrado[4, :]
derivVI_f  = x_filtrado[5, :]

# --- 6. Graficar (SOLO SEÑALES FILTRADAS) ---

# 6 filas, 1 columna.
# sharex=True oculta automáticamente las etiquetas X de las gráficas de arriba
fig, axs = plt.subplots(6, 1, figsize=(10, 18), sharex=True)

# --- Gráfica 1 (Fila 0) ---
axs[0].plot(t, derivI_f, color='blue')
axs[0].set_title('Derivación I')
axs[0].set_ylim(-200, 1000)
axs[0].set_ylabel('Amplitud')

# --- Gráfica 2 (Fila 1) ---
axs[1].plot(t, derivII_f, color='blue')
axs[1].set_title('Derivación II')
axs[1].set_ylim(-500, 500)
axs[1].set_ylabel('Amplitud')

# --- Gráfica 3 (Fila 2) ---
axs[2].plot(t, derivIII_f, color='blue')
axs[2].set_title('Derivación III')
axs[2].set_ylim(-500, 250)
axs[2].set_ylabel('Amplitud')

# --- Gráfica 4 (Fila 3) ---
axs[3].plot(t, derivIV_f, color='blue')
axs[3].set_title('aVR')
axs[3].set_ylim(-500, 250)
axs[3].set_ylabel('Amplitud')

# --- Gráfica 5 (Fila 4) ---
axs[4].plot(t, derivV_f, color='blue')
axs[4].set_title('aVL')
axs[4].set_ylim(-500, 600)
axs[4].set_ylabel('Amplitud')

# --- Gráfica 6 (Fila 5) ---
axs[5].plot(t, derivVI_f, color='blue')
axs[5].set_title('aVF')
axs[5].set_ylim(-500, 250)
axs[5].set_ylabel('Amplitud')
axs[5].set_xlabel('Tiempo (s)')
axs[5].set_xlim(0, 10)


# --- 7. Mostrar y guardar la gráfica ---
plt.tight_layout()
plt.savefig('grafica_filtrada_final.png', dpi=300)
plt.show()

print("\n¡Gráfica filtrada guardada como 'grafica_filtrada_final.png'!")
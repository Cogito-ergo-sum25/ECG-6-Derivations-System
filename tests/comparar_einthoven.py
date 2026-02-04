import scipy.io
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

# --- 1. Cargar el archivo .mat ---
try:
    mat = scipy.io.loadmat('main.mat')
except FileNotFoundError:
    print("Error: No se encontró 'main.mat'.")
    exit()

# --- 2. Acceder a los datos ---
x = mat['val']

# --- 3. Crear el vector de tiempo ---
duracion_segundos = 10.0
num_muestras = x.shape[1]
Fs = num_muestras / duracion_segundos
t = np.arange(num_muestras) / Fs

# --- 4. DISEÑAR Y APLICAR EL FILTRO ---
fs = Fs
cutoff_freq = 45.0
order = 5
nyquist_freq = 0.5 * fs
normal_cutoff = cutoff_freq / nyquist_freq
b, a = butter(order, normal_cutoff, btype='low', analog=False)

x_filtrado = filtfilt(b, a, x, axis=1)
print(f"Datos cargados y filtrados (Fs={Fs} Hz, Corte={cutoff_freq} Hz).")

# --- 5. Separar las derivaciones RELEVANTES (Filtradas) ---

# --- Bases para el cálculo ---
derivI_f   = x_filtrado[0, :]
derivII_f  = x_filtrado[1, :]

# --- Originales (para comparar) ---
derivIII_original = x_filtrado[2, :]
aVR_original      = x_filtrado[3, :]
aVL_original      = x_filtrado[4, :]
aVF_original      = x_filtrado[5, :]


# --- 6. CÁLCULO DE LAS 4 DERIVACIONES ---
print("Calculando las 4 derivaciones...")

# Ley de Einthoven
derivIII_calculada = derivII_f - derivI_f

# Ecuaciones de Goldberger
aVR_calculada = -(derivI_f + derivII_f) / 2
aVL_calculada = derivI_f - (derivII_f / 2)
aVF_calculada = derivII_f - (derivI_f / 2)


# --- 7. Graficar las Comparaciones (Cuadrícula 4x2) ---

# 4 filas (una para cada lead), 2 columnas (Comparación | Error)
fig, axs = plt.subplots(4, 2, figsize=(16, 18))
fig.suptitle('Verificación de Derivaciones Calculadas (vs. Originales)', fontsize=18)

# --- Fila 1: Derivación III ---
axs[0, 0].plot(t, derivIII_original, 'b-', label='III Original (Fila 3)', alpha=0.8)
axs[0, 0].plot(t, derivIII_calculada, 'r--', label='III Calculada (II - I)')
axs[0, 0].set_title('Comparación Derivación III')
axs[0, 0].set_ylabel('Amplitud')
axs[0, 0].set_ylim(-500, 250) # Límite de tu gráfica anterior
axs[0, 0].legend()

error_III = derivIII_original - derivIII_calculada
axs[0, 1].plot(t, error_III, 'k-')
axs[0, 1].set_title('Error Derivación III')
axs[0, 1].set_ylabel('Amplitud Error')

# --- Fila 2: aVR ---
axs[1, 0].plot(t, aVR_original, 'b-', label='aVR Original (Fila 4)', alpha=0.8)
axs[1, 0].plot(t, aVR_calculada, 'r--', label='aVR Calculada')
axs[1, 0].set_title('Comparación aVR')
axs[1, 0].set_ylabel('Amplitud')
axs[1, 0].set_ylim(-500, 250) # Límite de tu gráfica anterior
axs[1, 0].legend()

error_aVR = aVR_original - aVR_calculada
axs[1, 1].plot(t, error_aVR, 'k-')
axs[1, 1].set_title('Error aVR')
axs[1, 1].set_ylabel('Amplitud Error')

# --- Fila 3: aVL ---
axs[2, 0].plot(t, aVL_original, 'b-', label='aVL Original (Fila 5)', alpha=0.8)
axs[2, 0].plot(t, aVL_calculada, 'r--', label='aVL Calculada')
axs[2, 0].set_title('Comparación aVL')
axs[2, 0].set_ylabel('Amplitud')
axs[2, 0].set_ylim(-500, 600) # Límite de tu gráfica anterior
axs[2, 0].legend()

error_aVL = aVL_original - aVL_calculada
axs[2, 1].plot(t, error_aVL, 'k-')
axs[2, 1].set_title('Error aVL')
axs[2, 1].set_ylabel('Amplitud Error')

# --- Fila 4: aVF ---
axs[3, 0].plot(t, aVF_original, 'b-', label='aVF Original (Fila 6)', alpha=0.8)
axs[3, 0].plot(t, aVF_calculada, 'r--', label='aVF Calculada')
axs[3, 0].set_title('Comparación aVF')
axs[3, 0].set_ylabel('Amplitud')
axs[3, 0].set_xlabel('Tiempo (s)')
axs[3, 0].set_ylim(-500, 250) # Límite de tu gráfica anterior
axs[3, 0].legend()

error_aVF = aVF_original - aVF_calculada
axs[3, 1].plot(t, error_aVF, 'k-')
axs[3, 1].set_title('Error aVF')
axs[3, 1].set_xlabel('Tiempo (s)')
axs[3, 1].set_ylabel('Amplitud Error')

# Aplicar a todos los ejes X y poner rejilla
for ax in axs.flat:
    ax.set_xlim(0, 10)
    ax.grid(True, linestyle=':', alpha=0.7)

# --- 8. Mostrar y guardar la gráfica ---
plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Ajuste para el supertítulo
plt.savefig('comparacion_4_leads_calculadas.png', dpi=300)
plt.show()

print("\n¡Gráfica final de comparación guardada como 'comparacion_4_leads_calculadas.png'!")
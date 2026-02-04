# plotter_ecg_PRUEBAS.py - Visor Crudo vs. Filtrado
import serial
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time

# --- CONFIGURACIÓN ---
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200
MAX_DATA_POINTS = 500

# --- DISEÑO DEL FILTRO DIGITAL ---
fs = 333.33 
lowcut = 0.5 
highcut = 40.0
order = 4

sos = signal.butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos')
print(f"Diseño de filtro: Pasa-banda Butterworth (SOS) orden {order}, f_corte=[{lowcut}, {highcut}] Hz, fs={fs} Hz")

# --- INICIALIZACIÓN ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"¡Conexión exitosa en {SERIAL_PORT}!")
    time.sleep(1)
    ser.flushInput()
except serial.SerialException as e:
    print(f"Error al abrir el puerto serie {SERIAL_PORT}: {e}")
    exit()

# ## <-- CAMBIO: 4 Deques para crudos y filtrados
# Las de 'raw' guardan enteros, las de 'filt' guardan flotantes
data_I_raw = deque([0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
data_I_filt = deque([0.0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
data_II_raw = deque([0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)
data_II_filt = deque([0.0] * MAX_DATA_POINTS, maxlen=MAX_DATA_POINTS)

# ## <-- CAMBIO: Estados del filtro (igual que antes)
zi_I = signal.sosfilt_zi(sos)
zi_II = signal.sosfilt_zi(sos)


# ## <-- CAMBIO: CONFIGURACIÓN DE LA GRÁFICA (4 Subplots)
fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 12))
fig.suptitle("Visor de Pruebas: Señal Cruda vs. Filtrada (Online)", fontsize=10)

# ## <-- CAMBIO: 4 Líneas. Crudas en Rojo ('r-'), Filtradas en Azul ('b-')
line_I_raw, = axs[0].plot([], [], 'r-')
line_I_filt, = axs[1].plot([], [], 'b-')
line_II_raw, = axs[2].plot([], [], 'r-')
line_II_filt, = axs[3].plot([], [], 'b-')

lines = (line_I_raw, line_I_filt, line_II_raw, line_II_filt)
x_axis_data = np.arange(MAX_DATA_POINTS)

def init_plot():
    # ## <-- CAMBIO: Límites Y separados para crudo y filtrado
    # ¡AJUSTA ESTOS VALORES!
    ylim_raw = (0, 4095) # Ej: Si tu ADC es 12 bits (0-4095) y está centrado en 2048
    ylim_filt = (-1000, 1000) # La señal filtrada está centrada en 0
    
    axs[0].set_title("Derivación I (Cruda / Raw)")
    axs[0].set_ylabel("Valor ADC")
    axs[0].set_ylim(ylim_raw)
    axs[0].grid(True)

    axs[1].set_title("Derivación I (Filtrada)")
    axs[1].set_ylabel("Amplitud")
    axs[1].set_ylim(ylim_filt)
    axs[1].grid(True)
    
    axs[2].set_title("Derivación II (Cruda / Raw)")
    axs[2].set_ylabel("Valor ADC")
    axs[2].set_ylim(ylim_raw)
    axs[2].grid(True)

    axs[3].set_title("Derivación II (Filtrada)")
    axs[3].set_ylabel("Amplitud")
    axs[3].set_ylim(ylim_filt)
    axs[3].set_xlabel("Muestras")
    axs[3].grid(True)
    
    for ax in axs:
        ax.set_xlim(0, MAX_DATA_POINTS)

    # Inicializamos las líneas con ceros
    line_I_raw.set_data(x_axis_data, data_I_raw)
    line_I_filt.set_data(x_axis_data, data_I_filt)
    line_II_raw.set_data(x_axis_data, data_II_raw)
    line_II_filt.set_data(x_axis_data, data_II_filt)
    
    return lines

# --- FUNCIÓN DE ANIMACIÓN MODIFICADA ---
def update(frame):
    global zi_I, zi_II 
    
    try:
        line_data = ser.readline().decode('utf-8').strip()
        
        if ',' in line_data:
            valor_I, valor_II = map(int, line_data.split(','))
            
            # --- 1. FILTRAR SOLO LA NUEVA MUESTRA ---
            y_I, zi_I = signal.sosfilt(sos, [valor_I], zi=zi_I)
            y_II, zi_II = signal.sosfilt(sos, [valor_II], zi=zi_II)
            
            y_I_sample = y_I[0]
            y_II_sample = y_II[0]

            # --- 2. AÑADIR DATOS CRUDOS Y FILTRADOS A LAS DEQUES ---
            # ## <-- CAMBIO: Añadimos ambos tipos de datos
            data_I_raw.append(valor_I)
            data_I_filt.append(y_I_sample)
            
            data_II_raw.append(valor_II)
            data_II_filt.append(y_II_sample)

            # --- 3. ACTUALIZAR GRÁFICAS ---
            # ## <-- CAMBIO: Actualizamos las 4 líneas
            line_I_raw.set_data(x_axis_data, data_I_raw)
            line_I_filt.set_data(x_axis_data, data_I_filt)
            line_II_raw.set_data(x_axis_data, data_II_raw)
            line_II_filt.set_data(x_axis_data, data_II_filt)

    except (ValueError, UnicodeDecodeError, serial.SerialException):
        pass 
    
    # ## <-- CAMBIO: Retornamos las 4 líneas
    return lines

# --- EJECUCIÓN ---
ani = animation.FuncAnimation(fig, update, init_func=init_plot, blit=True, interval=0)

plt.tight_layout(rect=[0, 0, 1, 0.96]) 
plt.show() 

ser.close()
print("Conexión cerrada.")
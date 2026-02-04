import tkinter as tk
from tkinter import ttk
import numpy as np
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal  # <--- IMPORTANTE: Añadido Scipy

# --- CONFIGURACIÓN SERIE (ESP32) ---
SERIAL_PORT = 'COM4'  # Ajusta según tu sistema (ej. 'COM3' en Windows)
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Conexión exitosa con ESP32")
except Exception as e:
    print(f"Error: {e}")
    print("No se pudo abrir el puerto serie, se usarán señales simuladas")
    ser = None

MAX_POINTS = 500  # Puntos a mostrar

fs = 333.33 
lowcut = 0.5 
highcut = 40.0
order = 4
# Usamos 'sos' (Second-Order Sections) para estabilidad
sos = signal.butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos')
print(f"Filtro: Pasa-banda Butterworth (SOS) orden {order}, f_corte=[{lowcut}, {highcut}] Hz")

# --- VARIABLES GLOBALES ---
# Listas para datos CRUDOS (para gráficas 1 y 2)
data_I_raw = []   
data_II_raw = []  

# Listas para datos FILTRADOS (para cálculos y gráfica 3)
data_I_filt = []
data_II_filt = []

# Estado interno del filtro (para filtrado online)
zi_I = signal.sosfilt_zi(sos)
zi_II = signal.sosfilt_zi(sos)

running = True  # Bandera para el bucle principal
plot3_signal_name = "III"  # Qué mostrar en la gráfica 3 por defecto

# --- FUNCIONES DE PROCESAMIENTO ---

def leer_y_filtrar_senales():
    """
    Lee I y II del puerto serie.
    1. Almacena los datos crudos en data_I_raw, data_II_raw.
    2. Filtra los datos y almacena el resultado en data_I_filt, data_II_filt.
    """
    global data_I_raw, data_II_raw, data_I_filt, data_II_filt, zi_I, zi_II
    
    if ser is None:
        # --- Simulación si no hay ESP32 ---
        t = len(data_I_raw) * 0.05
        valor_I_raw = int(2048 + 1000 * np.sin(t) + np.random.uniform(-50, 50))
        valor_II_raw = int(2048 + 800 * np.sin(t - 0.5) + np.random.uniform(-50, 50))
    else:
        try:
            line_data = ser.readline().decode('utf-8').strip()
            if ',' in line_data:
                valor_I_raw, valor_II_raw = map(int, line_data.split(','))
            else:
                return  # Ignorar línea si no es válida
        except Exception as e:
            print(f"Error leyendo serial: {e}")
            return

    # --- 1. FILTRAR LA NUEVA MUESTRA (ONLINE) ---
    y_I, zi_I = signal.sosfilt(sos, [valor_I_raw], zi=zi_I)
    y_II, zi_II = signal.sosfilt(sos, [valor_II_raw], zi=zi_II)
    
    valor_I_filt = y_I[0]
    valor_II_filt = y_II[0]

    # --- 2. AÑADIR DATOS A LAS LISTAS (CRUDOS Y FILTRADOS) ---
    data_I_raw.append(valor_I_raw)
    data_II_raw.append(valor_II_raw)
    data_I_filt.append(valor_I_filt)
    data_II_filt.append(valor_II_filt)

    # --- 3. MANTENER EL TAMAÑO DE LAS LISTAS ---
    if len(data_I_raw) > MAX_POINTS:
        data_I_raw.pop(0)
        data_II_raw.pop(0)
        data_I_filt.pop(0)
        data_II_filt.pop(0)

def calcular_derivaciones():
    """
    Calcula todas las derivaciones a partir de las listas
    de datos YA FILTRADOS (data_I_filt, data_II_filt).
    """
    # Convertimos a arrays de numpy para cálculo vectorial
    filt_I = np.array(data_I_filt)
    filt_II = np.array(data_II_filt)
    
    derivaciones = {}
    
    # Añadimos las propias I y II filtradas para poder verlas
    derivaciones["I (Filt)"] = filt_I
    derivaciones["II (Filt)"] = filt_II
    
    # Triángulo de Einthoven
    derivaciones["III"] = filt_II - filt_I
    
    # Leyes de Goldberger
    derivaciones["aVR"] = -(filt_I + filt_II) / 2
    derivaciones["aVL"] = filt_I - (filt_II / 2)
    derivaciones["aVF"] = filt_II - (filt_I / 2)
    
    return derivaciones

# --- FUNCIONES DE LA INTERFAZ ---

def actualizar_grafica():
    """Bucle principal que lee, procesa y dibuja."""
    if not running:
        return

    leer_y_filtrar_senales()
    
    if len(data_I_raw) < 2:
        # Esperar a tener al menos algunos datos
        root.after(20, actualizar_grafica)
        return

    # 1. Preparar datos crudos
    x_axis = np.arange(len(data_I_raw))
    
    # 2. Calcular derivaciones (usa datos filtrados internamente)
    derivaciones = calcular_derivaciones()

    # 3. Actualizar líneas de las gráficas
    try:
        # Gráfica 1: RAW I
        linea1.set_data(x_axis, data_I_raw)
        
        # Gráfica 2: RAW II
        linea2.set_data(x_axis, data_II_raw)
        
        # Gráfica 3: Señal seleccionada (calculada a partir de datos filtrados)
        if plot3_signal_name in derivaciones:
            y3 = derivaciones[plot3_signal_name]
            if len(y3) == len(x_axis): # Asegurar que las longitudes coincidan
                linea3.set_data(x_axis, y3)
        
        # 4. Autorango (Ajuste automático del eje Y)
        # Nota: El autorango en datos crudos puede ser muy "ruidoso"
        ax1.relim()
        ax1.autoscale_view(scalex=False, scaley=True)
        
        ax2.relim()
        ax2.autoscale_view(scalex=False, scaley=True)
        
        ax3.relim()
        ax3.autoscale_view(scalex=False, scaley=True)
        
        canvas.draw_idle()
    
    except Exception as e:
        print(f"Error al dibujar: {e}") # Errores durante el ploteo

    # 5. Reprogramar
    root.after(30, actualizar_grafica) # Ajusta el 'after' según sea necesario

def set_plot3(nombre):
    """Función llamada por los botones."""
    global plot3_signal_name
    plot3_signal_name = nombre
    ax3.set_title(f"Señal Calculada (Desde Filtro): {nombre}")

def on_closing():
    """Maneja el cierre limpio de la app."""
    global running
    print("Cerrando aplicación...")
    running = False
    if ser:
        ser.close()
    root.destroy()

# ------------------- INTERFAZ (GUI) -------------------
# (Esta parte es idéntica a la v1 del debugger)

root = tk.Tk()
root.title("Debugger de Señales ECG v2 (Filtro SOS)")
root.geometry("1000x800")

# --- Frame de Gráficas (Arriba) ---
plot_frame = ttk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
fig.tight_layout(pad=3.0)

# Gráfica 1: RAW I
ax1.set_title("RAW Derivación I (Cruda)")
ax1.set_ylabel("Valor ADC")
ax1.grid(True, linestyle='--', alpha=0.6)
linea1, = ax1.plot([], [], color='blue', alpha=0.7)
ax1.set_xlim(0, MAX_POINTS)

# Gráfica 2: RAW II
ax2.set_title("RAW Derivación II (Cruda)")
ax2.set_ylabel("Valor ADC")
ax2.grid(True, linestyle='--', alpha=0.6)
linea2, = ax2.plot([], [], color='red', alpha=0.7)
ax2.set_xlim(0, MAX_POINTS)

# Gráfica 3: Calculada (desde datos filtrados)
ax3.set_title(f"Señal Calculada (Desde Filtro): {plot3_signal_name}")
ax3.set_xlabel("Muestras")
ax3.set_ylabel("Valor Calculado/Filtrado")
ax3.grid(True, linestyle='--', alpha=0.6)
linea3, = ax3.plot([], [], color='green')
ax3.set_xlim(0, MAX_POINTS)

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- Frame de Controles (Abajo) ---
control_frame = ttk.Frame(root)
control_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

# Botones
botones = ["I (Filt)", "II (Filt)", "III", "aVR", "aVL", "aVF"]
for nombre in botones:
    btn = ttk.Button(control_frame, text=nombre, 
                     command=lambda n=nombre: set_plot3(n))
    btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# --- INICIO ---
root.protocol("WM_DELETE_WINDOW", on_closing)
root.after(100, actualizar_grafica)  # Inicia el bucle
root.mainloop()
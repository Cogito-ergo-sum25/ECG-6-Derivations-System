import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import serial
from scipy import signal
from collections import deque

# --- CONFIGURACIÓN SERIE (ESP32) ---
SERIAL_PORT = 'COM4'  # Ajusta según tu sistema
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Conexión exitosa con ESP32")
except:
    print("No se pudo abrir el puerto serie, se usarán señales simuladas")
    ser = None

# --- DISEÑO DEL FILTRO DIGITAL ---
fs = 333.33
lowcut = 0.5 
highcut = 40.0
order = 4
sos = signal.butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos')
print(f"Diseño de filtro: Pasa-banda Butterworth (SOS) orden {order}, f_corte=[{lowcut}, {highcut}] Hz")

# --- VARIABLES GLOBALES ---
current_derivation = None
img_derivacion_actual = None
portada_imgtk = None
MAX_POINTS = 500

zi_I = signal.sosfilt_zi(sos)
zi_II = signal.sosfilt_zi(sos)

data_I_filt = deque([0.0] * MAX_POINTS, maxlen=MAX_POINTS)
data_II_filt = deque([0.0] * MAX_POINTS, maxlen=MAX_POINTS)

simulation_counter = 0

# --- Función para actualizar la imagen (sin cambios) ---
def actualizar_imagen(nombre):
    global img_derivacion_actual, current_derivation
    # Esta función es la clave. Simplemente *establece* la derivación
    # que se calculará en el próximo ciclo de 'actualizar_grafica'
    current_derivation = nombre 

    try:
        total_w = right_frame.winfo_width()
        total_h = right_frame.winfo_height()
        ancho = int(max(1, total_w * 0.65))
        alto = int(max(1, total_h * 0.35))
        if total_w <= 1 or total_h <= 1:
            root.after(100, lambda: actualizar_imagen(nombre))
            return
        img = Image.open(f"{nombre}.png")
        img.thumbnail((ancho, alto), Image.LANCZOS)
        img_derivacion_actual = ImageTk.PhotoImage(img)
        deriv_label.config(image=img_derivacion_actual, text="")
    except:
        deriv_label.config(text=f"{nombre}.png no encontrada", image="", bg="white")

# --- Función para actualizar portada (sin cambios) ---
def actualizar_portada():
    global portada_imgtk
    try:
        total_w = left_frame.winfo_width()
        total_h = left_frame.winfo_height()
        ancho = int(max(1, total_w * 0.8))
        alto = int(max(1, total_h * 0.6))
        if total_w <= 1 or total_h <= 1:
            root.after(100, actualizar_portada)
            return
        img = Image.open("portada.png")
        img.thumbnail((ancho, alto), Image.LANCZOS)
        portada_imgtk = ImageTk.PhotoImage(img)
        portada_label.config(image=portada_imgtk, text="")
    except:
        portada_label.config(text="portada.png no encontrada", image="", bg="white")


# --- CAMBIO 1: leer_senales AHORA SOLO LEE Y FILTRA I y II ---
def leer_senales():
    """Lee I y II, filtra muestra a muestra y actualiza las deques globales."""
    global data_I_filt, data_II_filt, simulation_counter
    global zi_I, zi_II 
    
    # --- Simulación ---
    if ser is None:
        simulation_counter += 1
        ruido_I = np.random.normal(0, 15)
        ruido_II = np.random.normal(0, 15)
        linea_base_I = 100 * np.sin(2 * np.pi * simulation_counter / (MAX_POINTS * 5))
        valor_I = int(2048 + 1000*np.sin(np.pi*simulation_counter/50) + ruido_I + linea_base_I)
        valor_II = int(2048 + 1000*np.sin(np.pi*simulation_counter/30) + ruido_II)
    # --- Lectura Real ---
    else:
        try:
            line_data = ser.readline().decode('utf-8').strip()
            if ',' in line_data:
                valor_I, valor_II = map(int, line_data.split(','))
            else:
                return None # No hay datos nuevos
        except:
            return None # Error de lectura

    # --- 1. FILTRAR SOLO LA NUEVA MUESTRA ---
    y_I, zi_I = signal.sosfilt(sos, [valor_I], zi=zi_I)
    y_II, zi_II = signal.sosfilt(sos, [valor_II], zi=zi_II)
    
    # --- 2. AÑADIR DATOS FILTRADOS A LAS DEQUES ---
    # (La deque descarta automáticamente el valor más antiguo)
    data_I_filt.append(y_I[0])
    data_II_filt.append(y_II[0])
    
    return True # Éxito, hay nuevos datos


# --- CAMBIO 2: actualizar_grafica AHORA HACE EL CÁLCULO ESPEFÍFICO ---
def actualizar_grafica():
    
    # 1. Llama a leer_senales() para actualizar las colas data_I_filt y data_II_filt
    nuevos_datos = leer_senales() 

    # 2. Comprueba si hay datos nuevos Y si el usuario ha seleccionado una derivación
    if nuevos_datos and current_derivation:
        
        # --- CÁLCULO "JUST-IN-TIME" ---
        # Solo ahora, convertimos las deques a arrays de NumPy
        I_filt = np.array(data_I_filt)
        II_filt = np.array(data_II_filt)
        
        # Y AHORA, calculamos SOLAMENTE la derivación que se está viendo
        if current_derivation == "I":
            y = I_filt
        elif current_derivation == "II":
            y = II_filt
        elif current_derivation == "III":
            y = II_filt - I_filt
        elif current_derivation == "aVR":
            y = -(I_filt + II_filt) / 2
        elif current_derivation == "aVL":
            y = I_filt - II_filt / 2
        elif current_derivation == "aVF":
            y = II_filt - I_filt / 2
        else:
            y = I_filt # Un valor por defecto por si acaso

        # --- 3. Graficar ---
        x = np.arange(len(y))
        linea.set_data(x, y)
        
        # Auto-ajuste del eje Y
        if len(y) > 0:
            rango = np.max(y) - np.min(y)
            margen = rango * 0.2
            if margen == 0: margen = 100
            ax.set_ylim(np.min(y) - margen, np.max(y) + margen)
        else:
            ax.set_ylim(-1000, 1000) 
            
        canvas.draw_idle()
        
    # 4. Programar la siguiente actualización
    root.after(50, actualizar_grafica)


# --- Redimensionar (sin cambios) ---
def redimensionar(event=None):
    actualizar_portada()
    if current_derivation:
        actualizar_imagen(current_derivation)
    total_w = right_frame.winfo_width()
    total_h = right_frame.winfo_height()
    if total_w > 10 and total_h > 10:
        fig.set_size_inches(total_w/100.0, (total_h*0.65)/100.0)
        canvas.draw_idle()

# ------------------- INTERFAZ (sin cambios) -------------------
root = tk.Tk()
root.title("Bioinstrumentacion II - Derivaciones de ECG")
root.configure(bg='white')
root.geometry("1200x700")

try:
    icon_img = tk.PhotoImage(file="icono.png")
    root.iconphoto(True, icon_img)
except tk.TclError:
    print("No se pudo cargar 'icono.png'")

root.columnconfigure(0, weight=35)
root.columnconfigure(1, weight=65)
root.rowconfigure(0, weight=1)

left_frame = ttk.Frame(root)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.rowconfigure(0, weight=3)
left_frame.rowconfigure(1, weight=7)
left_frame.columnconfigure(0, weight=1)

buttons_frame = ttk.Frame(left_frame)
buttons_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
buttons_frame.columnconfigure((0,1), weight=1)
buttons_frame.rowconfigure((0,1,2), weight=1)

botones = [
    ("Derivación I", "I"),
    ("Derivación II", "II"),
    ("Derivación III", "III"),
    ("aVR", "aVR"),
    ("aVL", "aVL"),
    ("aVF", "aVF")
]

for i, (texto, nombre) in enumerate(botones):
    btn = ttk.Button(buttons_frame, text=texto, command=lambda n=nombre: actualizar_imagen(n))
    btn.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="nsew")

portada_frame = ttk.Frame(left_frame)
portada_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
portada_frame.columnconfigure(0, weight=1)
portada_frame.rowconfigure(0, weight=1)

portada_label = tk.Label(portada_frame, bg='white')
portada_label.grid(row=0, column=0, sticky="nsew")

right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.rowconfigure(0, weight=65)
right_frame.rowconfigure(1, weight=35)
right_frame.columnconfigure(0, weight=1)

fig, ax = plt.subplots(figsize=(7,3), dpi=100)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_title("Señal ECG Filtrada (Online SOS)")
ax.set_xlabel("Muestras")
ax.set_ylabel("Amplitud (centrada en 0)")
ax.grid(True, color='gray', alpha=0.3)
linea, = ax.plot([], [], color='red')
ax.set_xlim(0, MAX_POINTS)

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

deriv_label = tk.Label(right_frame, bg='white')
deriv_label.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

root.bind("<Configure>", redimensionar)

actualizar_portada()
actualizar_grafica()

root.mainloop()

if ser is not None and ser.is_open:
    ser.close()
    print("Puerto serie cerrado.")
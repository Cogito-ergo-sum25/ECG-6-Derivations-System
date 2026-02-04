# interfaz_ecg
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# --- Simulación de señal ECG ---
def generar_senal_ecg(t):
    return 1.2 * np.sin(2 * np.pi * 1.3 * t) + 0.3 * np.sin(2 * np.pi * 5 * t)

# --- VARIABLES GLOBALES ---
img_derivacion_actual = None
portada_imgtk = None
current_derivation = None

# --- Actualiza la imagen de derivación (con protección contra tamaños 0) ---
def actualizar_imagen(nombre):
    global img_derivacion_actual, current_derivation
    current_derivation = nombre

    try:
        # dimensiones objetivo (65% del ancho total para la imagen de referencia)
        total_w = right_frame.winfo_width()
        total_h = right_frame.winfo_height()
        ancho = int(max(1, total_w * 0.65))   # aseguramos al menos 1
        alto = int(max(1, total_h * 0.35))    # aseguramos al menos 1

        # si aún no hay tamaño real (0 o 1 muy pequeño), reintentar después
        if total_w <= 1 or total_h <= 1:
            root.after(100, lambda: actualizar_imagen(nombre))
            return

        img = Image.open(f"{nombre}.png")
        # Escalamos manteniendo proporción: thumbnail evita deformar
        img.thumbnail((ancho, alto), Image.LANCZOS)
        img_derivacion_actual = ImageTk.PhotoImage(img)
        deriv_label.config(image=img_derivacion_actual, text="")
    except FileNotFoundError:
        deriv_label.config(text=f"{nombre}.png no encontrada", image="", bg="white")
    except Exception as e:
        deriv_label.config(text=f"Error al cargar {nombre}.png: {e}", image="", bg="white")

# --- Actualiza portada (con protección contra tamaños 0) ---
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
    except FileNotFoundError:
        portada_label.config(text="portada.png no encontrada", image="", bg="white")
    except Exception as e:
        portada_label.config(text=f"Error al cargar portada.png: {e}", image="", bg="white")

# --- Actualiza la gráfica periódicamente (simulada) ---
def actualizar_grafica():
    t = np.linspace(0, 2, 500)
    y = generar_senal_ecg(t)
    linea.set_ydata(y)
    canvas.draw_idle()
    root.after(100, actualizar_grafica)

# --- Redimensiona contenido al cambiar la ventana (protecciones incluidas) ---
def redimensionar(event=None):
    # Actualiza portada y derivación (se reintentarán si aún no hay tamaño)
    actualizar_portada()
    if current_derivation:
        actualizar_imagen(current_derivation)

    # Escalar figura de Matplotlib según el espacio disponible
    total_w = right_frame.winfo_width()
    total_h = right_frame.winfo_height()
    if total_w > 10 and total_h > 10:
        # Queremos que la figura ocupe el 65% del alto del right_frame (la parte superior)
        fig.set_size_inches(total_w / 100.0, (total_h * 0.65) / 100.0)
        canvas.draw_idle()

# -------------------- Construcción de la UI --------------------
root = tk.Tk()
root.title("Bioinstrumentacion II - Derivaciones de ECG")
root.configure(bg='white')
root.geometry("1200x700")

# Estructura general: 35% izquierdo / 65% derecho
root.columnconfigure(0, weight=35)
root.columnconfigure(1, weight=65)
root.rowconfigure(0, weight=1)

# ----- LADO IZQUIERDO -----
left_frame = ttk.Frame(root)
left_frame.grid(row=0, column=0, sticky="nsew")
# En el left: 30% alto botones / 70% alto portada -> implementado con weight 3 / 7
left_frame.rowconfigure(0, weight=3)  # botones (30%)
left_frame.rowconfigure(1, weight=7)  # portada (70%)
left_frame.columnconfigure(0, weight=1)

# Subframe botones (centrados)
buttons_frame = ttk.Frame(left_frame)
buttons_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
buttons_frame.columnconfigure((0, 1), weight=1)
buttons_frame.rowconfigure((0, 1, 2), weight=1)

botones = [
    ("Derivación I", "I"),
    ("Derivación II", "II"),
    ("Derivación III", "III"),
    ("aVR", "aVR"),
    ("aVL", "aVL"),
    ("aVF", "aVF"),
]

for i, (texto, nombre) in enumerate(botones):
    btn = ttk.Button(buttons_frame, text=texto, command=lambda n=nombre: actualizar_imagen(n))
    btn.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")

# Subframe portada (centrada)
portada_frame = ttk.Frame(left_frame)
portada_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
portada_frame.columnconfigure(0, weight=1)
portada_frame.rowconfigure(0, weight=1)

portada_label = tk.Label(portada_frame, bg='white')
portada_label.grid(row=0, column=0, sticky="nsew")

# ----- LADO DERECHO -----
right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=1, sticky="nsew")
# En el right: 65% alto gráfica / 35% alto imagen de referencia -> weight 65 / 35
right_frame.rowconfigure(0, weight=65)
right_frame.rowconfigure(1, weight=35)
right_frame.columnconfigure(0, weight=1)

# Gráfica (arriba en right_frame)
fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_title("Señal ECG Simulada", fontsize=12)
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Amplitud (mV)")
ax.grid(True, color='gray', alpha=0.3)
t = np.linspace(0, 2, 500)
y = generar_senal_ecg(t)
linea, = ax.plot(t, y, color='red', linewidth=1.2)
ax.set_ylim(-2, 2)

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# Imagen de derivación (abajo en right_frame)
deriv_label = tk.Label(right_frame, bg='white')
deriv_label.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

# Eventos y arranque
root.bind("<Configure>", redimensionar)

# Inicializamos (si no hay tamaños aún, las funciones reintentaran)
actualizar_portada()
actualizar_grafica()

root.mainloop()

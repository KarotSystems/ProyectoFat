import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os, json
from datetime import datetime

os.makedirs("fat_storage", exist_ok=True)
os.makedirs("blocks", exist_ok=True)

Fat_Destino = "fat_storage/fat.json"
Usuario = "admin"  # Usuario por defecto

#Funciones
def crear_carpeta():
    """Crea la tabla FAT principal si aún no existe."""
    if not os.path.exists(Fat_Destino):
        with open(Fat_Destino, "w") as f:
            json.dump({"files": {}}, f, indent=4)

def cargar_fat():
    """Carga el contenido actual de la tabla FAT (fat.json)."""
    crear_carpeta()
    with open(Fat_Destino, "r") as f:
        return json.load(f)

def guardar_fat(fat):
    """Guarda los cambios realizados a la tabla FAT."""
    with open(Fat_Destino, "w") as f:
        json.dump(fat, f, indent=4)

def segmentar_bloques(texto, nombre_archivo):
    """
    Divide el contenido del archivo en bloques de 20 caracteres,
    simulando la estructura FAT. Cada bloque se almacena en un JSON
    con puntero al siguiente bloque (enlace encadenado).
    """
    bloques = [texto[i:i+20] for i in range(0, len(texto), 20)]
    rutas = []
    for i, bloque in enumerate(bloques):
        ruta = f"blocks/{nombre_archivo}_block{i}.json"
        rutas.append(ruta)
        with open(ruta, "w") as f:
            json.dump({
                "datos": bloque,
                "siguiente": None if i == len(bloques)-1 else f"blocks/{nombre_archivo}_block{i+1}.json",
                "eof": i == len(bloques)-1
            }, f, indent=4)
    return rutas[0]  # Retorna la ruta del primer bloque (inicio de la cadena FAT)

#Funciones para Fat
def crear_archivo_gui():
    """Permite crear un nuevo archivo desde una ventana emergente."""
    nombre = simpledialog.askstring("Crear Archivo", "Nombre del archivo:")
    if not nombre:
        return

    contenido = simpledialog.askstring("Contenido", "Escribe el contenido del archivo:")
    if not contenido:
        return

    fat = cargar_fat()
    ruta_inicial = segmentar_bloques(contenido, nombre)

    # Se registran los metadatos en la tabla FAT
    fat["files"][nombre] = {
        "ruta_inicial": ruta_inicial,
        "papelera": False,
        "size": len(contenido),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "modified": None,
        "deleted": None,
        "owner": Usuario,
        "permisos": {Usuario: ["lectura", "escritura"]}  # El propietario tiene todos los permisos
    }
    guardar_fat(fat)
    messagebox.showinfo("Éxito", f"Archivo '{nombre}' creado correctamente.")
    actualizar_listas()

def abrir_archivo_gui():
    """Abre un archivo y muestra su contenido completo (concatenando los bloques FAT)."""
    nombre = simpledialog.askstring("Abrir Archivo", "Nombre del archivo:")
    if not nombre:
        return
    fat = cargar_fat()
    datos = fat["files"].get(nombre)

    # Validaciones básicas
    if not datos or datos["papelera"]:
        messagebox.showerror("Error", "Archivo no disponible.")
        return
    if Usuario not in datos["permisos"] or "lectura" not in datos["permisos"][Usuario]:
        messagebox.showerror("Permiso denegado", "No tienes permiso de lectura.")
        return

    # Se leen todos los bloques encadenados
    ruta = datos["ruta_inicial"]
    contenido = []
    while ruta:
        with open(ruta, "r") as f:
            bloque = json.load(f)
            contenido.append(bloque["datos"])
            ruta = bloque["siguiente"]

    # Se muestra el contenido completo reconstruido
    messagebox.showinfo("Contenido del Archivo", "".join(contenido))

def modificar_archivo_gui():
    """Permite modificar el contenido de un archivo existente."""
    nombre = simpledialog.askstring("Modificar Archivo", "Archivo a modificar:")
    if not nombre:
        return
    fat = cargar_fat()
    datos = fat["files"].get(nombre)

    if not datos or datos["papelera"]:
        messagebox.showerror("Error", "Archivo no disponible.")
        return
    if Usuario not in datos["permisos"] or "escritura" not in datos["permisos"][Usuario]:
        messagebox.showerror("Permiso denegado", "No tienes permiso de escritura.")
        return

    # Eliminación de bloques antiguos (simulando reescritura)
    ruta = datos["ruta_inicial"]
    while ruta:
        with open(ruta, "r") as f:
            bloque = json.load(f)
        os.remove(ruta)
        ruta = bloque["siguiente"]

    # Nuevo contenido
    nuevo_contenido = simpledialog.askstring("Modificar", "Nuevo contenido del archivo:")
    if not nuevo_contenido:
        return

    nueva_ruta = segmentar_bloques(nuevo_contenido, nombre)
    datos["ruta_inicial"] = nueva_ruta
    datos["size"] = len(nuevo_contenido)
    datos["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    guardar_fat(fat)

    messagebox.showinfo("Éxito", "Archivo modificado correctamente.")
    actualizar_listas()

def mover_a_papelera_gui():
    """Marca un archivo como eliminado (no lo borra físicamente)."""
    nombre = simpledialog.askstring("Eliminar", "Archivo a mover a la papelera:")
    if not nombre:
        return
    fat = cargar_fat()
    if nombre in fat["files"]:
        fat["files"][nombre]["papelera"] = True
        fat["files"][nombre]["deleted"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        guardar_fat(fat)
        messagebox.showinfo("Éxito", f"Archivo '{nombre}' movido a la papelera.")
        actualizar_listas()
    else:
        messagebox.showerror("Error", "El archivo no existe.")

def recuperar_archivo_gui():
    """Restaura un archivo desde la papelera."""
    nombre = simpledialog.askstring("Recuperar", "Archivo a recuperar:")
    if not nombre:
        return
    fat = cargar_fat()
    if nombre in fat["files"]:
        fat["files"][nombre]["papelera"] = False
        fat["files"][nombre]["deleted"] = None
        guardar_fat(fat)
        messagebox.showinfo("Éxito", f"Archivo '{nombre}' recuperado desde la papelera.")
        actualizar_listas()
    else:
        messagebox.showerror("Error", "El archivo no existe.")

def asignar_permisos_gui():
    """Permite al propietario asignar permisos de lectura o escritura a otro usuario."""
    nombre = simpledialog.askstring("Permisos", "Nombre del archivo:")
    usuario = simpledialog.askstring("Permisos", "Usuario a asignar:")
    tipo = simpledialog.askstring("Permisos", "Permiso (lectura/escritura):")
    fat = cargar_fat()
    datos = fat["files"].get(nombre)
    if not datos:
        messagebox.showerror("Error", "Archivo no encontrado.")
        return
    if datos["owner"] != Usuario:
        messagebox.showerror("Error", "Solo el propietario puede asignar permisos.")
        return
    if usuario not in datos["permisos"]:
        datos["permisos"][usuario] = []
    if tipo not in datos["permisos"][usuario]:
        datos["permisos"][usuario].append(tipo)
    guardar_fat(fat)
    messagebox.showinfo("Permisos", f"Permiso '{tipo}' asignado a '{usuario}'.")

#Tablas de interfaz
def actualizar_listas():
    """Actualiza las tablas de archivos activos y papelera en la interfaz."""
    fat = cargar_fat()
    for tabla in [tabla_activos, tabla_papelera]:
        for i in tabla.get_children():
            tabla.delete(i)

    for archivo, datos in fat["files"].items():
        if not datos["papelera"]:
            tabla_activos.insert("", "end", values=(archivo, datos["size"], datos["owner"], datos["created"]))
        else:
            tabla_papelera.insert("", "end", values=(archivo, datos["deleted"], datos["owner"]))

#interfaz
root = tk.Tk()
root.title("Sistema de Archivos FAT (Simulación)")
root.geometry("900x600")

# Cuaderno de pestañas (Notebook/tabla)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

frame1 = ttk.Frame(notebook)
notebook.add(frame1, text="Archivos Activos")

#Tabla principal
tabla_activos = ttk.Treeview(frame1, columns=("Nombre", "Tamaño", "Owner", "Creado"), show="headings")
for col, ancho in zip(("Nombre", "Tamaño", "Owner", "Creado"), (200, 100, 150, 150)):
    tabla_activos.heading(col, text=col)
    tabla_activos.column(col, width=ancho, anchor="center")
tabla_activos.pack(expand=True, fill="both", padx=10, pady=10)

#Papelera
frame2 = ttk.Frame(notebook)
notebook.add(frame2, text="Papelera")

tabla_papelera = ttk.Treeview(frame2, columns=("Nombre", "Eliminado", "Owner"), show="headings")
for col, ancho in zip(("Nombre", "Eliminado", "Owner"), (200, 150, 150)):
    tabla_papelera.heading(col, text=col)
    tabla_papelera.column(col, width=ancho, anchor="center")
tabla_papelera.pack(expand=True, fill="both", padx=10, pady=10)

#Sección para botones
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=10)

# Cada botón ejecuta una función del sistema FAT
botones = [
    ("Crear Archivo", crear_archivo_gui),
    ("Abrir Archivo", abrir_archivo_gui),
    ("Modificar Archivo", modificar_archivo_gui),
    ("Eliminar (Papelera)", mover_a_papelera_gui),
    ("Recuperar Archivo", recuperar_archivo_gui),
    ("Asignar Permisos", asignar_permisos_gui),
    ("Actualizar", actualizar_listas),
    ("Salir", root.quit)
]
for texto, comando in botones:
    ttk.Button(frame_botones, text=texto, command=comando, width=20).pack(side="left", padx=5)

# Carga inicial de los datos
actualizar_listas()

# Inicia la interfaz
root.mainloop()
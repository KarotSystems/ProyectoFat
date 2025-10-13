import os, json
from datetime import datetime

#Inicialización
os.makedirs("fat_storage", exist_ok=True)
os.makedirs("blocks", exist_ok=True)
Fat_Destino = "fat_storage/fat.json"

#Inicializar tabla FAT si no existe
def crear_carpeta():
    if not os.path.exists(Fat_Destino):
        with open(Fat_Destino, "w") as f:
            json.dump({"files": {}}, f, indent=4)

#Usuario actual (puedes cambiarlo para pruebas)
Usuario = "admin"

def segmentar_bloques(texto, nombre_archivo):
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

    return rutas[0]  # ruta inicial

def crear_archivo(nombre):
    texto = input("Contenido (FIN para terminar):\n")
    contenido = []
    while texto != "FIN":
        contenido.append(texto)
        texto = input()
    texto_completo = " ".join(contenido)

    ruta_inicial = segmentar_bloques(texto_completo, nombre)
    size = len(texto_completo)

    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    fat["files"][nombre] = {
        "ruta_inicial": ruta_inicial,
        "papelera": False,
        "size": size,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "modified": None,
        "deleted": None,
        "owner": Usuario,
        "permisos": {Usuario: ["lectura", "escritura"]}
    }

    with open(Fat_Destino, "w") as f:
        json.dump(fat, f, indent=4)

    print(f"Archivo '{nombre}' creado.")

def Listar_archivos():
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    print("\n=== Archivos activos ===")
    for archivo, datos in fat["files"].items():
        if not datos["papelera"]:
            print(f"{archivo} | Tamaño: {datos['size']} | Owner: {datos['owner']}")

def Mostrar_papelera():
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    print("\n=== Papelera ===")
    for archivo, datos in fat["files"].items():
        if datos["papelera"]:
            print(f"{archivo} | Eliminado: {datos['deleted']}")

def abrir_archivo(nombre):
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    datos = fat["files"].get(nombre)
    if not datos or datos["papelera"]:
        print("Archivo no disponible.")
        return
    
def Modificar_archivo(nombre):
    pass

def mover_a_papelera(nombre):
    pass

def Recuperar_desde_papelera(nombre):
    pass

def Asignar_permisos(nombre):
    pass

def Crear_nuevo_usuario(nombre):
    pass

while True:
    print("\n--- Menú ---")
    print("1. Crear archivo")
    print("2. Listar archivos")
    print("3. Mostrar papelera")
    print("4. Abrir archivo")
    print("5. Modificar archivo")
    print("6. Eliminar (mover a papelera)")
    print("7. Recuperar desde papelera")
    print("8. Asignar permisos (owner/creador)")
    print("9. Salir")
    opcion = input("Elige una opción: ")

    if opcion == "1":
        nombre = input("Nombre del archivo: ")
        crear_archivo(nombre)
    elif opcion == "2":
        Listar_archivos()

    elif opcion == "3":
        Mostrar_papelera()

    elif opcion == "4":
        nombre = input("Archivo a abrir: ")
        abrir_archivo(nombre)

    elif opcion == "5":
        nombre = input("Archivo a modificar: ")
        Modificar_archivo(nombre)

    elif opcion == "6":
        nombre = input("Archivo a eliminar: ")
        mover_a_papelera(nombre)

    elif opcion == "7":
        nombre = input("Archivo a recuperar: ")
        Recuperar_desde_papelera(nombre)

    elif opcion == "8":
        nombre = input("Archivo: ")
        usuario = input("Usuario a asignar: ")
        permiso = input("Permiso (lectura/escritura): ")
        Asignar_permisos(nombre, usuario, permiso)

    elif opcion == "9":
        print("Saliendo del sistema")
        break

    else:
        print("Opción inválida")
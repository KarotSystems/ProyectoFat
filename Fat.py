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
    os.makedirs("blocks", exist_ok=True)

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
    if os.path.exists(f"fat_storage/{nombre}"):
        with open(f"fat_storage/{nombre}", "r") as f:
            print("\nContenido actual:\n", f.read())
    else:
        with open(f"fat_storage/{nombre}", "w") as f:
            print("Escribe el texto (finaliza con 'FIN'): ")
            texto = []
            while True:
                contenido = input()
                if contenido == "FIN":
                    break
            texto.append(contenido + "\n")
            f.writelines(texto)

    print(f"Archivo '{nombre}' creado con éxito.")

def Listar_archivos():
    with open(f"fat_storage/{nombre}", "r") as f:
        fat = json.load(f)

    print("\n=== Archivos activos ===")
    for archivo, datos in fat["files"].items():
        if not datos["papelera"]:
            print(f"{archivo} | Tamaño: {datos['size']} | Owner: {datos['owner']}")

def Mostrar_papelera():
    with open(f"fat_storage/{nombre}", "r") as f:
        fat = json.load(f)

    print("\n=== Papelera ===")
    for archivo, datos in fat["files"].items():
        if datos["papelera"]:
            print(f"{archivo} | Eliminado: {datos['deleted']}")

def abrir_archivo(nombre):
    with open(f"fat_storage/{nombre}", "r") as f:
        fat = json.load(f)
        
    print("\n=== Archivos activos ===")
    for archivo, datos in fat["files"].items():
        if not datos["papelera"]:
            print(f"{archivo} | Tamaño: {datos['size']} | Owner: {datos['owner']}")

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
    print("9. Crear nuevo usuario")
    print("0. Salir")
    opcion = input("Elige una opción: ")

    if opcion == "1":
        nombre = input("Nombre del archivo: ")
        if not nombre.lower().endswith(".json"): # Si no escribe .txt, se agrega automáticamente
            nombre += ".json"
        print("Ruta Actual: ", os.getcwd())
        print("Archivo aqui: ", os.listdir())
        print("¿Existe? ", os.path.exists(nombre))
        print("Tamaño: ", os.path.getsize(nombre), " bytes")
        
    elif opcion == "2":
        print("Escribe el texto (finaliza con 'FIN'): ")
        texto = []
        while True:
            contenido = input()
            if contenido == "FIN":
                break

            texto.append(contenido + "\n")
        with open(nombre, "w") as f:
            f.writelines(texto)

    elif opcion == "3":
        print("Escribe el texto a agregar (finaliza con 'FIN'): ")
        texto = []
        while True:
            contenido = input()
            if contenido == "FIN":
                break

            texto.append(contenido + "\n")
        with open(nombre, "a") as f:
            f.writelines(texto)

    elif opcion == "4":
        with open(nombre, "r") as f:
            lineas = f.readlines()

        for i, linea in enumerate(lineas, 1):
            print(f"{i}: {linea}")

        try:
            num = int(input("\nNúmero de línea a editar: "))
            if num <= len(lineas): 
                texto = input("Nuevo contenido: ") + "\n"
                lineas[num - 1] = texto # Restamos 1 porque son base 0 (0=1,1=2, etc)
                with open(nombre, "w") as f:
                    f.writelines(lineas)
                print("Línea editada correctamente.")
            else:
                print("Número de línea inválido.")
        except ValueError:
            print("Debes ingresar un número válido.")

    elif opcion == "5":
        copia = shutil.copy(f"{nombre}", f"{nombre}_copia.txt")
        print(f"Copia creada: {copia}")

    elif opcion == "6":
        pass

    elif opcion == "7":
        pass

    elif opcion == "8":
        pass

    elif opcion == "9":
        pass

    elif opcion == "0":
        print("Saliendo del sistema")
        break

    else:
        print("Opción inválida")
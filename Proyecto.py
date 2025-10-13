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

# Divide el contenido en bloques de 20 caracteres y los guarda en archivos JSON
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

#Crea un nuevo archivo
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

    #formato fat segun el pdf
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

#Muestra todos los archivos
def Listar_archivos():
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    #archivos activos si no estan en la papelera
    print("\n=== Archivos activos ===")
    for archivo, datos in fat["files"].items():
        if not datos["papelera"]:
            print(f"{archivo} | Tamaño: {datos['size']} | Owner: {datos['owner']}")

#Archivos que están en la papelera
def Mostrar_papelera():
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    #archivos si estan en la papelera
    print("\n=== Papelera ===")
    for archivo, datos in fat["files"].items():
        if datos["papelera"]:
            print(f"{archivo} | Eliminado: {datos['deleted']}")

#Muestra su contenido
def abrir_archivo(nombre):
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    datos = fat["files"].get(nombre)
    if not datos or datos["papelera"]:
        print("Archivo no disponible.")
        return

    #Valida los permisos del usuario
    if usuario not in datos["permisos"] or "lectura" not in datos["permisos"][usuario]:
        print("No tienes permiso de lectura.")
        return

    ruta = datos["ruta_inicial"]
    contenido = []

    #busca la ruta del fat que se guardo en json
    while ruta:
        with open(ruta, "r") as f:
            bloque = json.load(f)
            contenido.append(bloque["datos"])
            ruta = bloque["siguiente"]

    print("\nContenido del archivo:")
    print("".join(contenido))

#Modifica el contenido
def Modificar_archivo(nombre):
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    datos = fat["files"].get(nombre)
    if not datos or datos["papelera"]:
        print("Archivo no disponible.")
        return

    #Valida los permisos del usuario
    if usuario not in datos["permisos"] or "escritura" not in datos["permisos"][usuario]:
        print("No tienes permiso de escritura.")
        return

    #Eliminar bloques antiguos
    ruta = datos["ruta_inicial"]
    while ruta:
        with open(ruta, "r") as f:
            bloque = json.load(f)
        os.remove(ruta)
        ruta = bloque["siguiente"]

    #Crear nuevos bloques
    nuevo_texto = input("Nuevo contenido (FIN para terminar):\n")
    contenido = []
    while nuevo_texto != "FIN":
        contenido.append(nuevo_texto)
        nuevo_texto = input()
    texto_completo = " ".join(contenido)

    nueva_ruta = segmentar_bloques(texto_completo, nombre)
    datos["ruta_inicial"] = nueva_ruta
    datos["size"] = len(texto_completo)
    datos["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(Fat_Destino, "w") as f:
        json.dump(fat, f, indent=4)

    print("Archivo modificado.")

#Mueve un archivo a la papelera 
def mover_a_papelera(nombre):
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    if nombre in fat["files"]:
        fat["files"][Fat_Destino]["papelera"] = True
        fat["files"][Fat_Destino]["deleted"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(Fat_Destino, "w") as f:
            json.dump(fat, f, indent=4)
        print("Archivo movido a la papelera.")

#Recupera un archivo
def Recuperar_desde_papelera(nombre):
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    if nombre in fat["files"]:
        fat["files"][Fat_Destino]["papelera"] = False
        fat["files"][Fat_Destino]["deleted"] = None
        with open(Fat_Destino, "w") as f:
            json.dump(fat, f, indent=4)
        print("Archivo recuperado.")

#Asigna permisos de lectura/escritura
def Asignar_permisos(nombre, usuario, tipo_permiso):
    with open(Fat_Destino, "r") as f:
        fat = json.load(f)

    #Si el user/owner no es el owner registrado
    datos = fat["files"].get(nombre)
    if not datos or datos["owner"] != usuario:
        print("Solo el owner puede asignar permisos.")
        return

    #si no tiene owner, se le asigna algunos permisos
    if usuario not in datos["permisos"]:
        datos["permisos"][usuario] = []

    if tipo_permiso not in datos["permisos"][usuario]:
        datos["permisos"][usuario].append(tipo_permiso)

    with open(Fat_Destino, "w") as f:
        json.dump(fat, f, indent=4)

    print(f"Permiso '{tipo_permiso}' asignado a '{usuario}'.")

#Interfas del sistema
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
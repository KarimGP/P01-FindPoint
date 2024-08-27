import json
import os

# Ruta del archivo JSON
FILENAME = 'ratings.json'

# Cargar datos desde el archivo JSON
def cargar_datos():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            return json.load(file)
    else:
        print(f"Error: File not found {FILENAME}")
        return {'arc': {}, 'art': {}, 'us': {}}  # Devolver un diccionario vacío si no existe el archivo

# Guardar datos en el archivo JSON
def guardar_datos(datos):
    with open(FILENAME, 'w') as file:
        json.dump(datos, file, indent=4)

# Función para añadir un nuevo lugar (modificada para recibir parámetros)
def add_place(new_point, specify):
    datos = cargar_datos()

    if new_point.isalpha() and specify in ['arc', 'art', 'us']:
        nueva_calificacion = {"rating": []}

        if new_point not in datos[specify]:  # Verificar si el lugar ya existe
            datos[specify][new_point] = nueva_calificacion
            guardar_datos(datos)
            return f"The new place '{new_point}' has been added with ratings {nueva_calificacion['rating']}."
        else:
            return f"The point '{new_point}' already exists in the '{specify}' category."
    else:
        return "Invalid input. Please enter a valid place name and category."

# Función para eliminar un lugar existente (modificada para recibir parámetros)
def delete_place(delete_point, specify):
    datos = cargar_datos()

    if specify in datos:
        if delete_point in datos[specify]:
            del datos[specify][delete_point]
            guardar_datos(datos)
            return f"'{delete_point}' has been deleted from the '{specify}' category."
        else:
            return f"Error: The point '{delete_point}' does not exist in the '{specify}' category."
    else:
        return "Invalid category. Please choose between 'arc', 'art', or 'us'."

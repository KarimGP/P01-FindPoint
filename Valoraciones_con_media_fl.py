import json
import os
import unicodedata

# Ruta del archivo JSON
FILENAME = 'ratings.json'

# Cargar datos desde el archivo JSON
def cargar_datos():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            return json.load(file)
    else:
        print(f"Error: File not found {FILENAME}")
        return None

# Guardar datos en el archivo JSON
def guardar_datos(datos):
    with open(FILENAME, 'w') as file:
        json.dump(datos, file, indent=4)

# Función para eliminar acentos y diéresis
def quitar_acentos_y_diereses(texto):
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')

# Función para actualizar la calificación (modificada para aceptar parámetros)
def actualizar_rating(diccionario, lugar, nueva_calificacion):
    lugar_normalizado = quitar_acentos_y_diereses(lugar).lower()
    
    # Normalizar las claves del diccionario
    claves_normalizadas = {quitar_acentos_y_diereses(clave).lower(): clave for clave in diccionario.keys()}
    
    # Buscar la clave correspondiente en el diccionario normalizado
    lugar_original = claves_normalizadas.get(lugar_normalizado)
    
    if lugar_original:
        diccionario[lugar_original]["rating"].append(nueva_calificacion)
        return f"Rating {nueva_calificacion} has been added to {lugar_original}."
    else:
        return f"{lugar} is not found in the dictionary."

# Función para calcular la media de un lugar específico (modificada para devolver resultados)
def calcular_media(diccionario, lugar):
    lugar_normalizado = quitar_acentos_y_diereses(lugar).lower()
    # Normalizar las claves del diccionario
    claves_normalizadas = {quitar_acentos_y_diereses(clave).lower(): clave for clave in diccionario.keys()}
    # Buscar la clave correspondiente en el diccionario normalizado
    lugar_original = claves_normalizadas.get(lugar_normalizado)

    if lugar_original in diccionario:
        ratings = diccionario[lugar_original]["rating"]
        if ratings:
            diccionario[lugar_original]["media"] = sum(ratings) / len(ratings)
            new_media = diccionario[lugar_original]["media"]
            return f"Average rating of {lugar_original}: {new_media:.1f}"
        else:
            diccionario[lugar_original]["media"] = 0
            return f"No ratings available for {lugar_original}."
    else:
        return f"{lugar} is not found in the dictionary."

# Función principal adaptada para Flask
def value_med(category, place, new_rating):
    datos = cargar_datos()

    if category in ['arc', 'art', 'us'] and place:
        result_rating = actualizar_rating(datos[category], place, new_rating)
        result_media = calcular_media(datos[category], place)
        guardar_datos(datos)
        return f"{result_rating} {result_media}"
    else:
        return "Invalid category or place name."

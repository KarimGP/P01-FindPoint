import json
import os
import random  # Necesario para usar random.choice()

# Ruta del archivo JSON
FILENAME = 'ratings.json'

# Cargar los datos desde el archivo JSON
def cargar_datos():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as file:
            return json.load(file)
    else:
        print(f"Error: File not found {FILENAME}")
        return None

# Elegir categoría (modificado para aceptar un parámetro)
def choose(choosen_type):
    if choosen_type in ['arc', 'art', 'us']:
        return choosen_type
    else:
        return None

# Proponer un punto de interés (modificado para devolver resultados)
def proposal_point(choosen_type, data):
    if choosen_type in data:
        proposed_list = list(data[choosen_type].keys())
        if proposed_list:  # Verificar si hay puntos disponibles
            interesting_point = random.choice(proposed_list)
            return interesting_point
        else:
            return None
    else:
        return None

# Repetir la elección hasta que se acepte un punto de interés (simplificado)
def repeat_chasing(interesting_point, data):
    if interesting_point not in score_point:
        score_point[interesting_point] = 0

    return interesting_point

# Inicializar el diccionario de puntos de puntuación
score_point = {}

# Función principal de elección y procesamiento de puntos adaptada
def choosin(choosen_type, data):
    if data:
        chosen_type = choose(choosen_type)
        if chosen_type:
            interesting_point = proposal_point(chosen_type, data)
            if interesting_point:
                return repeat_chasing(interesting_point, data)
    return None

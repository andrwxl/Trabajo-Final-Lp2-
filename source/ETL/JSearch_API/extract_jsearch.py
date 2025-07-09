import requests
import json
import os
import time
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from config import APP_KEY_JSearch

def obtener_ofertas_jsearch(query, country_code='us', pagina=1):
    url = "https://jsearch.p.rapidapi.com/search"

    # Se añade el parámetro 'country' a la búsqueda.
    querystring = {
        "query": query,
        "page": str(pagina),
        "num_pages": "1",
        "country": country_code
    }

    headers = {
        "x-rapidapi-key": APP_KEY_JSearch,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    print(f"Realizando petición a JSearch para: '{query}' (País: {country_code.upper()}) (Página {pagina})...")
    
    try:
        respuesta = requests.get(url, headers=headers, params=querystring)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la API de JSearch: {e}"

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":

    PAISES_A_BUSCAR = [
        {'nombre_en': 'United States', 'codigo': 'us'},
        {'nombre_en': 'Mexico', 'codigo': 'mx'},
        {'nombre_en': 'Colombia', 'codigo': 'co'},
        {'nombre_en': 'Chile', 'codigo': 'cl'},
        {'nombre_en': 'Argentina', 'codigo': 'ar'},
        {'nombre_en': 'Brazil', 'codigo': 'br'},
    ]

    # 2. Lista de roles o tecnologías a buscar en cada país
    TERMINOS_DE_BUSQUEDA = [
        "Data Scientist",
        "Data Analyst",
        "Software Developer",
        "Python Developer",
        "Frontend Developer",
        "Backend Developer",
        "DevOps Engineer"
    ]
    
    # --- FIN DE LA NUEVA ESTRUCTURA ---

    todos_los_resultados = []

    print("--- Iniciando extracción masiva y comparativa de datos de JSearch ---")
    
    # 3. Bucle anidado para buscar cada término en cada país
    for pais_info in PAISES_A_BUSCAR:
        pais_codigo = pais_info['codigo']
        pais_nombre = pais_info['nombre_en']
        
        for termino in TERMINOS_DE_BUSQUEDA:
            # Construimos la query combinando el término y el nombre del país en inglés
            query_actual = f"{termino} in {pais_nombre}"
            pagina_actual = 1
            
            print(f"\n--- Iniciando búsqueda para '{query_actual}' ---")
            
            while True:
                datos_pagina = obtener_ofertas_jsearch(query_actual, pais_codigo, pagina=pagina_actual)
                
                if isinstance(datos_pagina, str):
                    print(datos_pagina)
                    break

                if datos_pagina and 'data' in datos_pagina and datos_pagina['data']:
                    resultados = datos_pagina['data']
                    todos_los_resultados.extend(resultados)
                    print(f"Página {pagina_actual}: Se obtuvieron {len(resultados)} resultados.")
                    
                    if pagina_actual >= 5: # Limitamos a 5 páginas por búsqueda para no exceder los límites
                        print("Límite de páginas alcanzado para esta búsqueda.")
                        break
                    
                    pagina_actual += 1
                    time.sleep(0.1)
                else:
                    print("No se encontraron más resultados. Finalizando esta búsqueda.")
                    break
    
    if todos_los_resultados:
        print(f"\n--- Proceso completado. Total de ofertas extraídas: {len(todos_los_resultados)} ---")
        ruta_salida = os.path.join('datos', 'crudos')
        os.makedirs(ruta_salida, exist_ok=True)
        nombre_archivo = "jsearch_datos_crudos.json"
        
        with open(os.path.join(ruta_salida, nombre_archivo), 'w', encoding='utf-8') as f:
            json.dump(todos_los_resultados, f, ensure_ascii=False, indent=4)
        
        print(f"Todos los datos han sido guardados en: '{os.path.join(ruta_salida, nombre_archivo)}'")
    else:
        print("\nNo se extrajo ningún dato de la API en ninguna de las búsquedas.")

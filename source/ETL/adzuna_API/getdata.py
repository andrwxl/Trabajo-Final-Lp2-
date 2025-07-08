import requests
import json
import os
import time
from config import APP_ID, APP_KEY

def obtener_ofertas_adzuna(que_buscar, donde_buscar, pais='us', pagina=1):
    # Construimos la URL base usando el código del país.
    url_endpoint = f"https://api.adzuna.com/v1/api/jobs/{pais}/search/{pagina}"
    
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'what': que_buscar,
        'where': donde_buscar,
        'results_per_page': 50
    }
    
    print(f"Petición a Adzuna: Buscando '{que_buscar}' en '{donde_buscar}' ({pais.upper()}) - Página {pagina}...")
    
    try:
        respuesta = requests.get(url_endpoint, params=params)
        print(f"URL final construida: {respuesta.url}") # Imprimimos la URL para depurar
        respuesta.raise_for_status()
        return respuesta.json()
        
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la API de Adzuna: {e}"

if __name__ == "__main__":
    busquedas = [
        {'que': 'python developer', 'donde': 'california', 'pais': 'us'},
        {'que': 'data analyst', 'donde': 'new york', 'pais': 'us'},
        {'que': 'react developer', 'donde': 'texas', 'pais': 'us'},
    ]

    todos_los_resultados = []

    print("--- Iniciando extracción masiva de datos de Adzuna ---")
    
    for busqueda in busquedas:
        que = busqueda['que']
        donde = busqueda['donde']
        pais = busqueda['pais']
        pagina_actual = 1
        
        print(f"\n--- Iniciando búsqueda para '{que}' en '{donde}' ({pais.upper()}) ---")
        
        while True:
            datos_pagina = obtener_ofertas_adzuna(que, donde, pais, pagina=pagina_actual)
            
            if isinstance(datos_pagina, str):
                print(datos_pagina)
                break

            if datos_pagina and datos_pagina.get('results'):
                resultados = datos_pagina['results']
                todos_los_resultados.extend(resultados)
                print(f"Página {pagina_actual}: Se obtuvieron {len(resultados)} resultados.")
                
                if len(resultados) < 50:
                    print("Última página alcanzada para esta búsqueda.")
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
        nombre_archivo = "adzuna_datos_crudos.json"
        
        with open(os.path.join(ruta_salida, nombre_archivo), 'w', encoding='utf-8') as f:
            json.dump(todos_los_resultados, f, ensure_ascii=False, indent=4)
        
        print(f"Todos los datos han sido guardados en: '{os.path.join(ruta_salida, nombre_archivo)}'")
    else:
        print("\nNA")

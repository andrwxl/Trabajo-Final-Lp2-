# EXTRACTOR DE JOOBLE API
import http.client
import json
import os
import time
#from config import JOOBLE_API_KEY # Asumo que tu clave está en config.py
JOOBLE_API_KEY = "clave api"  # Reemplaza con tu clave real
def obtener_ofertas_jooble(keywords, location="Peru"):
    """
    Realiza una petición POST a la API de Jooble usando http.client.
    """
    host = 'es.jooble.org'
    
    try:
        # Establecemos la conexión con el host.
        connection = http.client.HTTPConnection(host)
        
        # Cabecera necesaria para la petición.
        headers = {"Content-type": "application/json"}
        
        # Creamos el cuerpo de la petición como un diccionario de Python.
        body_dict = {
            "keywords": keywords,
            "location": location
        }
        # Convertimos el diccionario a un string en formato JSON.
        body_json = json.dumps(body_dict)

        print(f"Realizando petición a Jooble para: '{keywords}' en '{location}'...")
        
        # Realizamos la petición POST.
        connection.request('POST', '/api/' + JOOBLE_API_KEY, body_json, headers)
        response = connection.getresponse()
        
        # Leemos y decodificamos la respuesta.
        data = response.read().decode("utf-8")
        connection.close()
        
        # Verificamos que la respuesta sea exitosa (código 200).
        if response.status == 200:
            return json.loads(data) # Convertimos el string JSON de la respuesta a un diccionario.
        else:
            print(f"Error en la respuesta de la API: {response.status} {response.reason}")
            return None

    except Exception as e:
        print(f"Ocurrió un error de conexión: {e}")
        return None

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if _name_ == "_main_":
    
    # Lista de países de América para realizar la búsqueda.
    PAISES_DE_AMERICA = [
        "Peru", "Mexico", "Colombia", "Chile", "Argentina", "Ecuador", "United States"
    ]

    # Lista extendida de términos de búsqueda para el sector de informática.
    TERMINOS_DE_BUSQUEDA = [
        "informatica", "sistemas", "programacion", "desarrollador", "software",
        "analista de datos", "data scientist", "ingeniero de datos", "ciberseguridad",
        "soporte tecnico", "redes y telecomunicaciones", "devops", "cloud", "arquitecto de software",
        "frontend", "backend", "fullstack", "mobile developer", "analista funcional",
        "jefe de proyecto ti", "product owner", "scrum master", "qa tester"
    ]

    # Lista para acumular todos los resultados.
    todos_los_resultados = []

    print("--- Iniciando extracción masiva de datos de Jooble ---")
    
    # Iteramos sobre cada país y cada término de búsqueda.
    for pais in PAISES_DE_AMERICA:
        print(f"\n--- Buscando en {pais} ---")
        for termino in TERMINOS_DE_BUSQUEDA:
            datos = obtener_ofertas_jooble(termino, location=pais)
            
            # La respuesta de Jooble está dentro de la clave 'jobs'.
            if datos and datos.get('jobs'):
                resultados = datos['jobs']
                print(f" -> Se encontraron {len(resultados)} ofertas para '{termino}'.")
                todos_los_resultados.extend(resultados)
            else:
                print(f" -> No se encontraron ofertas para '{termino}'.")
            
            # Pausa de 1 segundo para no sobrecargar la API.
            time.sleep(1)
    
    # Guardamos todos los resultados consolidados en un único archivo JSON.
    if todos_los_resultados:
        print(f"\n--- Proceso completado. Total de ofertas extraídas: {len(todos_los_resultados)} ---")
        ruta_salida = os.path.join('datos', 'crudos')
        os.makedirs(ruta_salida, exist_ok=True)
        nombre_archivo = "jooble_datos_crudos.json"
        
        with open(os.path.join(ruta_salida, nombre_archivo), 'w', encoding='utf-8') as f:
            json.dump(todos_los_resultados, f, ensure_ascii=False, indent=4)
        
        print(f"Todos los datos han sido guardados en: '{os.path.join(ruta_salida, nombre_archivo)}'")
    else:
        print("\nNo se extrajo ningún dato de la API en ninguna de las búsquedas.")
        

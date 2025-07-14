import http.client
import json
import os
from urllib.parse import quote
import time

# --- 1. Configuración Principal ---
# Define los puestos de trabajo que quieres buscar
terminos_de_busqueda = [
    # --- Data & Analytics ---
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "Business Intelligence Analyst",
    "BI Developer",
    "Analytics Engineer",
    "Data Architect",
    "Database Administrator",
    "DBA",
    "ETL Developer",

    # --- Software & Web Development ---
    "Software Engineer",
    "Software Developer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Python Developer",
    "Java Developer",
    "JavaScript Developer",
    "React Developer",
    "Node.js Developer",
    "C# Developer",
    ".NET Developer",
    "Mobile Developer",
    "iOS Developer",
    "Android Developer",

    # --- Cloud & DevOps ---
    "Cloud Engineer",
    "DevOps Engineer",
    "Cloud Architect",
    "Site Reliability Engineer",
    "SRE",
    "AWS Engineer",
    "Azure Engineer",
    "GCP Engineer",
    "Solutions Architect",
    "Infrastructure Engineer",

    # --- AI & Machine Learning ---
    "Machine Learning Engineer",
    "ML Engineer",
    "AI Engineer",
    "Computer Vision Engineer",
    "NLP Engineer",
    "Research Scientist",

    # --- IT, Security & Networking ---
    "Cybersecurity Analyst",
    "Security Engineer",
    "Network Engineer",
    "Systems Administrator",
    "IT Support Specialist",
    "QA Engineer",
    "Automation Tester",

    # --- Management & Product ---
    "Project Manager",
    "Product Manager",
    "Scrum Master",
    "Technical Lead",
    "Engineering Manager"
]
# Diccionario para almacenar todos los resultados
resultados_totales = {}

# Tus credenciales de la API (es una buena práctica no dejarlas directamente en el código)
headers = {
    'x-rapidapi-key': "ba24c48cc8msh6dbc0e9d372d11fp1cbe46jsne29df9a56b7e",
    'x-rapidapi-host': "active-jobs-db.p.rapidapi.com"
}

# --- 2. Proceso de Extracción de Datos ---
# Establecemos la conexión una sola vez fuera del bucle
conn = http.client.HTTPSConnection("active-jobs-db.p.rapidapi.com")

# Iteramos sobre cada término de búsqueda
for termino in terminos_de_busqueda:
    print(f"🔎 Buscando trabajos para: '{termino}'...")

    # Codificamos el término para que sea seguro en una URL (maneja espacios y caracteres especiales)
    termino_codificado = quote(f'"{termino}"')

    # Creamos la URL de la petición dinámicamente con el término actual
    # Los filtros de límite, ubicación y tipo de descripción se mantienen
    endpoint_url = (f"/active-ats-7d?limit=10&offset=0&title_filter={termino_codificado}"
                    f"&location_filter=%22United%20States%22%20OR%20%22United%20Kingdom%22"
                    f"&description_type=text")

    try:
        # Realizamos la petición GET
        conn.request("GET", endpoint_url, headers=headers)
        res = conn.getresponse()
        
        print(f"   -> Estado de la respuesta: {res.status} {res.reason}")

        if res.status == 200:
            # Leemos y decodificamos la respuesta
            data = res.read().decode("utf-8")
            # Convertimos la respuesta JSON a un diccionario de Python
            datos_json = json.loads(data)
            # Guardamos los resultados en nuestro diccionario principal
            resultados_totales[termino] = datos_json
        else:
            # Si hay un error, lo registramos y continuamos con el siguiente término
            resultados_totales[termino] = {"error": f"No se pudieron obtener datos. Código de estado: {res.status}"}

    except Exception as e:
        print(f"Ha ocurrido un error al procesar '{termino}': {e}")
        resultados_totales[termino] = {"error": f"Excepción durante la petición: {str(e)}"}
    
    # Pausa de cortesía para no saturar la API
    time.sleep(1) 

# Cerramos la conexión después de terminar todas las búsquedas
conn.close()
print("\n✅ Todas las búsquedas han finalizado.")

# --- 3. Almacenamiento de los Resultados ---
# Definimos la ruta y guardamos el diccionario completo en un archivo JSON
ruta_directorio = os.path.join('datos', 'crudos')
os.makedirs(ruta_directorio, exist_ok=True) # Crea los directorios si no existen

ruta_archivo = os.path.join(ruta_directorio, 'active_jobs_data_multiple.json')

with open(ruta_archivo, 'w', encoding='utf-8') as f:
    json.dump(resultados_totales, f, ensure_ascii=False, indent=4)

print(f"\n💾 ¡Éxito! Resultados guardados en: {ruta_archivo}")
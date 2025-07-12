# skill_scraper_final.py
#
# VERSIÓN 3.0 - Estrategia final usando Requests y BeautifulSoup.
# Este método es más simple y menos propenso a ser detectado por sitios anti-bots.
#
# Requisitos (ejecuta 'pip install requests beautifulsoup4'):
# ------------------------------------------------------------------
# requests
# beautifulsoup4
# ------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin
import time

# ==============================================================================
# 1. MANEJADOR DE LA BASE DE DATOS (Simplificado para este script)
# ==============================================================================
def init_db(db_name="skills_knowledge.db"):
    """Asegura que la tabla de cursos exista en la base de datos."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            source TEXT NOT NULL,
            skill TEXT NOT NULL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"📚 Base de datos '{db_name}' lista.")

def save_courses(courses_data, db_name="skills_knowledge.db"):
    """Guarda una lista de cursos en la base de datos, ignorando duplicados."""
    if not courses_data:
        return
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    sql_query = 'INSERT OR IGNORE INTO courses (title, url, source, skill) VALUES (?, ?, ?, ?)'
    data_to_insert = [(c['title'], c['url'], c['source'], c['skill']) for c in courses_data]
    cursor.executemany(sql_query, data_to_insert)
    rows_added = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"   - ✅ {rows_added} nuevos cursos guardados en la base de datos.")

# ==============================================================================
# 2. FUNCIÓN DE SCRAPING CON REQUESTS Y BEAUTIFULSOUP
# ==============================================================================
def scrape_mit_page(url_to_scrape, skill_category):
    """
    Descarga y extrae los cursos de una URL del MIT usando un método directo.
    """
    print(f"\n🔎 Buscando cursos de '{skill_category}' en MIT OpenCourseWare...")

    # Nos disfrazamos de un navegador común para no ser bloqueados.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Hacemos la petición para descargar el HTML de la página.
        response = requests.get(url_to_scrape, headers=headers, timeout=15)
        # Verificamos que la descarga fue exitosa (código 200).
        response.raise_for_status()
        print("   - Página descargada correctamente.")

        # Usamos BeautifulSoup para "entender" el HTML descargado.
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Lógica de Extracción Adaptada a la Página Esquelética ---
        # En la versión simple, todos los enlaces a cursos están dentro de 'divs' con la clase 'course_info'.
        course_blocks = soup.select('div.course_info')
        
        if not course_blocks:
            print(f"   - No se encontraron bloques de cursos ('div.course_info'). La estructura puede haber cambiado.")
            return []

        print(f"   - Se encontraron {len(course_blocks)} bloques de cursos. Extrayendo datos...")
        
        scraped_data = []
        for block in course_blocks:
            # El enlace del curso es el primer 'a' dentro del bloque.
            link_element = block.find('a')
            
            if link_element:
                title = link_element.get_text(strip=True)
                relative_url = link_element.get('href')

                # Nos aseguramos de que sea un enlace de curso válido.
                if relative_url and title:
                    full_url = urljoin("https://ocw.mit.edu/", relative_url)
                    scraped_data.append({
                        "title": title,
                        "url": full_url,
                        "source": "MIT OpenCourseWare",
                        "skill": skill_category
                    })
        
        print(f"   - Extracción completada. {len(scraped_data)} cursos válidos procesados.")
        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"   - Error al descargar la página: {e}")
        return []
    except Exception as e:
        print(f"   - Ocurrió un error inesperado al procesar la página: {e}")
        return []

# ==============================================================================
# 3. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO PROCESO DE SCRAPING (ESTRATEGIA DIRECTA) 🚀")
    
    db_file = "skills_knowledge.db"
    init_db(db_file)

    # Las URLs de búsqueda que nos han funcionado hasta ahora.
    targets = {
        "Computer Science": "https://ocw.mit.edu/search/?d=Electrical%20Engineering%20and%20Computer%20Science",
        "Data Science": "https://ocw.mit.edu/search/?d=Data%20Science",
        "Mechanical Engineering": "https://ocw.mit.edu/search/?d=Mechanical%20Engineering",
        "Mathematics": "https://ocw.mit.edu/search/?d=Mathematics"
    }

    # --- Bucle Principal ---
    for skill, url in targets.items():
        results = scrape_mit_page(url, skill)
        if results:
            save_courses(results, db_file)
        
        # Pausa respetuosa entre peticiones.
        print("   - Pausando por 2 segundos...")
        time.sleep(2)
        
    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

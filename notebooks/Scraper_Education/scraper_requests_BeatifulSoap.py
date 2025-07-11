# general_scraper_requests.py
#
# Un scraper web modular y configurable utilizando Requests y BeautifulSoup.
# Esta versión es extremadamente rápida y eficiente para sitios web estáticos.
#
# Requisitos (ejecuta 'pip install -r requirements.txt'):
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
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
# Aquí es donde defines los sitios que quieres scrapear.
# Este método funciona mejor en sitios donde el contenido no depende de JavaScript.

SITES_CONFIG = {
    "books_to_scrape": {
        "name": "Books to Scrape",
        "url": "http://books.toscrape.com/",
        "item_container_selector": "article.product_pod", # Selector para cada libro
        "title_selector": "h3 a",                         # Selector para el título dentro del libro
        "link_selector": "h3 a"                           # Selector para el enlace dentro del libro
    },
    "quotes_to_scrape": {
        "name": "Quotes to Scrape",
        "url": "http://quotes.toscrape.com/",
        "item_container_selector": "div.quote",           # Selector para cada cita
        "title_selector": "span.text",                    # Selector para el texto de la cita
        "link_selector": "a"                              # Selector para el enlace "about" del autor
    }
    # PLANTILLA PARA UN NUEVO SITIO ESTÁTICO:
    # "nombre_del_sitio": {
    #     "name": "Nombre Real del Sitio",
    #     "url": "https://www.ejemplo.com/pagina-a-scrapear",
    #     "item_container_selector": "selector_css_para_cada_item",
    #     "title_selector": "selector_css_para_el_titulo",
    #     "link_selector": "selector_css_para_el_enlace"
    # }
}

# ==============================================================================
# 2. FUNCIÓN DE SCRAPING
# ==============================================================================
def scrape_site_with_requests(site_config):
    """
    Descarga y extrae datos de un sitio usando Requests y BeautifulSoup.
    """
    name = site_config["name"]
    url = site_config["url"]
    item_selector = site_config["item_container_selector"]
    title_selector = site_config["title_selector"]
    link_selector = site_config["link_selector"]

    print(f"\n🔎 Iniciando scraping para: '{name}'...")
    
    # Nos disfrazamos de un navegador común para evitar bloqueos básicos.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Hacemos la petición para descargar el HTML de la página.
        response = requests.get(url, headers=headers, timeout=15)
        # Lanza un error si la descarga no fue exitosa (ej. error 404, 500).
        response.raise_for_status()
        print("   - Página descargada correctamente.")

        # Usamos BeautifulSoup para "entender" y parsear el HTML descargado.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraemos todos los ítems de la página usando el selector proporcionado.
        item_elements = soup.select(item_selector)
        
        if not item_elements:
            print(f"   - No se encontraron ítems con el selector '{item_selector}'.")
            return []

        print(f"   - Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
        
        scraped_data = []
        for item in item_elements:
            # Usamos .select_one() que es más seguro que .find() si el elemento no existe.
            title_element = item.select_one(title_selector)
            link_element = item.select_one(link_selector)
            
            if title_element and link_element:
                title = title_element.get_text(strip=True)
                relative_url = link_element.get('href')
                full_url = urljoin(url, relative_url) # Construye la URL completa
                
                scraped_data.append({
                    "title": title,
                    "url": full_url,
                    "source": name,
                    "skill": name # Usamos el nombre del sitio como categoría general
                })
        
        print(f"   - Extracción completada. {len(scraped_data)} ítems procesados.")
        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"   - Error de red al intentar descargar la página: {e}")
        return []
    except Exception as e:
        print(f"   - Ocurrió un error inesperado al procesar la página: {e}")
        return []

# ==============================================================================
# 3. MANEJADOR DE LA BASE DE DATOS
# ==============================================================================
class DatabaseManager:
    def __init__(self, db_name="general_knowledge_requests.db"):
        self.db_name = db_name
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Asegura que la tabla de ítems exista en la base de datos."""
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_items (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL,
                category TEXT NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        self.conn.close()
        print(f"📚 Base de datos '{self.db_name}' lista.")

    def save_items(self, items_data):
        """Guarda una lista de ítems en la base de datos, ignorando duplicados."""
        if not items_data:
            return
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        sql_query = 'INSERT OR IGNORE INTO scraped_items (title, url, source, category) VALUES (?, ?, ?, ?)'
        data_to_insert = [(item['title'], item['url'], item['source'], item['skill']) for item in items_data]
        cursor.executemany(sql_query, data_to_insert)
        rows_added = cursor.rowcount
        self.conn.commit()
        self.conn.close()
        print(f"   - ✅ {rows_added} nuevos ítems guardados en la base de datos.")

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO SCRAPER WEB (VERSIÓN REQUESTS + BEAUTIFULSOUP) 🚀")
    
    db_manager = DatabaseManager()

    # Itera a través de cada sitio definido en la configuración.
    for site_key, site_config in SITES_CONFIG.items():
        results = scrape_site_with_requests(site_config)
        if results:
            db_manager.save_items(results)
        
        # Pausa respetuosa entre sitios.
        if len(SITES_CONFIG) > 1:
            print("   - Pausando por 2 segundos antes del siguiente sitio...")
            time.sleep(2)

    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

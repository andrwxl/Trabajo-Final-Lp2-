# general_scraper_cloud.py
#
# Un scraper web modular utilizando Cloudscraper y BeautifulSoup.
# VERSIÓN AVANZADA: Diseñada para evitar sistemas anti-bots como Cloudflare.
#
# Requisitos (ejecuta 'pip install -r requirements.txt'):
# ------------------------------------------------------------------
# cloudscraper
# beautifulsoup4
# ------------------------------------------------------------------

import cloudscraper
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin
import time

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
SITES_CONFIG = {
    "class_central_subjects": {
        "name": "Class Central",
        "url": "https://www.classcentral.com/subjects",
        "item_container_selector": "a.text-1.weight-bold",
        "title_selector": None,
        "link_selector": None
    },
    "books_to_scrape": {
        "name": "Books to Scrape",
        "url": "http://books.toscrape.com/",
        "item_container_selector": "article.product_pod",
        "title_selector": "h3 a",
        "link_selector": "h3 a"
    }
}

# ==============================================================================
# 2. FUNCIÓN DE SCRAPING (USANDO CLOUDSCRAPER)
# ==============================================================================
def scrape_site_with_cloudscraper(site_config):
    """
    Descarga y extrae datos de un sitio usando Cloudscraper y BeautifulSoup.
    """
    name = site_config["name"]
    url = site_config["url"]
    item_selector = site_config["item_container_selector"]
    title_selector = site_config.get("title_selector")
    link_selector = site_config.get("link_selector")

    print(f"\n🔎 Iniciando scraping para: '{name}' (con Cloudscraper)...")
    
    # Creamos una instancia de cloudscraper. Este objeto se comportará como un navegador real.
    scraper = cloudscraper.create_scraper()

    try:
        # Usamos el scraper para hacer la petición GET.
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        print("   - Página descargada correctamente (¡bloqueo 403 evitado!).")

        soup = BeautifulSoup(response.text, 'html.parser')

        item_elements = soup.select(item_selector)
        
        if not item_elements:
            print(f"   - No se encontraron ítems con el selector '{item_selector}'.")
            return []

        print(f"   - Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
        
        scraped_data = []
        for item in item_elements:
            title_element = item.select_one(title_selector) if title_selector else item
            link_element = item.select_one(link_selector) if link_selector else item
            
            if title_element and link_element:
                title = title_element.get_text(strip=True)
                relative_url = link_element.get('href')
                full_url = urljoin(url, relative_url)
                
                if title and full_url:
                    scraped_data.append({
                        "title": title,
                        "url": full_url,
                        "source": name,
                        "skill": name 
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
    def __init__(self, db_name="general_knowledge_cloud.db"):
        self.db_name = db_name
        self.conn = None
        self._init_db()

    def _init_db(self):
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
    print("🚀 INICIANDO SCRAPER WEB (VERSIÓN CLOUDSCRAPER) 🚀")
    
    db_manager = DatabaseManager()

    for site_key, site_config in SITES_CONFIG.items():
        results = scrape_site_with_cloudscraper(site_config)
        if results:
            db_manager.save_items(results)
        
        if len(SITES_CONFIG) > 1:
            print("   - Pausando por 2 segundos antes del siguiente sitio...")
            time.sleep(2)

    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

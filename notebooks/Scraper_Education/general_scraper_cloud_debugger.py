# general_scraper_cloud_debugger.py
#
# VERSIÓN DE DEPURACIÓN: Guarda el HTML descargado para poder analizarlo
# y encontrar los selectores correctos.
#
# Requisitos:
# ------------------------------------------------------------------
# cloudscraper
# beautifulsoup4
# ------------------------------------------------------------------

import cloudscraper
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin
import time
import os

import requests

# ... (El diccionario SITES_CONFIG y la clase DatabaseManager no cambian y van aquí)
# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
SITES_CONFIG = {
    "class_central_subjects": {
        "name": "Class Central",
        "url": "https://www.classcentral.com/subjects",
        "item_container_selector": "a.text-1.weight-bold",  # Este es el selector que vamos a corregir
        "title_selector": None,
        "link_selector": None
    }
}

# ==============================================================================
# 2. FUNCIÓN DE SCRAPING (CON DEPURACIÓN)
# ==============================================================================
def scrape_site_with_cloudscraper(site_config):
    name = site_config["name"]
    url = site_config["url"]
    item_selector = site_config["item_container_selector"]
    title_selector = site_config.get("title_selector")
    link_selector = site_config.get("link_selector")

    print(f"\n🔎 Iniciando scraping para: '{name}' (con Cloudscraper)...")
    
    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        print("   - Página descargada correctamente (¡bloqueo 403 evitado!).")

        # --- CÓDIGO DE DEPURACIÓN AÑADIDO ---
        # Guardamos el HTML en un archivo para poder inspeccionarlo manualmente.
        html_path = 'debug_page.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"   - [DEPURACIÓN] HTML de la página guardado en: {os.path.abspath(html_path)}")
        # --- FIN DEL CÓDIGO DE DEPURACIÓN ---

        soup = BeautifulSoup(response.text, 'html.parser')
        item_elements = soup.select(item_selector)
        
        if not item_elements:
            print(f"   - No se encontraron ítems con el selector '{item_selector}'.")
            return []

        print(f"   - Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
        
        scraped_data = []
        # ... (el resto de la lógica de extracción no cambia) ...
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
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_items (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL, category TEXT NOT NULL, scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print(f"📚 Base de datos '{self.db_name}' lista.")

    def save_items(self, items_data):
        if not items_data: return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        sql_query = 'INSERT OR IGNORE INTO scraped_items (title, url, source, category) VALUES (?, ?, ?, ?)'
        data_to_insert = [(item['title'], item['url'], item['source'], item['skill']) for item in items_data]
        cursor.executemany(sql_query, data_to_insert)
        rows_added = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"   - ✅ {rows_added} nuevos ítems guardados en la base de datos.")

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    print("🚀 INICIANDO SCRAPER WEB (MODO DEPURACIÓN) 🚀")
    db_manager = DatabaseManager()
    for site_key, site_config in SITES_CONFIG.items():
        if site_config["name"] == "Class Central": # Solo ejecutamos para Class Central
            scrape_site_with_cloudscraper(site_config)
    print("\n🏁 PROCESO DE DEPURACIÓN COMPLETADO 🏁")

if __name__ == "__main__":
    main()

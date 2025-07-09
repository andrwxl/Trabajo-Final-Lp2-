# general_scraper.py
#
# Un scraper web modular y configurable diseñado para ser adaptado fácilmente a diferentes sitios web.
#
# Requisitos (ejecuta 'pip install -r requirements.txt'):
# ------------------------------------------------------------------
# selenium
# webdriver-manager
# ------------------------------------------------------------------

import time
import sqlite3
from abc import ABC, abstractmethod
from urllib.parse import urljoin

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
# Aquí es donde defines los sitios que quieres scrapear.
# Para añadir un nuevo sitio, simplemente copia una de las plantillas y
# rellena con los selectores CSS correctos que encuentres con F12.

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
    # PLANTILLA PARA UN NUEVO SITIO:
    # "nombre_del_sitio": {
    #     "name": "Nombre Real del Sitio",
    #     "url": "https://www.ejemplo.com/pagina-a-scrapear",
    #     "item_container_selector": "selector_css_para_cada_item",
    #     "title_selector": "selector_css_para_el_titulo",
    #     "link_selector": "selector_css_para_el_enlace"
    # }
}


# ==============================================================================
# 2. CLASE SCRAPER GENERAL
# ==============================================================================
class GeneralScraper:
    """
    Una clase de scraper robusta que toma una configuración para operar.
    """
    def __init__(self):
        self.driver = self._init_driver()
        print("✅ Scraper general inicializado con modo sigilo.")

    def _init_driver(self):
        """Inicializa el WebDriver de Selenium con opciones avanzadas anti-detección."""
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            '''
        })
        return driver

    def scrape_site(self, site_config):
        """
        Realiza el proceso de scraping para una configuración de sitio dada.
        """
        name = site_config["name"]
        url = site_config["url"]
        item_selector = site_config["item_container_selector"]
        title_selector = site_config["title_selector"]
        link_selector = site_config["link_selector"]

        print(f"\n🔎 Iniciando scraping para: '{name}'...")
        try:
            self.driver.get(url)
            
            # Esperamos a que el contenedor del primer ítem aparezca.
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, item_selector))
            )
            print("   - Página cargada y lista de ítems encontrada.")
            time.sleep(2)

            # Extraemos todos los ítems de la página.
            item_elements = self.driver.find_elements(By.CSS_SELECTOR, item_selector)
            
            if not item_elements:
                print(f"   - No se encontraron ítems con el selector '{item_selector}'.")
                return []

            print(f"   - Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
            
            scraped_data = []
            for item in item_elements:
                try:
                    title = item.find_element(By.CSS_SELECTOR, title_selector).text
                    
                    link_element = item.find_element(By.CSS_SELECTOR, link_selector)
                    relative_url = link_element.get_attribute('href')
                    full_url = urljoin(url, relative_url) # Construye la URL completa
                    
                    scraped_data.append({
                        "title": title.strip(),
                        "url": full_url,
                        "source": name,
                        "skill": name # Usamos el nombre del sitio como categoría general
                    })
                except NoSuchElementException:
                    # Si un ítem no tiene la estructura esperada, lo saltamos.
                    continue
            
            print(f"   - Extracción completada. {len(scraped_data)} ítems procesados.")
            return scraped_data

        except TimeoutException:
            print(f"   - Error: Tiempo de espera agotado. El sitio puede ser muy lento o el selector '{item_selector}' es incorrecto.")
            return []
        except Exception as e:
            print(f"   - Ocurrió un error inesperado al scrapear '{name}': {e}")
            return []

    def close(self):
        """Cierra el navegador y libera los recursos."""
        if self.driver:
            self.driver.quit()
            print("\n✅ Navegador cerrado.")

# ==============================================================================
# 3. MANEJADOR DE LA BASE DE DATOS
# ==============================================================================
class DatabaseManager:
    def __init__(self, db_name="general_knowledge.db"):
        self.db_name = db_name
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Asegura que la tabla de cursos exista en la base de datos."""
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
    print("🚀 INICIANDO SCRAPER WEB GENERAL Y CONFIGURABLE 🚀")
    
    db_manager = DatabaseManager()
    scraper = GeneralScraper()

    try:
        # Itera a través de cada sitio definido en la configuración.
        for site_key, site_config in SITES_CONFIG.items():
            results = scraper.scrape_site(site_config)
            if results:
                db_manager.save_items(results)
            
            # Pausa respetuosa entre sitios.
            if len(SITES_CONFIG) > 1:
                print("   - Pausando por 3 segundos antes del siguiente sitio...")
                time.sleep(3)
    finally:
        # Nos aseguramos de que el navegador se cierre siempre.
        scraper.close()

    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()
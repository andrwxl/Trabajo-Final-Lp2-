# scraper_definitivo_v10.py
#
# VERSIÓN 10.0: La versión final y más robusta.
# Todas las funciones de scraping (Cloudscraper y Selenium) ahora guardan
# el progreso directamente en el archivo CSV en tiempo real.
# El script es completamente resumible y a prueba de cualquier interrupción.

import requests
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv
import os

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
SITES_CONFIG = {
    "books_to_scrape": {
        "name": "Books to Scrape", "type": "Libro (Práctica)", "tool": "cloudscraper",
        "url": "http://books.toscrape.com/",
        "pagination_selector": "li.next a",
        "selectors": {
            "item_container": "article.product_pod", "title": "h3 a", "link": "h3 a",
            "cost": "p.price_color", "level": "p.star-rating"
        }
    },
    "hacker_news": {
        "name": "Hacker News", "type": "Artículo de Tecnología", "tool": "cloudscraper",
        "url": "https://news.ycombinator.com/",
        "pagination_selector": "a.morelink",
        "selectors": {
            "item_container": "tr.athing", "title": "span.titleline > a", "link": "span.titleline > a"
        }
    },
    "class_central": {
        "name": "Class Central", "type": "Índice de Materias", "tool": "cloudscraper",
        "url": "https://www.classcentral.com/subjects",
        "selectors": {
            "item_container": "a.l-subjects-page__subject-link", "title": "span.l-subjects-page__subject-label", "link": None,
            "duration_effort": "span.l-subjects-page__subject-course-count"
        }
    },
    "openstax": {
        "name": "OpenStax", "type": "Libro de Texto Universitario", "tool": "cloudscraper",
        "url": "https://openstax.org/subjects",
        "selectors": {
            "item_container": "div[class*='BookCard-styles__Container']",
            "title": "h3", "link": "a",
            "author_instructor": "div[class*='BookCard-styles__Author']"
        }
    },
    "coursera": {
        "name": "Coursera (Data Science)", "type": "Curso Profesional", "tool": "selenium",
        "url": "https://www.coursera.org/search?query=data%20science",
        "load_more_selector": "button[data-testid='search-results-show-more-button']",
        "pagination_selector": "button[aria-label='Next Page']",
        "selectors": {
            "item_container": "li.cds-9", "title": "h3.cds-CommonCard-title", "link": "a",
            "author_instructor": "span.partner-name", "level": "div[data-testid='card-metadata'] > p"
        }
    },
}

# ==============================================================================
# 2. MOTORES DE SCRAPING
# ==============================================================================
def scrape_site_with_cloudscraper(site_config, existing_urls, output_filename):
    """
    Función de scraping con Cloudscraper, AHORA CORREGIDA para ser resumible
    y guardar en tiempo real, igual que la de Selenium.
    """
    name = site_config["name"]
    base_url = site_config["url"]
    pagination_selector = site_config.get("pagination_selector")
    
    print(f"\n🔎 Usando [Cloudscraper v11.0 - Indestructible] para: '{name}'...")
    scraper = cloudscraper.create_scraper()
    current_url = base_url
    page_count = 1
    items_found_this_session = 0

    while current_url:
        print(f"   - Scrapeando página {page_count}: {current_url}")
        response = None
        for attempt in range(3):
            try:
                response = scraper.get(current_url, timeout=20)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"   - ⚠️ Intento {attempt + 1} fallido: {e}")
                if attempt < 2: time.sleep(5)
        
        if not response: break

        soup = BeautifulSoup(response.text, 'html.parser')
        items_on_page = extract_data_from_soup(soup, site_config)
        
        # Filtra los ítems que ya existen en el archivo CSV
        new_items = [item for item in items_on_page if item['url'] not in existing_urls]
        
        if new_items:
            # Guarda los nuevos ítems directamente en el archivo
            append_to_csv(new_items, output_filename)
            items_found_this_session += len(new_items)
            # Actualiza el set de URLs en memoria para evitar duplicados en la misma sesión
            for item in new_items:
                existing_urls.add(item['url'])
            print(f"   - ✅ {len(new_items)} ítems nuevos guardados. Total en archivo: {len(existing_urls)}")

        # Lógica de paginación
        next_page_element = soup.select_one(pagination_selector) if pagination_selector else None
        if next_page_element:
            next_page_url = next_page_element.get('href')
            current_url = urljoin(base_url, next_page_url)
            page_count += 1
            time.sleep(1)
        else:
            current_url = None
    
    print(f"\n   - Finalizado el scraping para '{name}'. Se añadieron {items_found_this_session} ítems nuevos.")

# Versión final de las funciones de Selenium


def scrape_site_with_selenium(site_config, existing_urls, output_filename, start_time, limits):
    """
    Función de scraping con Selenium que guarda el progreso directamente en el archivo.
    """
    name = site_config["name"]
    selectors = site_config["selectors"]
    pagination_selector = site_config.get("pagination_selector")

    print(f"\n🔎 Usando [Selenium v9.0 - Indestructible] para: '{name}'...")
    driver = init_selenium_driver()
    if not driver: return

    try:
        driver.get(site_config["url"])
        page_count = 1
        items_found_this_session = 0

        while True:
            total_items_so_far = len(existing_urls)
            if (limits['max_items'] is not None and total_items_so_far >= limits['max_items']) or \
               (limits['max_runtime'] is not None and (time.time() - start_time) > limits['max_runtime'] * 60):
                print("   - ✋ LÍMITE ALCANZADO. Deteniendo este sitio.")
                break

            print(f"\n--- Scrapeando Página {page_count} ---")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["item_container"])))

            # --- LÓGICA FINAL DE SCROLL "HUMANO" ---
            print("   - Iniciando scroll controlado...")
            max_scrolls = 10 # Un límite de seguridad para no entrar en un bucle infinito
            scroll_count = 0
            
            while scroll_count < max_scrolls:
                last_item_count = len(driver.find_elements(By.CSS_SELECTOR, selectors["item_container"]))
                
                # Hacemos scroll hacia el último elemento encontrado para revelar el "activador"
                all_elements = driver.find_elements(By.CSS_SELECTOR, selectors["item_container"])
                if all_elements:
                    last_element = all_elements[-1]
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", last_element)
                
                # Esperamos un tiempo para que el nuevo contenido cargue
                time.sleep(5) 
                
                new_item_count = len(driver.find_elements(By.CSS_SELECTOR, selectors["item_container"]))
                
                if new_item_count > last_item_count:
                    print(f"   - Nuevo contenido cargado. Total de ítems en página: {new_item_count}")
                    scroll_count = 0 # Reseteamos el contador si hay éxito
                else:
                    print(f"   - No se detectaron nuevos ítems en este scroll (intento {scroll_count + 1}/{max_scrolls}).")
                    scroll_count += 1
            
            print("   - Carga de contenido de la página actual finalizada.")
            
            # Extraemos los datos de la página actual
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items_on_page = extract_data_from_soup(soup, site_config)
            
            new_items = [item for item in items_on_page if item['url'] not in existing_urls]
            
            if new_items:
                append_to_csv(new_items, output_filename)
                items_found_this_session += len(new_items)
                for item in new_items:
                    existing_urls.add(item['url']) # Actualizamos el set en memoria
                print(f"   - ✅ {len(new_items)} ítems nuevos guardados. Total en archivo: {len(existing_urls)}")
            
            try:
                next_page_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, pagination_selector)))
                if not next_page_button.is_enabled():
                    break
                driver.execute_script("arguments[0].click();", next_page_button)
                page_count += 1
                time.sleep(7)
            except TimeoutException:
                break
        
        print(f"\n   - Finalizado el scraping para '{name}'. Se añadieron {items_found_this_session} ítems nuevos.")

    except Exception as e:
        print(f"   - ❌ Error fatal en Selenium para '{name}': {e}")
    finally:
        if driver: driver.quit()

# ==============================================================================
# 3. LÓGICA DE EXTRACCIÓN Y GUARDADO (NUEVAS FUNCIONES AUXILIARES)
# ==============================================================================
def init_selenium_driver():
    """
    Inicializa el driver de Selenium con configuraciones para evitar la detección
    y con un tiempo de espera extendido.
    """
    try:
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument("--headless=new") # Mantenlo comentado para depurar
        options.add_argument("--window-size=1920,1080")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # --- AUMENTAMOS EL TIMEOUT PARA EVITAR EL CRASH ---
        driver.set_page_load_timeout(120) # Le damos hasta 2 minutos para cargar páginas
        driver.set_script_timeout(120) # Le damos hasta 2 minutos para ejecutar scripts

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
        return driver
    except Exception as e:
        print(f"   - ❌ Error fatal al inicializar Selenium: {e}")
        return None

def get_text_or_na(element, selector):
    if not selector: return "N/A"
    found_el = element.select_one(selector)
    return found_el.get_text(strip=True) if found_el else "N/A"

def get_link_or_na(element, selector, base_url):
    link_element = element if selector is None else element.select_one(selector)
    if not link_element: return "N/A"
    relative_url = link_element.get('href')
    return urljoin(base_url, relative_url) if relative_url else "N/A"

def extract_data_from_soup(soup, site_config):
    selectors = site_config["selectors"]
    item_elements = soup.select(selectors["item_container"])
    
    if not item_elements:
        print(f"   - ❌ No se encontraron ítems con el selector '{selectors['item_container']}'.")
        return []

    print(f"   - ✅ ¡Éxito! Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
    scraped_data = []
    for item in item_elements:
        data = {
            "fuente": site_config["name"],
            "tipo_recurso": site_config["type"],
            "titulo": get_text_or_na(item, selectors.get("title")),
            "url": get_link_or_na(item, selectors.get("link"), site_config["url"]),
            "autor_instructor": get_text_or_na(item, selectors.get("author_instructor")),
            "costo": get_text_or_na(item, selectors.get("cost")),
            "nivel": get_text_or_na(item, selectors.get("level")),
            "duracion_esfuerzo": get_text_or_na(item, selectors.get("duration_effort"))
        }
        if data["titulo"] != "N/A" and data["url"] != "N/A":
            scraped_data.append(data)
            
    print(f"   - Extracción completada. {len(scraped_data)} ítems procesados.")
    return scraped_data

def load_from_csv(filename):
    """Carga las URLs existentes de un CSV para evitar duplicados."""
    if not os.path.isfile(filename):
        return set()
    
    existing_urls = set()
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row and 'url' in row:
                    existing_urls.add(row['url'])
    except Exception as e:
        print(f"   - Advertencia: no se pudo leer el archivo CSV existente. Se creará uno nuevo. Error: {e}")
        return set()
    print(f"   - Se cargaron {len(existing_urls)} URLs de un archivo existente para evitar duplicados.")
    return existing_urls

def append_to_csv(items_to_add, filename):
    """Añade una lista de ítems a un archivo CSV."""
    if not items_to_add: return

    fieldnames = ["fuente", "tipo_recurso", "titulo", "url", "autor_instructor", "costo", "nivel", "duracion_esfuerzo"]
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        if not file_exists or os.path.getsize(filename) == 0:
            writer.writeheader()
        writer.writerows(items_to_add)

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    print("🚀 INICIANDO SCRAPER 'ATLAS MUNDIAL' v10.0 (INDESTRUCTIBLE) 🚀")

    limits = {"max_items": 2500, "max_runtime": 2}
    output_filename = "matriz_de_conocimiento.csv"
    start_time = time.time()

    existing_urls = load_from_csv(output_filename)
    
    try:
        for site_key, site_config in SITES_CONFIG.items():
            
            if (limits['max_items'] is not None and len(existing_urls) >= limits['max_items']) or \
               (limits['max_runtime'] is not None and (time.time() - start_time) > limits['max_runtime'] * 60):
                print("\n✋ LÍMITE ALCANZADO. Finalizando.")
                break

            tool = site_config.get("tool", "cloudscraper")
            
            if tool == 'cloudscraper':
                scrape_site_with_cloudscraper(site_config, existing_urls, output_filename)
            elif tool == 'selenium':
                scrape_site_with_selenium(site_config, existing_urls, output_filename, start_time, limits)
            
            print(f"\n   - ✅ Checkpoint final para '{site_config['name']}'. Total de ítems en archivo: {len(existing_urls)}")
            
            if len(SITES_CONFIG) > 1 and site_key != list(SITES_CONFIG.keys())[-1]:
                print("\n----------------------------------------------------")
                time.sleep(3)

    except KeyboardInterrupt:
        print("\n\n🛑 Proceso interrumpido por el usuario.")
    
    finally:
        print("\n--- Proceso finalizado. ---")
        final_count = len(load_from_csv(output_filename))
        print(f"\n💾 El archivo '{output_filename}' contiene {final_count} ítems.")
        
        elapsed_final = time.time() - start_time
        print(f"\n⏱️ Tiempo total de ejecución: {elapsed_final / 60:.2f} minutos.")
        print("\n🏁 PROCESO DE SCRAPING COMPLETADO (o interrumpido de forma segura) 🏁")


if __name__ == "__main__":
    main()
    
# scraper_definitivo_v3.py
#
# VERSIÓN 3.0: La culminación de nuestro trabajo.
# Extrae datos detallados de múltiples fuentes y los guarda en un único CSV.
# ¡Ahora con capacidad de scroll infinito para sitios dinámicos!
#
# Requisitos:
# ------------------------------------------------------------------
# cloudscraper
# beautifulsoup4
# selenium
# webdriver-manager
# ------------------------------------------------------------------

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
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS - "ATLAS MUNDIAL"
# ==============================================================================
SITES_CONFIG = {
    # --- NIVEL 1: FÁCIL ---
    "books_to_scrape": {
        "name": "Books to Scrape", "type": "Libro (Práctica)", "tool": "cloudscraper",
        "url": "http://books.toscrape.com/",
        "pagination_selector": "a.morelink",        
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
    # --- NIVEL 2: MEDIO ---
    "class_central": {
        "name": "Class Central", "type": "Índice de Materias", "tool": "cloudscraper",
        "url": "https://www.classcentral.com/subjects",
        "pagination_selector": "a.l-subjects-page__next-link",
        # Selector para el botón de "Siguiente" en la paginación
        "selectors": {
            "item_container": "a.l-subjects-page__subject-link", "title": "span.l-subjects-page__subject-label", "link": None,
            "duration_effort": "span.l-subjects-page__subject-course-count"
        }
    },
    "openstax": {
        "name": "OpenStax", "type": "Libro de Texto Universitario", "tool": "cloudscraper",
        "url": "https://openstax.org/subjects",
        "pagination_selector": "a.pagination__next",
        # Selector para el botón de "Siguiente" en la paginación
        "selectors": {
            "item_container": "div[data-is-qa='Book Legal Card']", "title": "h2[data-is-qa='Book Title']", "link": "a",
            "author_instructor": "p[class*='styles__Author']"
        }
    },
    # --- NIVEL 3: DIFÍCIL (Requiere Selenium) ---
    # ¡Ahora puedes descomentar este bloque para probar el scroll infinito!
    "coursera": {
        "name": "Coursera (Data Science)", "type": "Curso Profesional", "tool": "selenium",
        "url": "https://www.coursera.org/search?query=data%20science",
        "pagination_selector": "button[data-testid='search-results-show-more-button']",
        "selectors": {
            "item_container": "li.cds-9", "title": "h3.cds-CommonCard-title", "link": "a",
            "author_instructor": "span.partner-name", "level": "div[data-testid='card-metadata'] > p"
        }
    },
}

# ==============================================================================
# 2. MOTORES DE SCRAPING
# ==============================================================================
def scrape_site_with_cloudscraper(site_config):
    name = site_config["name"]
    base_url = site_config["url"]
    pagination_selector = site_config.get("pagination_selector") # Obtenemos el selector de paginación
    
    print(f"\n🔎 Usando [Cloudscraper] para: '{name}'...")
    scraper = cloudscraper.create_scraper()
    all_items_from_site = []
    current_url = base_url

    # --- NUEVA LÓGICA DE BUCLE PARA PAGINACIÓN ---
    page_count = 1
    while current_url:
        print(f"   - Scrapeando página {page_count}: {current_url}")
        
        # Intentamos descargar la página actual
        response = None
        for attempt in range(3):
            try:
                response = scraper.get(current_url, timeout=20)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"   - ⚠️ Intento {attempt + 1} fallido para descargar la página: {e}")
                if attempt < 2: time.sleep(5)
        
        if not response:
            print(f"   - ❌ Fallaron todos los intentos para descargar '{current_url}'. Abortando este sitio.")
            break

        # Extraemos datos de la página actual
        soup = BeautifulSoup(response.text, 'html.parser')
        items_on_page = extract_data_from_soup(soup, site_config)
        if not items_on_page:
            print("   - No se encontraron más ítems en esta página.")
            break
        
        all_items_from_site.extend(items_on_page)
        
        # Buscamos el enlace de la siguiente página
        next_page_element = soup.select_one(pagination_selector) if pagination_selector else None
        if next_page_element:
            next_page_url = next_page_element.get('href')
            current_url = urljoin(base_url, next_page_url) # Construimos la URL completa para la siguiente página
            page_count += 1
            time.sleep(1) # Pequeña pausa para ser respetuosos con el servidor
        else:
            print("   - No se encontró un enlace a la siguiente página. Fin de la paginación.")
            current_url = None # Terminamos el bucle

    return all_items_from_site

# Reemplaza tu función scrape_site_with_selenium con esta versión mejorada

def scrape_site_with_selenium(site_config):
    name = site_config["name"]
    selectors = site_config["selectors"]
    pagination_selector = site_config.get("pagination_selector")

    print(f"\n🔎 Usando [Selenium v2.0 - Robusto] para: '{name}'...")
    driver = init_selenium_driver()
    if not driver: return []
    
    try:
        driver.get(site_config["url"])
        # Espera inicial a que los primeros ítems aparezcan
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors["item_container"]))
        )
        print("   - Página inicial cargada.")

        # --- MANEJO DE COOKIES/POPUPS (OPCIONAL PERO RECOMENDADO) ---
        try:
            # Intenta encontrar y cerrar un botón de cookies común
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            cookie_button.click()
            print("   - Banner de cookies cerrado.")
            time.sleep(2)
        except TimeoutException:
            print("   - No se encontró banner de cookies, o ya estaba aceptado.")
            pass # Si no hay botón de cookies, no hagas nada
        
        # --- LÓGICA HÍBRIDA DE SCROLL Y CLIC ---
        print("   - Iniciando carga de contenido dinámico (scroll/clic)...")
        max_attempts = 5 # Número de veces que intentaremos cargar más contenido sin éxito antes de rendirnos
        attempts = 0
        while attempts < max_attempts:
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            # Intento 1: Hacer clic en el botón "Cargar Más" si existe
            try:
                if pagination_selector:
                    load_more_button = driver.find_element(By.CSS_SELECTOR, pagination_selector)
                    driver.execute_script("arguments[0].click();", load_more_button)
                    print("   - Botón 'Cargar más' presionado.")
                    time.sleep(4) # Espera generosa a que cargue el contenido
            except Exception:
                # Si no hay botón, no es un error, simplemente intentamos hacer scroll
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4)

            # Verificamos si la página ha crecido
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height > last_height:
                print(f"   - Nuevo contenido cargado. Altura de la página: {new_height}px")
                attempts = 0 # Reseteamos el contador porque hubo éxito
            else:
                attempts += 1
                print(f"   - No se detectó nuevo contenido (intento {attempts}/{max_attempts}).")
        
        print("   - Carga dinámica finalizada.")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return extract_data_from_soup(soup, site_config)
        
    except Exception as e:
        print(f"   - ❌ Error en Selenium para '{name}': {e}")
        return []
    finally:
        if driver: driver.quit()

def init_selenium_driver():
    try:
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
        return driver
    except Exception as e:
        print(f"   - ❌ Error fatal al inicializar Selenium: {e}")
        return None

# ==============================================================================
# 3. LÓGICA DE EXTRACCIÓN Y GUARDADO
# ==============================================================================
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

def save_to_csv(all_items, filename="matriz_de_conocimiento.csv"):
    if not all_items:
        print("\nNo se encontraron ítems para guardar en el archivo CSV.")
        return

    fieldnames = ["fuente", "tipo_recurso", "titulo", "url", "autor_instructor", "costo", "nivel", "duracion_esfuerzo"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_items)
        
    print(f"\n💾 ¡VICTORIA! {len(all_items)} ítems guardados en: {os.path.abspath(filename)}")

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    print("🚀 INICIANDO SCRAPER 'ATLAS MUNDIAL' 🚀")
    all_results = []
    for site_key, site_config in SITES_CONFIG.items():
        results = []
        tool = site_config.get("tool", "cloudscraper")
        
        if tool == 'cloudscraper':
            results = scrape_site_with_cloudscraper(site_config)
        elif tool == 'selenium':
            results = scrape_site_with_selenium(site_config)
        
        if results:
            all_results.extend(results)
        
        if len(SITES_CONFIG) > 1 and site_key != list(SITES_CONFIG.keys())[-1]:
            print("   - Pausando por 3 segundos antes del siguiente sitio...")
            time.sleep(3)

    save_to_csv(all_results)
    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

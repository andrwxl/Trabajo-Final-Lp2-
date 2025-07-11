# scraper_definitivo.py
#
# VERSIÓN FINAL: Un scraper modular que utiliza la herramienta adecuada (Cloudscraper o Selenium)
# para cada sitio web, basándose en una configuración central.
#
# Requisitos (ejecuta 'pip install -r requirements.txt'):
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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
# Aquí definimos todos nuestros objetivos. El campo "tool" le dice al script
# qué método usar: 'cloudscraper' para sitios estáticos, 'selenium' para dinámicos.

SITES_CONFIG = {
    # --- NIVEL 1: FÁCIL ---
    "books_to_scrape": {
        "name": "Books to Scrape",
        "type": "Libro (Práctica)",
        "tool": "cloudscraper",
        "url": "http://books.toscrape.com/",
        "item_container_selector": "article.product_pod",
        "title_selector": "h3 a",
        "link_selector": "h3 a"
    },
    "hacker_news": {
        "name": "Hacker News",
        "type": "Artículo de Tecnología",
        "tool": "cloudscraper",
        "url": "https://news.ycombinator.com/",
        "item_container_selector": "tr.athing",
        "title_selector": "span.titleline > a",
        "link_selector": "span.titleline > a"
    },
    # --- NIVEL 2: MEDIO ---
    "class_central": {
        "name": "Class Central",
        "type": "Índice de Cursos",
        "tool": "cloudscraper",
        "url": "https://www.classcentral.com/subjects",
        "item_container_selector": "a.l-subjects-page__subject-link",
        "title_selector": "span.l-subjects-page__subject-label",
        "link_selector": None
    },
    "openstax": {
        "name": "OpenStax",
        "type": "Libro de Texto Universitario",
        "tool": "cloudscraper",
        "url": "https://openstax.org/subjects",
        "item_container_selector": "div[data-is-qa='Book Legal Card'] a",
        "title_selector": "h2",
        "link_selector": None
    },
    # --- NIVEL 3: DIFÍCIL (Requiere Selenium) ---
    "coursera": {
        "name": "Coursera",
        "type": "Curso Profesional",
        "tool": "selenium",
        "url": "https://www.coursera.org/search?query=python",
        "item_container_selector": "li.cds-9", # Selector puede ser frágil
        "title_selector": "h3.cds-CommonCard-title",
        "link_selector": "a"
    },
    # --- NIVEL 4: EXPERTO (Nuestro gran desafío) ---
    "mit_ocw": {
        "name": "MIT OpenCourseWare",
        "type": "Curso Universitario (MIT)",
        "tool": "selenium",
        "url": "https://ocw.mit.edu/search/",
        "item_container_selector": "li.course-card-list-item",
        "title_selector": "h3",
        "link_selector": "a"
    }
}

# ==============================================================================
# 2. MOTORES DE SCRAPING
# ==============================================================================

# --- Motor 1: Cloudscraper (para sitios estáticos) ---
def scrape_site_with_cloudscraper(site_config):
    name, resource_type, url = site_config["name"], site_config["type"], site_config["url"]
    item_selector, title_selector, link_selector = site_config["item_container_selector"], site_config.get("title_selector"), site_config.get("link_selector")

    print(f"\n🔎 Usando [Cloudscraper] para: '{name}' (Tipo: {resource_type})...")
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url, timeout=20)
        response.raise_for_status()
        print(f"   - Página descargada correctamente.")
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_data_from_soup(soup, site_config)
    except requests.exceptions.RequestException as e:
        print(f"   - ❌ Error de red: {e}")
        return []

# --- Motor 2: Selenium (para sitios dinámicos) ---
def scrape_site_with_selenium(site_config):
    name, resource_type, url = site_config["name"], site_config["type"], site_config["url"]
    item_selector = site_config["item_container_selector"]
    
    print(f"\n🔎 Usando [Selenium] para: '{name}' (Tipo: {resource_type})...")
    driver = init_selenium_driver()
    if not driver: return []
    
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, item_selector)))
        print("   - Página dinámica cargada y lista de ítems encontrada.")
        time.sleep(5) # Pausa extra para que todo el contenido se asiente
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return extract_data_from_soup(soup, site_config)
    except TimeoutException:
        print(f"   - ❌ Error: Tiempo de espera agotado. El sitio puede ser muy lento o el selector '{item_selector}' es incorrecto.")
        return []
    finally:
        driver.quit()

def init_selenium_driver():
    """Inicializa el WebDriver de Selenium con opciones avanzadas anti-detección."""
    try:
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--headless") # Ejecutar en segundo plano
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
        return driver
    except Exception as e:
        print(f"   - ❌ Error al inicializar Selenium: {e}")
        return None

# --- Función de extracción común ---
def extract_data_from_soup(soup, site_config):
    """Función universal para extraer datos de un objeto BeautifulSoup."""
    name, resource_type, url = site_config["name"], site_config["type"], site_config["url"]
    item_selector, title_selector, link_selector = site_config["item_container_selector"], site_config.get("title_selector"), site_config.get("link_selector")

    item_elements = soup.select(item_selector)
    if not item_elements:
        print(f"   - ❌ No se encontraron ítems con el selector '{item_selector}'.")
        return []

    print(f"   - ✅ ¡Éxito! Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
    scraped_data = []
    for item in item_elements:
        try:
            title_element = item.select_one(title_selector) if title_selector else item
            link_element = item if link_selector is None else item.select_one(link_selector)
            
            title = title_element.get_text(strip=True) if title_element else "N/A"
            relative_url = link_element.get('href') if link_element else ""
            full_url = urljoin(url, relative_url)
            
            if title != "N/A" and full_url:
                scraped_data.append({
                    "habilidad_fuente": name,
                    "tipo_recurso": resource_type,
                    "titulo": title,
                    "url": full_url
                })
        except Exception:
            continue # Si un ítem individual falla, lo saltamos y continuamos con el resto.
            
    print(f"   - Extracción completada. {len(scraped_data)} ítems procesados.")
    return scraped_data

# ==============================================================================
# 3. FUNCIÓN PARA GUARDAR EN CSV
# ==============================================================================
def save_to_csv(all_items, filename="matriz_de_conocimiento.csv"):
    if not all_items:
        print("\nNo se encontraron ítems para guardar en el archivo CSV.")
        return

    fieldnames = ["habilidad_fuente", "tipo_recurso", "titulo", "url"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_items)
        
    print(f"\n💾 ¡VICTORIA! {len(all_items)} ítems guardados en: {os.path.abspath(filename)}")

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO SCRAPER DEFINITIVO 🚀")
    
    all_results = []

    for site_key, site_config in SITES_CONFIG.items():
        results = []
        if site_config['tool'] == 'cloudscraper':
            results = scrape_site_with_cloudscraper(site_config)
        elif site_config['tool'] == 'selenium':
            results = scrape_site_with_selenium(site_config)
        else:
            print(f"Herramienta desconocida '{site_config['tool']}' para el sitio '{site_config['name']}'.")

        if results:
            all_results.extend(results)
        
        if len(SITES_CONFIG) > 1 and site_key != list(SITES_CONFIG.keys())[-1]:
            print("   - Pausando por 3 segundos antes del siguiente sitio...")
            time.sleep(3)

    save_to_csv(all_results)

    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

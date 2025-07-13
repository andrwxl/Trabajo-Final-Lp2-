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
        "selectors": {
            # --- SELECTORES CORREGIDOS ---
            "item_container": "div[class*='BookCard-styles__Container']",
            "title": "h3", 
            "link": "a",
            "author_instructor": "div[class*='BookCard-styles__Author']"
        }
    },
    # --- NIVEL 3: DIFÍCIL (Requiere Selenium) ---
    # En SITES_CONFIG, vamos a reutilizar "pagination_selector" para este nuevo propósito
    "coursera": {
        "name": "Coursera (Data Science)", "type": "Curso Profesional", "tool": "selenium",
        "url": "https://www.coursera.org/search?query=data%20science",
        # Selector para el botón "Cargar Más"
        "load_more_selector": "button[data-testid='search-results-show-more-button']", 
        # --- NUEVO SELECTOR PARA EL BOTÓN "SIGUIENTE PÁGINA" ---
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

# Versión final de las funciones de Selenium

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

def scrape_site_with_selenium(site_config):
    name = site_config["name"]
    selectors = site_config["selectors"]
    pagination_selector = site_config.get("pagination_selector")

    print(f"\n🔎 Usando [Selenium v4.0 - Scroll Humano] para: '{name}'...")
    driver = init_selenium_driver()
    if not driver: return []

    all_items_from_site = []
    
    try:
        driver.get(site_config["url"])
        page_count = 1

        while True: # Bucle exterior para manejar las páginas (1, 2, 3...)
            print(f"\n--- Scrapeando Página {page_count} ---")
            
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["item_container"])))
            print("   - Página cargada.")

            # --- LÓGICA FINAL DE SCROLL "HUMANO" ---
            print("   - Iniciando scroll controlado...")
            max_scrolls = 100 # Un límite de seguridad para no entrar en un bucle infinito
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
            
            # Extraemos los datos
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items_on_page = extract_data_from_soup(soup, site_config)
            
            # Añadimos solo los ítems que no hayamos añadido ya (para evitar duplicados)
            current_urls = {item['url'] for item in all_items_from_site}
            new_items = [item for item in items_on_page if item['url'] not in current_urls]
            all_items_from_site.extend(new_items)
            print(f"   - Total de ítems únicos acumulados: {len(all_items_from_site)}")

            # --- Lógica para pasar a la siguiente página (sin cambios, pero ahora debería funcionar) ---
            try:
                # ... (El bloque de código para pasar de página que te di antes se mantiene aquí)
                print("   - Buscando el botón 'Siguiente Página'...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                wait = WebDriverWait(driver, 15)
                next_page_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, pagination_selector)))
                
                if not next_page_button.is_enabled():
                    print("   - El botón 'Siguiente Página' está desactivado. Fin del scraping.")
                    break
                
                print("   - Botón 'Siguiente Página' encontrado. Pasando de página...")
                driver.execute_script("arguments[0].click();", next_page_button)
                page_count += 1
                time.sleep(7)
            except TimeoutException:
                print("   - No se encontró el botón 'Siguiente Página'. Fin del scraping total.")
                break 
            except Exception as e:
                print(f"   - Ocurrió un error al pasar de página: {e}")
                break 

        return all_items_from_site
        
    except Exception as e:
        print(f"   - ❌ Error fatal en Selenium para '{name}': {e}")
        return []
    finally:
        if driver: driver.quit()

# ==============================================================================
# 2.1. INICIALIZACIÓN DE SELENIUM
def init_selenium_driver():
    try:
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        #options.add_argument("--headless=new")
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
    """
    Guarda la lista completa de ítems en un archivo CSV.
    Sobrescribe el archivo cada vez que se llama para asegurar que el archivo
    siempre refleje el estado más reciente y completo del progreso.
    """
    if not all_items:
        return # No hagas nada si no hay ítems que guardar

    fieldnames = ["fuente", "tipo_recurso", "titulo", "url", "autor_instructor", "costo", "nivel", "duracion_esfuerzo"]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_items)
        # El mensaje de éxito ahora se imprime desde la función main
    except IOError as e:
        print(f"   - ❌ ERROR AL ESCRIBIR EN EL ARCHIVO CSV: {e}")

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN (VERSIÓN CON LÍMITES)
# ==============================================================================

def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    Ahora incluye límites configurables para detener la ejecución.
    """
    print("🚀 INICIANDO SCRAPER 'ATLAS MUNDIAL' v6.0 (CON LÍMITES) 🚀")

    # --- PANEL DE CONTROL: CONFIGURA TUS LÍMITES AQUÍ ---
    # Pon un número grande (ej. 999999) o None para no tener límite.
    MAX_ITEMS = 1000  # Detenerse después de recolectar 500 ítems en total.
    MAX_RUNTIME_MINUTES = 1 # Detenerse después de 15 minutos.

    all_results = []
    output_filename = "matriz_de_conocimiento.csv"
    start_time = time.time() # Guardamos la hora de inicio
    print(f"\n🕒 Tiempo máximo de ejecución: {MAX_RUNTIME_MINUTES} minutos."
          if MAX_RUNTIME_MINUTES else "Sin límite de tiempo."
          f"\n📁 Guardando resultados en: {os.path.abspath(output_filename)}\n")
    print("tiempo de inicio:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)))
    print("tiempo final estimado:",
           time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(start_time + (MAX_RUNTIME_MINUTES * 60))) 
                          if MAX_RUNTIME_MINUTES else "Sin límite de tiempo")
    try:
        for site_key, site_config in SITES_CONFIG.items():
            
            # --- VERIFICACIÓN DE LÍMITES AL INICIO DE CADA CICLO ---
            elapsed_seconds = time.time() - start_time
            if MAX_RUNTIME_MINUTES is not None and elapsed_seconds > MAX_RUNTIME_MINUTES * 60:
                print(f"\n✋ LÍMITE DE TIEMPO ALCANZADO ({MAX_RUNTIME_MINUTES} min). Deteniendo el scraper.")
                break # Sale del bucle for

            if MAX_ITEMS is not None and len(all_results) >= MAX_ITEMS:
                print(f"\n✋ LÍMITE DE ÍTEMS ALCANZADO ({MAX_ITEMS}). Deteniendo el scraper.")
                break # Sale del bucle for

            # --- Lógica de scraping (sin cambios) ---
            results = []
            tool = site_config.get("tool", "cloudscraper")
            
            if tool == 'cloudscraper':
                results = scrape_site_with_cloudscraper(site_config)
            elif tool == 'selenium':
                results = scrape_site_with_selenium(site_config)
            
            if results:
                all_results.extend(results)
                print(f"   - ✅ Checkpoint. Total de ítems hasta ahora: {len(all_results)}. Guardando progreso...")
                save_to_csv(all_results, output_filename)
            
            # Pausa respetuosa
            if len(SITES_CONFIG) > 1 and site_key != list(SITES_CONFIG.keys())[-1]:
                print("\n----------------------------------------------------")
                time.sleep(3)

    except KeyboardInterrupt:
        print("\n\n🛑 Proceso interrumpido por el usuario. Procediendo a guardado de emergencia.")
    except Exception as e:
        print(f"\n🚨 OCURRIÓ UN ERROR INESPERADO: {e}")
        print("   - Procediendo al guardado de emergencia...")

    finally:
        # El guardado final de emergencia se mantiene igual
        print("\n--- Bloque 'finally' alcanzado. Realizando guardado final. ---")
        if all_results:
             save_to_csv(all_results, output_filename)
             print(f"\n💾 ¡GUARDADO FINAL REALIZADO! {len(all_results)} ítems en total fueron guardados en: {os.path.abspath(output_filename)}")
        else:
            print("   - No se recolectaron datos para el guardado final.")
        
        elapsed_final = time.time() - start_time
        print(f"\n⏱️ Tiempo total de ejecución: {elapsed_final / 60:.2f} minutos.")
        print("\n🏁 PROCESO DE SCRAPING COMPLETADO (o interrumpido de forma segura) 🏁")


if __name__ == "__main__":
    main()

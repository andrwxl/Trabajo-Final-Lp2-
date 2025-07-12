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
# scraper_config_atlas.py
#
# CONFIGURACIÓN CENTRAL DE SITIOS - "ATLAS MUNDIAL"
# -----------------------------------------------------
# Este es el "cerebro" de nuestro scraper. Cada entrada define un objetivo.
# Para activar un sitio, asegúrate de que su bloque no esté comentado.
# Para desactivarlo, comenta su bloque con '#' al inicio de cada línea.

SITES_CONFIG = {
    # ==============================================================================
    # NIVEL 1: SITIOS DE PRÁCTICA Y ESTÁTICOS (FÁCIL - Alta probabilidad de éxito)
    # Herramienta: cloudscraper
    # ==============================================================================
    "books_to_scrape": {
        "name": "Books to Scrape", "type": "Libro (Práctica)", "tool": "cloudscraper",
        "url": "http://books.toscrape.com/",
        "selectors": {
            "item_container": "article.product_pod",
            "title": "h3 a", "link": "h3 a", "author_instructor": None,
            "cost": "p.price_color", "level": "p.star-rating", "duration_effort": None
        }
    },
    "quotes_to_scrape": {
        "name": "Quotes to Scrape", "type": "Cita (Práctica)", "tool": "cloudscraper",
        "url": "http://quotes.toscrape.com/",
        "selectors": {
            "item_container": "div.quote", "title": "span.text", "link": "a",
            "author_instructor": "small.author",
            "cost": None, "level": None, "duration_effort": None
        }
    },
    "hacker_news": {
        "name": "Hacker News", "type": "Artículo de Tecnología", "tool": "cloudscraper",
        "url": "https://news.ycombinator.com/",
        "selectors": {
            "item_container": "tr.athing", "title": "span.titleline > a", "link": "span.titleline > a",
            "author_instructor": None, "cost": None, "level": None, "duration_effort": None
        }
    },
    "open_culture": {
        "name": "Open Culture", "type": "Agregador Cultural", "tool": "cloudscraper",
        "url": "https://www.openculture.com/freeonlinecourses",
        "selectors": {
            "item_container": "div.post > h2", "title": "a", "link": "a",
            "author_instructor": None, "cost": None, "level": None, "duration_effort": None
        }
    },
    "open_yale_courses": {
        "name": "Open Yale Courses", "type": "Curso Universitario", "tool": "cloudscraper",
        "url": "https://oyc.yale.edu/courses",
        "selectors": {
            "item_container": "tr.views-row", "title": "td.views-field-title a", "link": "td.views-field-title a",
            "author_instructor": "td.views-field-field-faculty-value", "cost": None, "level": None, "duration_effort": None
        }
    },

    # ==============================================================================
    # NIVEL 2: FUENTES DE CONTENIDO REAL (ESTÁTICAS - MEDIO)
    # Herramienta: cloudscraper
    # ==============================================================================
    "class_central": {
        "name": "Class Central", "type": "Índice de Materias", "tool": "cloudscraper",
        "url": "https://www.classcentral.com/subjects",
        "selectors": {
            "item_container": "a.l-subjects-page__subject-link", "title": "span.l-subjects-page__subject-label", "link": None,
            "author_instructor": None, "cost": None, "level": None, "duration_effort": "span.l-subjects-page__subject-course-count"
        }
    },
    "openstax": {
        "name": "OpenStax", "type": "Libro de Texto Universitario", "tool": "cloudscraper",
        "url": "https://openstax.org/subjects",
        "selectors": {
            "item_container": "div[data-is-qa='Book Legal Card']", "title": "h2, h3", "link": "a",
            "author_instructor": "p[class*='styles__Author']", "cost": None, "level": None, "duration_effort": None
        }
    },
    "project_gutenberg": {
        "name": "Project Gutenberg", "type": "Libro (Dominio Público)", "tool": "cloudscraper",
        "url": "https://www.gutenberg.org/ebooks/search/?sort_order=random",
        "selectors": {
            "item_container": "li.booklink", "title": "span.title", "link": "a.link",
            "author_instructor": "span.subtitle", "cost": None, "level": None, "duration_effort": None
        }
    },
    "dev_to": {
        "name": "Dev.to (Python)", "type": "Artículo de Programación", "tool": "cloudscraper",
        "url": "https://dev.to/t/python",
        "selectors": {
            "item_container": "article.crayons-story", "title": "h2.crayons-story__title a", "link": "h2.crayons-story__title a",
            "author_instructor": "p.profile-preview-card__name", "cost": None, "level": None, "duration_effort": "div.crayons-story__read-time"
        }
    },

    # ==============================================================================
    # NIVEL 3: SITIOS DINÁMICOS (DIFÍCIL - Requieren Selenium)
    # ¡DESAFÍO! Descomenta estos bloques para intentar scrapearlos.
    # Los selectores son frágiles y pueden necesitar actualización.
    # ==============================================================================
     "coursera": {
         "name": "Coursera (Data Science)", "type": "Curso Profesional", "tool": "selenium",
         "url": "https://www.coursera.org/search?query=data%20science",
         "selectors": {
             "item_container": "li.cds-9", "title": "h3.cds-CommonCard-title", "link": "a",
             "author_instructor": "span.partner-name", "cost": None,
             "level": "div[data-testid='card-metadata'] > p", "duration_effort": None
         }
     },
     "edx": {
         "name": "edX (Computer Science)", "type": "Curso Profesional", "tool": "selenium",
         "url": "https://www.edx.org/search?subject=Computer+Science",
         "selectors": {
             "item_container": "div.base-card-wrapper", "title": "h3.base-card-title", "link": "a.base-card-link",
             "author_instructor": "div.label-wrapper", "cost": None, "level": None, "duration_effort": None
         }
     },
     "udemy": {
         "name": "Udemy (Python)", "type": "Curso Profesional", "tool": "selenium",
         "url": "https://www.udemy.com/courses/search/?src=ukw&q=python",
         "selectors": {
             "item_container": "div[class*='course-card-main-content']", "title": "h3[data-purpose='course-title-url']", "link": "a",
             "author_instructor": "div[data-purpose='instructor-name']", "cost": "div[data-purpose='course-price-text'] span:nth-of-type(2)",
             "level": "div[data-purpose='course-meta-info'] span:nth-of-type(2)", "duration_effort": "div[data-purpose='course-meta-info'] span:nth-of-type(1)"
         }
     },
     "khan_academy": {
         "name": "Khan Academy (Math)", "type": "Lección / Curso", "tool": "selenium",
         "url": "https://www.khanacademy.org/math",
         "selectors": {
             "item_container": "div[class*='_1lfs2r4f']", "title": "span[class*='_e9bmo1']", "link": "a",
             "author_instructor": None, "cost": None, "level": None, "duration_effort": None
         }
     },

    # ==============================================================================
    # NIVEL 4: EL DESAFÍO FINAL (EXPERTO)
    # ==============================================================================
     "mit_ocw": {
         "name": "MIT OpenCourseWare", "type": "Curso Universitario (MIT)", "tool": "selenium",
         "url": "https://ocw.mit.edu/search/",
         "selectors": {
             "item_container": "li.course-card-list-item", "title": "h3", "link": "a",
             "author_instructor": "div[class*='course-card-faculty']", "cost": None,
             "level": "div[class*='course-card-level']", "duration_effort": None
         }
     },
     "platzi": {
         "name": "Platzi (Rutas)", "type": "Ruta de Aprendizaje", "tool": "selenium",
         "url": "https://platzi.com/rutas/",
         "selectors": {
             "item_container": "a.RouteCard", "title": "h3.RouteCard-title", "link": None,
             "author_instructor": None, "cost": None, "level": None, "duration_effort": "p.RouteCard-courses-text"
         }
     }
}

    # ==============================================================================
    # NIVEL 3: SITIOS DINÁMICOS (DIFÍCIL - Requieren Selenium)
    # ¡DESAFÍO! Descomenta estos bloques para intentar scrapearlos.
    # Los selectores son frágiles y pueden necesitar actualización.
    # ==============================================================================
    # "coursera": {
    #     "name": "Coursera (Data Science)", "type": "Curso Profesional", "tool": "selenium",
    #     "url": "https://www.coursera.org/search?query=data%20science",
    #     "selectors": {
    #         "item_container": "li.cds-9",
    #         "title": "h3.cds-CommonCard-title",
    #         "link": "a",
    #         "author_instructor": "span.partner-name",
    #         "cost": None,
    #         "level": "div[data-testid='card-metadata'] > p",
    #         "duration_effort": None
    #     }
    # },
    # "edx": {
    #     "name": "edX (Computer Science)", "type": "Curso Profesional", "tool": "selenium",
    #     "url": "https://www.edx.org/search?subject=Computer+Science",
    #     "selectors": {
    #         "item_container": "div.base-card-wrapper",
    #         "title": "h3.base-card-title",
    #         "link": "a.base-card-link",
    #         "author_instructor": "div.label-wrapper",
    #         "cost": None, "level": None, "duration_effort": None
    #     }
    # },
    # "udemy": {
    #     "name": "Udemy (Python)", "type": "Curso Profesional", "tool": "selenium",
    #     "url": "https://www.udemy.com/courses/search/?src=ukw&q=python",
    #     "selectors": {
    #         "item_container": "div.course-card-main-content--ZJppP",
    #         "title": "h3[data-purpose='course-title-url']",
    #         "link": "a",
    #         "author_instructor": "div[data-purpose='instructor-name']",
    #         "cost": "div[data-purpose='course-price-text'] span:nth-of-type(2)",
    #         "level": "div[data-purpose='course-meta-info'] span:nth-of-type(2)",
    #         "duration_effort": "div[data-purpose='course-meta-info'] span:nth-of-type(1)"
    #     }
    # },

    # ==============================================================================
    # NIVEL 4: EL DESAFÍO FINAL (EXPERTO)
    # ==============================================================================
    # "mit_ocw": {
    #     "name": "MIT OpenCourseWare", "type": "Curso Universitario (MIT)", "tool": "selenium",
    #     "url": "https://ocw.mit.edu/search/",
    #     "selectors": {
    #         "item_container": "li.course-card-list-item",
    #         "title": "h3",
    #         "link": "a",
    #         "author_instructor": "div[class*='course-card-faculty']",
    #         "cost": None,
    #         "level": "div[class*='course-card-level']",
    #         "duration_effort": None
    #     }
    # }

# ==============================================================================
# 2. MOTORES DE SCRAPING (MEJORADOS)
# ==============================================================================
def scrape_site_with_cloudscraper(site_config):
    name = site_config["name"]
    print(f"\n🔎 Usando [Cloudscraper] para: '{name}'...")
    scraper = cloudscraper.create_scraper()
    
    # ¡MEJORA! Bucle de reintentos para errores de red
    for attempt in range(3):
        try:
            response = scraper.get(site_config["url"], timeout=20)
            response.raise_for_status()
            print(f"   - Página descargada correctamente en el intento {attempt + 1}.")
            soup = BeautifulSoup(response.text, 'html.parser')
            return extract_data_from_soup(soup, site_config)
        except requests.exceptions.RequestException as e:
            print(f"   - ⚠️ Intento {attempt + 1} fallido por error de red: {e}")
            if attempt < 2:
                print("   - Esperando 5 segundos para reintentar...")
                time.sleep(5)
            else:
                print(f"   - ❌ Fallaron todos los intentos para '{name}'.")
    return []

def scrape_site_with_selenium(site_config):
    name = site_config["name"]
    selectors = site_config["selectors"]
    print(f"\n🔎 Usando [Selenium] para: '{name}'...")
    driver = init_selenium_driver()
    if not driver: return []
    
    try:
        driver.get(site_config["url"])
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["item_container"])))
        print("   - Página dinámica cargada y lista de ítems encontrada.")
        time.sleep(5)
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

def get_text_or_na(element, selector):
    """Función auxiliar para obtener texto de un sub-elemento o devolver 'N/A'."""
    if not selector: return "N/A"
    found_el = element.select_one(selector)
    return found_el.get_text(strip=True) if found_el else "N/A"

def get_link_or_na(element, selector, base_url):
    """Función auxiliar para obtener un enlace completo o devolver 'N/A'."""
    if selector is None: # Si el link es el propio contenedor
        link_element = element
    else:
        link_element = element.select_one(selector)
    
    if not link_element: return "N/A"
    
    relative_url = link_element.get('href')
    return urljoin(base_url, relative_url) if relative_url else "N/A"

def extract_data_from_soup(soup, site_config):
    """Función universal y robusta para extraer todos los datos de un objeto BeautifulSoup."""
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

# ==============================================================================
# 3. FUNCIÓN PARA GUARDAR EN CSV
# ==============================================================================
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
    print("🚀 INICIANDO SCRAPER DEFINITIVO V2 🚀")
    all_results = []
    for site_key, site_config in SITES_CONFIG.items():
        results = []
        tool = site_config.get("tool", "cloudscraper") # Cloudscraper por defecto
        
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

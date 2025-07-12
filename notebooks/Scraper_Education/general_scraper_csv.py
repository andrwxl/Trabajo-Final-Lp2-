# general_scraper_csv.py
#
# VERSIÓN MULTI-SITIO CON SALIDA A CSV
# Utiliza Cloudscraper y BeautifulSoup para extraer datos de sitios configurados.
#
# Requisitos:
# ------------------------------------------------------------------
# cloudscraper
# beautifulsoup4
# ------------------------------------------------------------------

import requests
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv
import os

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
# ¡Aquí está la magia! Para añadir un nuevo sitio, solo tienes que añadir
# una nueva entrada a este diccionario con sus selectores correspondientes.

SITES_CONFIG = {
    "class_central_subjects": {
        "name": "Class Central",
        "url": "https://www.classcentral.com/subjects",
        "item_container_selector": "a.l-subjects-page__subject-link",
        "title_selector": "span.l-subjects-page__subject-label",
        "link_selector": None  # El contenedor ya es el enlace
    },
    "hacker_news": {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "item_container_selector": "tr.athing",  # Cada noticia es una fila con la clase 'athing'
        "title_selector": "span.titleline > a", # El título está en un enlace dentro de un span
        "link_selector": "span.titleline > a"   # El enlace es el mismo que el del título
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
    
    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        print(f"   - Página '{name}' descargada correctamente.")

        soup = BeautifulSoup(response.text, 'html.parser')
        item_elements = soup.select(item_selector)
        
        if not item_elements:
            print(f"   - ❌ No se encontraron ítems con el selector '{item_selector}'.")
            return []

        print(f"   - ✅ ¡Éxito! Se encontraron {len(item_elements)} ítems. Extrayendo datos...")
        
        scraped_data = []
        for item in item_elements:
            title_element = item.select_one(title_selector) if title_selector else item
            link_element = item if link_selector is None else item.select_one(link_selector)
            
            if title_element and link_element:
                title = title_element.get_text(strip=True)
                # Para Hacker News, algunos enlaces son internos y otros externos. urljoin lo maneja bien.
                relative_url = link_element.get('href')
                full_url = urljoin(url, relative_url)
                
                if title and full_url:
                    scraped_data.append({
                        "titulo": title,
                        "url": full_url,
                        "fuente": name,
                        "categoria": name 
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
# 3. FUNCIÓN PARA GUARDAR EN CSV
# ==============================================================================
def save_to_csv(all_items, filename="conocimiento_extraido.csv"):
    """
    Guarda una lista de diccionarios en un archivo CSV.
    """
    if not all_items:
        print("No se encontraron ítems para guardar en el archivo CSV.")
        return

    fieldnames = all_items[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_items)
        
    print(f"\n💾 ¡Éxito! {len(all_items)} ítems guardados en el archivo: {os.path.abspath(filename)}")

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO SCRAPER WEB (VERSIÓN MULTI-SITIO) 🚀")
    
    all_results = []

    for site_key, site_config in SITES_CONFIG.items():
        results = scrape_site_with_cloudscraper(site_config)
        if results:
            all_results.extend(results)
        
        if len(SITES_CONFIG) > 1 and site_key != list(SITES_CONFIG.keys())[-1]:
            print("   - Pausando por 2 segundos antes del siguiente sitio...")
            time.sleep(2)

    save_to_csv(all_results)

    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

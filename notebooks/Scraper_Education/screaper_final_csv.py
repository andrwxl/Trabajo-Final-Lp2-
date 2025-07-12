# general_scraper_csv.py
#
# VERSIÓN FINAL CON SALIDA A CSV
# Utiliza Cloudscraper y BeautifulSoup y guarda los resultados en un archivo CSV.
#
# Requisitos:
# ------------------------------------------------------------------
# cloudscraper
# beautifulsoup4
# ------------------------------------------------------------------

import requests
import cloudscraper
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urljoin
import time
import csv # Módulo para manejar archivos CSV
import os  # Módulo para interactuar con el sistema operativo

# ==============================================================================
# 1. CONFIGURACIÓN CENTRAL DE SITIOS
# ==============================================================================
SITES_CONFIG = {
    "class_central_subjects": {
        "name": "Class Central",
        "url": "https://www.classcentral.com/subjects",
        "item_container_selector": "a.l-subjects-page__subject-link",
        "title_selector": "span.l-subjects-page__subject-label",
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
    
    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        print("   - Página descargada correctamente.")

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
# 3. NUEVA FUNCIÓN PARA GUARDAR EN CSV
# ==============================================================================
def save_to_csv(all_items, filename="conocimiento_extraido.csv"):
    """
    Guarda una lista de diccionarios en un archivo CSV.
    Sobrescribe el archivo en cada ejecución para tener un reporte limpio.
    """
    if not all_items:
        print("No se encontraron ítems para guardar en el archivo CSV.")
        return

    # Define los nombres de las columnas (el encabezado).
    # Usamos los keys del primer diccionario en la lista.
    fieldnames = all_items[0].keys()
    
    # Usamos 'w' (write) para crear un archivo nuevo cada vez.
    # newline='' es importante para evitar filas en blanco en Windows.
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribe la fila del encabezado.
        writer.writeheader()
        
        # Escribe todas las filas de datos.
        writer.writerows(all_items)
        
    # Imprime un mensaje de confirmación con la ubicación del archivo.
    print(f"\n💾 ¡Éxito! {len(all_items)} ítems guardados en el archivo: {os.path.abspath(filename)}")


# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO SCRAPER WEB (VERSIÓN CON SALIDA A CSV) 🚀")
    
    all_results = []

    # Itera a través de cada sitio definido en la configuración.
    for site_key, site_config in SITES_CONFIG.items():
        results = scrape_site_with_cloudscraper(site_config)
        if results:
            # Acumula los resultados de todos los sitios en una sola lista.
            all_results.extend(results)
        
        if len(SITES_CONFIG) > 1:
            print("   - Pausando por 2 segundos antes del siguiente sitio...")
            time.sleep(2)

    # Guarda todos los resultados acumulados en el archivo CSV al final.
    save_to_csv(all_results)

    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")

if __name__ == "__main__":
    main()

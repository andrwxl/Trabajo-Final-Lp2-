# skill_scraper.py
#
# Este script realiza web scraping en la plataforma Platzi para buscar cursos
# relacionados con habilidades específicas, y guarda los resultados en una base de datos SQLite.
#
# Requisitos (guarda esto en un archivo requirements.txt y ejecuta 'pip install -r requirements.txt'):
# ---------------------------------------------------------------------------------------------
# selenium
# webdriver-manager
# ---------------------------------------------------------------------------------------------

import time
import sqlite3
from abc import ABC, abstractmethod

# --- Selenium Imports ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ==============================================================================
# 1. CLASE BASE PARA SCRAPERS
# ==============================================================================
class BaseScraper(ABC):
    """
    Clase base abstracta para nuestros scrapers.
    Define la estructura y la interfaz que todos los scrapers específicos deben seguir.
    """
    def __init__(self, source_name, base_url):
        self.source_name = source_name
        self.base_url = base_url
        self.driver = self._init_driver()
        print(f"✅ Scraper para '{self.source_name}' inicializado.")

    def _init_driver(self):
        """Inicializa el WebDriver de Selenium con configuraciones comunes."""
        chrome_options = Options()
        # Identificamos nuestro bot con un User-Agent personalizado.
        chrome_options.add_argument("user-agent=SkillScraperBot/1.0 (Proyecto Educativo)")
        # Opcional: ejecutar en modo "headless" (sin abrir una ventana de navegador visible)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    @abstractmethod
    def scrape(self, skill_keyword):
        """
        Método principal que debe ser implementado por cada scraper hijo.
        Debe contener la lógica específica para extraer datos de su sitio web.
        """
        pass

    def close(self):
        """Cierra el navegador y libera los recursos."""
        if self.driver:
            self.driver.quit()
            print(f"✅ Navegador para '{self.source_name}' cerrado.")

# ==============================================================================
# 2. SCRAPER ESPECÍFICO PARA PLATZI (VERSIÓN CORREGIDA Y ACTUALIZADA)
# ==============================================================================
class PlatziScraper(BaseScraper):
    """
    Implementación del scraper para la plataforma Platzi.
    Hereda de BaseScraper y contiene la lógica para buscar y extraer cursos.
    VERSIÓN ACTUALIZADA: Maneja el banner de cookies y usa selectores corregidos.
    """
    def __init__(self):
        super().__init__(source_name="Platzi", base_url="https://platzi.com")

    def scrape(self, skill_keyword):
        """
        Realiza el proceso de scraping en Platzi para una habilidad dada.
        """
        print(f"\n🔎 Buscando '{skill_keyword}' en {self.source_name}...")
        try:
            self.driver.get(self.base_url)
            
            # --- NUEVO PASO: Manejar el banner de cookies ---
            # Intentamos encontrar y hacer clic en el botón "Entendido" del banner de cookies.
            try:
                # Usamos XPATH porque el texto 'Entendido' es un buen identificador.
                cookie_button_locator = (By.XPATH, "//button[contains(text(), 'Entendido')]")
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(cookie_button_locator)
                )
                cookie_button.click()
                print("   - Banner de cookies aceptado.")
                time.sleep(1) # Pequeña pausa para que el banner desaparezca.
            except TimeoutException:
                # Si no encontramos el botón en 5 segundos, asumimos que no está y continuamos.
                print("   - No se encontró el banner de cookies, continuando...")

            # --- Paso 1: Abrir la barra de búsqueda ---
            search_button_locator = (By.CSS_SELECTOR, "button[aria-label='Buscar']")
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(search_button_locator)
            )
            search_button.click()
            print("   - Barra de búsqueda abierta.")

            # --- Paso 2: Escribir en el campo de búsqueda y presionar Enter ---
            search_input_locator = (By.CSS_SELECTOR, "input[name='search']")
            search_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(search_input_locator)
            )
            search_input.send_keys(skill_keyword)
            search_input.send_keys(Keys.RETURN)
            print(f"   - Buscando cursos para '{skill_keyword}'.")

            # --- Paso 3: Esperar a que la página de resultados cargue ---
            # El contenedor de resultados ahora tiene el id 'search-results'.
            results_container_locator = (By.ID, "search-results")
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(results_container_locator)
            )
            print("   - Página de resultados cargada.")
            time.sleep(3) # Pausa cortés para asegurar que todo el JS renderice.

            # --- Paso 4: Extraer los datos de los cursos (con selectores actualizados) ---
            course_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.SearchResult-item-wrapper")
            
            if not course_elements:
                print(f"   - No se encontraron resultados para '{skill_keyword}'.")
                return []

            print(f"   - Se encontraron {len(course_elements)} resultados. Extrayendo datos...")
            
            scraped_data = []
            for course_element in course_elements:
                try:
                    # El título ahora está en una etiqueta h3 con la clase 'Card-title'
                    title = course_element.find_element(By.CSS_SELECTOR, "h3.Card-title").text
                    url = course_element.get_attribute('href')
                    
                    if title and url:
                        scraped_data.append({
                            "title": title,
                            "url": url,
                            "source": self.source_name,
                            "skill": skill_keyword
                        })
                except NoSuchElementException:
                    continue
            
            print(f"   - Extracción completada. {len(scraped_data)} cursos procesados.")
            return scraped_data

        except TimeoutException as e:
            print(f"   - Error: Tiempo de espera agotado. El sitio puede haber cambiado o la red es lenta.")
            print(f"   - Detalle del error: {e}")
            return []
        except Exception as e:
            print(f"   - Ocurrió un error inesperado al scrapear {self.source_name}: {e}")
            return []

# ==============================================================================
# 3. MANEJADOR DE LA BASE DE DATOS
# ==============================================================================
class DatabaseManager:
    """
    Clase para manejar todas las operaciones con la base de datos SQLite.
    """
    def __init__(self, db_name="skills_knowledge.db"):
        self.db_name = db_name
        self.conn = None
        print(f"📚 Manejador de base de datos para '{db_name}' listo.")

    def _connect(self):
        """Establece la conexión a la base de datos."""
        self.conn = sqlite3.connect(self.db_name)
        # Esto permite que los resultados de las consultas se parezcan a diccionarios.
        self.conn.row_factory = sqlite3.Row

    def _disconnect(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    def create_table(self):
        """Crea la tabla 'courses' si no existe."""
        self._connect()
        cursor = self.conn.cursor()
        # La restricción 'UNIQUE (url)' es clave para evitar duplicados.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT NOT NULL,
                skill TEXT NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        self._disconnect()
        print("   - Tabla 'courses' asegurada en la base de datos.")

    def save_courses(self, courses_data):
        """Guarda una lista de diccionarios de cursos en la base de datos."""
        if not courses_data:
            return
            
        self._connect()
        cursor = self.conn.cursor()
        
        # 'INSERT OR IGNORE' es una instrucción de SQLite que ignora la inserción
        # si se viola una restricción UNIQUE (en nuestro caso, la URL).
        # Esto previene errores y duplicados de forma muy eficiente.
        sql_query = 'INSERT OR IGNORE INTO courses (title, url, source, skill) VALUES (?, ?, ?, ?)'
        
        # Transformamos la lista de diccionarios al formato que necesita executemany
        data_to_insert = [(c['title'], c['url'], c['source'], c['skill']) for c in courses_data]
        
        cursor.executemany(sql_query, data_to_insert)
        
        # 'rowcount' nos dice cuántas filas fueron realmente insertadas.
        rows_added = cursor.rowcount 
        self.conn.commit()
        self._disconnect()
        print(f"   - {rows_added} nuevos cursos guardados en la base de datos.")

    def get_all_courses(self):
        """Obtiene y devuelve todos los cursos de la base de datos."""
        self._connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY skill, source")
        courses = [dict(row) for row in cursor.fetchall()]
        self._disconnect()
        return courses

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO PROCESO DE SCRAPING DE HABILIDADES 🚀")

    # --- Configuración ---
    skills_to_find = ["Machine Learning", "Ciberseguridad", "Bases de Datos", "Python"]
    scrapers_to_run = [PlatziScraper()] # En el futuro, puedes añadir más: [PlatziScraper(), CourseraScraper()]
    
    db_manager = DatabaseManager()
    db_manager.create_table()

    # --- Bucle Principal ---
    for scraper in scrapers_to_run:
        try:
            for skill in skills_to_find:
                # Hacemos scraping para una habilidad
                results = scraper.scrape(skill)
                
                # Guardamos los resultados en la base de datos
                if results:
                    db_manager.save_courses(results)
                
                # Pausa respetuosa entre búsquedas
                print("   - Pausando por 5 segundos antes de la siguiente búsqueda...")
                time.sleep(5)
        finally:
            # Nos aseguramos de que el navegador se cierre siempre, incluso si hay un error.
            scraper.close()

    # --- Finalización ---
    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")
    all_data = db_manager.get_all_courses()
    print(f"\n📊 Total de cursos en la base de datos: {len(all_data)}")
    print("Mostrando algunos resultados guardados:")
    for course in all_data[:10]: # Muestra los primeros 10 para verificar
        print(f"   - [{course['skill']}] {course['title']} ({course['source']})")


if __name__ == "__main__":
    main()


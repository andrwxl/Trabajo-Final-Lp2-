# skill_scraper.py
#
# Este script realiza web scraping en el catálogo de cursos de MIT OpenCourseWare
# para extraer cursos y guardarlos en una base de datos SQLite.
#
# Requisitos (guarda esto en un archivo requirements.txt y ejecuta 'pip install -r requirements.txt'):
# ---------------------------------------------------------------------------------------------
# selenium
# webdriver-manager
# ---------------------------------------------------------------------------------------------

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
# 1. CLASE BASE PARA SCRAPERS (Sin cambios)
# ==============================================================================
class BaseScraper(ABC):
    """
    Clase base abstracta para nuestros scrapers.
    Define la estructura y la interfaz que todos los scrapers específicos deben seguir.
    """
    def __init__(self, source_name):
        self.source_name = source_name
        self.driver = self._init_driver()
        print(f"✅ Scraper para '{self.source_name}' inicializado.")

    def _init_driver(self):
        """Inicializa el WebDriver de Selenium con configuraciones comunes."""
        chrome_options = Options()
        chrome_options.add_argument("user-agent=SkillScraperBot/1.0 (Proyecto Educativo)")
        # Descomenta la siguiente línea para ejecutar sin abrir una ventana de navegador
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    @abstractmethod
    def scrape(self, url_to_scrape, skill_category):
        """
        Método principal que debe ser implementado por cada scraper hijo.
        """
        pass

    def close(self):
        """Cierra el navegador y libera los recursos."""
        if self.driver:
            self.driver.quit()
            print(f"✅ Navegador para '{self.source_name}' cerrado.")

# ==============================================================================
# 2. SCRAPER PARA MIT OPENCOURSEWARE (VERSIÓN MÁS ROBUSTA)
# ==============================================================================
class MitOcwScraper(BaseScraper):
    """
    Implementación del scraper para la plataforma MIT OpenCourseWare (OCW).
    VERSIÓN MEJORADA: Aumenta el tiempo de espera y cambia la condición de espera para mayor robustez.
    """
    def __init__(self):
        super().__init__(source_name="MIT OpenCourseWare")

    def scrape(self, url_to_scrape, skill_category):
        """
        Realiza el proceso de scraping en una URL de colección de MIT OCW.
        """
        print(f"\n🔎 Buscando cursos de '{skill_category}' en {self.source_name}...")
        try:
            self.driver.get(url_to_scrape)
            
            # --- Paso 1: Esperar a que las tarjetas de los cursos carguen (con mejoras) ---
            container_locator = (By.ID, "course-cards-container")
            
            # MEJORA 1: Aumentamos el tiempo de espera a 30 segundos.
            wait = WebDriverWait(self.driver, 30) 
            
            # MEJORA 2: Cambiamos la condición a 'presence_of_element_located'.
            # Esto solo verifica que el contenedor exista en el HTML, sin importar si es visible.
            # Es una condición más fiable y menos propensa a fallos por elementos que tapan la vista.
            wait.until(
                EC.presence_of_element_located(container_locator)
            )
            print("   - Contenedor de cursos encontrado en el HTML.")
            
            # Damos una pausa adicional para que el contenido visual termine de cargar.
            time.sleep(3)

            # --- Paso 2: Extraer los datos de cada curso ---
            course_elements = self.driver.find_elements(By.CSS_SELECTOR, "article.course-card")
            
            if not course_elements:
                print(f"   - No se encontraron cursos en la página.")
                return []

            print(f"   - Se encontraron {len(course_elements)} cursos. Extrayendo datos...")
            
            scraped_data = []
            for course_element in course_elements:
                try:
                    link_element = course_element.find_element(By.CSS_SELECTOR, "a")
                    title = link_element.find_element(By.CSS_SELECTOR, "h3.course-card-title").text
                    relative_url = link_element.get_attribute('href')
                    full_url = urljoin("https://ocw.mit.edu/", relative_url)
                    
                    if title and full_url:
                        scraped_data.append({
                            "title": title.strip(),
                            "url": full_url,
                            "source": self.source_name,
                            "skill": skill_category
                        })
                except NoSuchElementException:
                    continue
            
            print(f"   - Extracción completada. {len(scraped_data)} cursos procesados.")
            return scraped_data

        except TimeoutException:
            print(f"   - Error: Tiempo de espera agotado incluso con 30 segundos. El sitio puede estar caído o bloqueando el acceso.")
            return []
        except Exception as e:
            print(f"   - Ocurrió un error inesperado al scrapear {self.source_name}: {e}")
            return []

# ==============================================================================
# 3. MANEJADOR DE LA BASE DE DATOS (Sin cambios)
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
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row

    def _disconnect(self):
        if self.conn:
            self.conn.close()

    def create_table(self):
        self._connect()
        cursor = self.conn.cursor()
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
        if not courses_data:
            return
        self._connect()
        cursor = self.conn.cursor()
        sql_query = 'INSERT OR IGNORE INTO courses (title, url, source, skill) VALUES (?, ?, ?, ?)'
        data_to_insert = [(c['title'], c['url'], c['source'], c['skill']) for c in courses_data]
        cursor.executemany(sql_query, data_to_insert)
        rows_added = cursor.rowcount 
        self.conn.commit()
        self._disconnect()
        print(f"   - {rows_added} nuevos cursos guardados en la base de datos.")

    def get_all_courses(self):
        self._connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY skill, source")
        courses = [dict(row) for row in cursor.fetchall()]
        self._disconnect()
        return courses

# ==============================================================================
# 4. SCRIPT PRINCIPAL DE EJECUCIÓN (Sin cambios)
# ==============================================================================
def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("🚀 INICIANDO PROCESO DE SCRAPING DE HABILIDADES EN MIT OCW 🚀")

    # --- Configuración ---
    targets = {
        "Computer Science": "https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/",
        "Data Science": "https://ocw.mit.edu/topics/data-science/",
        "Mechanical Engineering": "https://ocw.mit.edu/courses/mechanical-engineering/",
        "Mathematics": "https://ocw.mit.edu/courses/mathematics/"
    }
    
    scraper = MitOcwScraper()
    db_manager = DatabaseManager()
    db_manager.create_table()

    # --- Bucle Principal ---
    try:
        for skill, url in targets.items():
            results = scraper.scrape(url, skill)
            if results:
                db_manager.save_courses(results)
            if len(targets) > 1:
                print("   - Pausando por 5 segundos antes de la siguiente categoría...")
                time.sleep(5)
    finally:
        scraper.close()

    # --- Finalización ---
    print("\n🏁 PROCESO DE SCRAPING COMPLETADO 🏁")
    all_data = db_manager.get_all_courses()
    print(f"\n📊 Total de cursos en la base de datos: {len(all_data)}")
    if all_data:
        print("Mostrando todos los resultados guardados:")
        for course in all_data:
            print(f"   - [{course['skill']}] {course['title']} ({course['source']})")


if __name__ == "__main__":
    main()

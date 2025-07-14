Documentación Arquitectónica: Framework de Scraping v11.0
Este documento detalla la estructura, lógica y funcionamiento del script de web scraping. Ha sido diseñado como un framework modular, robusto y a prueba de fallos para la recolección de datos a gran escala.

# 1. CONFIGURACIÓN CENTRAL DE SITIOS - "EL ATLAS"

SITES_CONFIG = {
    "books_to_scrape": {
        # ...
    },
    "coursera": {
        # ...
    },
    # ... más sitios
}

## ¿Qué es SITES_CONFIG?
E
s el cerebro y panel de control de todo el scraper. Este diccionario de Python contiene las "órdenes de trabajo" para cada sitio web que queremos analizar.

## Su Diseño Modular

En lugar de tener un código diferente para cada sitio, centralizamos la configuración aquí. Para añadir un nuevo sitio, simplemente se agrega una nueva entrada a este diccionario. Cada entrada contiene:

name: Un nombre legible para los logs (Ej: "Books to Scrape").

type: El tipo de recurso que se extrae (Ej: "Libro (Práctica)").

tool: La herramienta necesaria para el trabajo. cloudscraper para sitios estáticos y selenium para sitios dinámicos y complejos.

url: La dirección de inicio para el scraping.

pagination_selector: (Opcional) El selector CSS para encontrar el botón o enlace "Siguiente Página".

selectors: Un "mapa del tesoro" con los selectores CSS para encontrar cada dato específico:

item_container: El contenedor principal de cada ítem en la lista.

title, link, cost, etc.: Los selectores para los datos individuales dentro de cada contenedor.

Ventaja: Esta estructura hace que el scraper sea increíblemente escalable y fácil de mantener.

# 2. MOTORES DE SCRAPING - "LAS LÍNEAS DE ENSAMBLAJE"
El framework cuenta con dos motores de scraping especializados, y el script principal elige el adecuado según la configuración del sitio.

## scrape_site_with_cloudscraper(site_config, existing_urls, output_filename)
Esta es nuestra línea de ensamblaje estándar y de alta velocidad.

Propósito: Diseñada para sitios web estáticos donde el contenido se carga directamente en el HTML.

Funcionamiento:

Utiliza cloudscraper para descargar el HTML de una página, simulando ser un navegador y evitando protecciones básicas.

Entra en un bucle while que dura mientras encuentre un botón de "Siguiente Página" (definido en pagination_selector).

En cada página, extrae los ítems, los filtra para no añadir duplicados (usando existing_urls) y los guarda directamente en el archivo CSV mediante append_to_csv.

Construye la URL de la siguiente página y repite el proceso.

## scrape_site_with_selenium(site_config, existing_urls, output_filename, start_time, limits)
Esta es nuestra línea de ensamblaje de alta tecnología y para trabajos pesados.

Propósito: Diseñada para sitios web dinámicos y complejos (como Coursera) que dependen de JavaScript para cargar su contenido.

Funcionamiento:

Inicia una instancia completa del navegador Chrome usando Selenium.

Entra en un gran bucle while para manejar la paginación principal (clics en "Siguiente Página").

Dentro de ese bucle, entra en otro bucle para manejar la carga de contenido de la página actual. Implementa la lógica de "scroll humano":

Hace scroll suavemente hasta el último elemento visible.

Espera a que se cargue nuevo contenido.

Repite este proceso hasta que la página deja de crecer, asegurando que todo el contenido "perezoso" (lazy-loaded) se cargue.

Verifica constantemente los límites de tiempo y cantidad para detenerse de forma segura si es necesario.

Al igual que Cloudscraper, extrae los datos, filtra duplicados y los guarda en tiempo real en el archivo CSV.

# 3. LÓGICA DE EXTRACCIÓN Y GUARDADO - "HERRAMIENTAS DE PRECISIÓN Y LOGÍSTICA"
Estas son las funciones auxiliares que hacen que todo el sistema funcione de manera robusta y reutilizable.

## init_selenium_driver()
Propósito: Configura e inicia el navegador Selenium.

Características Clave:

Añade headers y otras opciones para que el navegador parezca lo más humano posible y evite ser detectado como un bot.

Establece tiempos de espera (timeouts) generosos para evitar que el script se cierre prematuramente en páginas lentas o muy pesadas.

## extract_data_from_soup(soup, site_config)
Propósito: Es el "brazo robótico" que extrae los datos.

Funcionamiento: Recibe el HTML parseado (soup) y la configuración del sitio. Itera sobre todos los item_container y usa los selectores específicos (title, link, etc.) para extraer cada pieza de información, devolviendo una lista de diccionarios.

## load_from_csv(filename)
Propósito: Implementa la capacidad de reanudar el trabajo.

Funcionamiento: Antes de que comience el scraping, esta función lee el archivo CSV de salida (si existe) y crea un set con todas las URLs que ya han sido guardadas. Esto es extremadamente rápido y eficiente.

## append_to_csv(items_to_add, filename)
Propósito: Es el núcleo del sistema a prueba de fallos.

Funcionamiento: En lugar de mantener los datos en memoria, esta función abre el archivo CSV en modo "append" ('a') y añade las nuevas filas encontradas inmediatamente. Si el archivo no existe, crea el encabezado primero. Esto garantiza que, incluso si el script se interrumpe, el progreso está a salvo en el disco duro.

# 4. SCRIPT PRINCIPAL DE EJECUCIÓN - "EL GERENTE DE PLANTA"
La función main() orquesta todo el proceso de principio a fin.

## main()
Propósito: Controlar el flujo general del scraper.

Funcionamiento:

Define los Límites: Establece las variables limits (ej. 10 minutos, 5000 ítems).

Carga el Progreso: Llama a load_from_csv para saber qué trabajo ya se ha hecho.

Bucle Principal: Itera sobre cada sitio en SITES_CONFIG.

Verificación de Límites: Antes de empezar con un nuevo sitio, comprueba si se ha alcanzado algún límite. Si es así, se detiene de forma segura.

Delegación: Llama a la función de scraping apropiada (cloudscraper o selenium), pasándole toda la información que necesita para hacer su trabajo y respetar los límites.

Manejo de Errores (try...finally): Envuelve todo el proceso en un bloque de seguridad. El bloque finally garantiza que, sin importar si el script termina bien, es interrumpido por el usuario (Ctrl+C) o sufre un error fatal, se ejecutará un último guardado y se mostrará un resumen final del estado del archivo y el tiempo de ejecución.
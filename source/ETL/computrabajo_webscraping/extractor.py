import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- CONFIGURACIÓN PRINCIPAL ---
PAISES = ['pe', 'co', 'cl', 'mx', 'ar']

# Palabras clave para las búsquedas de empleo.
PALABRAS_CLAVE = [
    #"informatica",
    #"datos",
    #"programacion",
    #"sistemas",
    #"python",
    #"power-bi",
    "sql",
    #"developer",
    #"excel",
    #"analista",
]

# Mapeo de códigos de país a nombres para el CSV
MAPEO_PAISES = {
    'pe': 'Perú',
    'co': 'Colombia',
    'cl': 'Chile',
    'mx': 'México',
    'ar': 'Argentina'
}
# Monedas segun pais
MONEDAS_PAISES = {
    'pe': 'PEN',  # Sol Peruano
    'co': 'COP',  # Peso Colombiano
    'cl': 'CLP',  # Peso Chileno
    'mx': 'MXN',  # Peso Mexicano
    'ar': 'ARS'   # Peso Argentino
}


def peticion_pagina(url):
    """
    Realiza una petición GET a la URL proporcionada con un User-Agent.
    Maneja posibles errores de conexión.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        respuesta = requests.get(url, headers=headers, timeout=15)
        respuesta.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx.
        return respuesta
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la petición a la URL {url}: {e}")
        return None

def extraer_datos_pagina(url, pais_codigo, categoria):
    """
    Extrae la información de todas las ofertas de una única página.
    Recibe el código del país para construir las URLs de las ofertas correctamente.
    """
    respuesta = peticion_pagina(url)
    if not respuesta:
        return []

    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    contenedores_ofertas = sopa.find_all('article', class_='box_offer')
    
    if not contenedores_ofertas:
        return []

    lista_ofertas = []
    # Itera sobre cada oferta para extraer sus datos
    for oferta in contenedores_ofertas:
        titulo_tag = oferta.find('a', class_='js-o-link fc_base')
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "NA"
        # Construcción dinámica de la URL de la oferta
        url_oferta = f"https://{pais_codigo}.computrabajo.com{titulo_tag['href']}" if titulo_tag and titulo_tag.has_attr('href') else "NA"
        
        empresa_tag = oferta.find('a', class_='fc_base t_ellipsis')
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "NA"

        # La ubicación puede estar en diferentes spans, buscamos de forma más flexible
        ubicacion_p = oferta.find('p', class_='fs16 fc_base mt5')
        ubicacion = ubicacion_p.find('span').get_text(strip=True) if ubicacion_p and ubicacion_p.find('span') else "NA"

        div_1 = oferta.find('div', class_='fs13 mt15')
        salario, modalidad = "NA", "NA"
        if div_1:
            spans_info = div_1.find_all('span', class_='dIB mr10')
            for span in spans_info:
                if span.find('span', class_='i_salary'):
                    salario = span.get_text(strip=True)
                elif span.find('span', class_='i_home_office'):
                    modalidad = span.get_text(strip=True)

        oferta_dict = {
            'puesto_trabajo': titulo,
            'nombre_empresa': empresa,
            'pais': MAPEO_PAISES.get(pais_codigo, pais_codigo), # Usa el nombre completo del país
            'region_estado': ubicacion,
            'categoria_busqueda': categoria,
            'tipo_contrato': modalidad,
            'salario': salario,
            'moneda_salario': MONEDAS_PAISES[pais_codigo],  # Usa la moneda del país
            'periodo_salario': 'Mensual',
            'plataforma_origen': 'Computrabajo',
            'tipo_fuente_datos': 'Web Scraping',
            'enlace_oferta': url_oferta,
        }
        lista_ofertas.append(oferta_dict)
        
    return lista_ofertas

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    datos_finales = []
    
    # Bucle principal que itera sobre cada país
    for pais in PAISES:
        # Bucle anidado que itera sobre cada palabra clave
        for palabra in PALABRAS_CLAVE:
            
            # Construye la URL base para la búsqueda actual
            url_base_busqueda = f"https://{pais}.computrabajo.com/trabajo-de-{palabra}"
            print(f"\n--- Iniciando scraping para '{palabra}' en '{MAPEO_PAISES.get(pais, pais)}' ---")
            
            numero_pagina = 1
            while True:
                if numero_pagina == 1:
                    url_actual = url_base_busqueda
                else:
                    # La paginación se maneja con ?p=NUMERO
                    url_actual = f"{url_base_busqueda}?p={numero_pagina}"
                
                print(f"Extrayendo datos de: {url_actual}")
                
                datos_de_la_pagina = extraer_datos_pagina(url_actual, pais, palabra)
                
                # Si la página no devuelve datos, rompemos el bucle para pasar a la siguiente categoría
                if not datos_de_la_pagina:
                    print(f"No se encontraron más ofertas para '{palabra}' en '{MAPEO_PAISES.get(pais, pais)}'. Pasando a la siguiente búsqueda.")
                    break
                    
                datos_finales.extend(datos_de_la_pagina)
                
                numero_pagina += 1
                #time.sleep(1) # Pausa cortés para no sobrecargar el servidor

    if datos_finales:
        df = pd.DataFrame(datos_finales)
        # Se recomienda guardar en un formato que soporte bien UTF-8, como CSV con la codificación especificada.
        nombre_archivo = "datos/crudos/computrabajo_multipaís.csv"
        try:
            # Asegúrate de que el directorio 'datos/crudos/' exista o guarda en el directorio actual.
            df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
            print(f"\n✅ ¡Éxito! {len(df)} ofertas extraídas y guardadas en '{nombre_archivo}'.")
        except Exception as e:
            print(f"Error al guardar el archivo CSV: {e}")
    else:
        print("\nNo se pudo extraer ninguna oferta de trabajo.")

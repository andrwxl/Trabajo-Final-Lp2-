import requests
from bs4 import BeautifulSoup
import pandas as pd

# Lista para almacenar las URLs de las ofertas de empleo.
urls_base = [
    "https://pe.computrabajo.com/trabajo-de-informatica",
    "https://pe.computrabajo.com/trabajo-de-datos",
    "https://pe.computrabajo.com/trabajo-de-programacion",
    "https://pe.computrabajo.com/trabajo-de-sistemas",
]

def peticion_pagina(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        respuesta = requests.get(url, headers=headers)
        respuesta.raise_for_status() # Lanza un error si la petición no fue exitosa.
        return respuesta
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la petición a la URL: {e}")
        return []

def extraer_datos_pagina(url):    
    respuesta = peticion_pagina(url)

    if not respuesta: return []

    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    contenedores_ofertas = sopa.find_all('article', class_='box_offer')
    
    if not contenedores_ofertas: return []
    #print(f"Se encontraron {len(contenedores_ofertas)} ofertas en la página.")
    lista_ofertas = []
    # Itera sobre cada oferta para extraer sus datos
    for oferta in contenedores_ofertas:
        
        titulo_tag = oferta.find('a', class_='js-o-link fc_base')
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "NA"
        
        empresa_tag = oferta.find('a', class_='fc_base t_ellipsis')
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "NA"

        ubicacion_tag = oferta.find('span', class_='loc')
        ubicacion = ubicacion_tag.get_text(strip=True) if ubicacion_tag else "NA"

        div_1 = oferta.find('div', class_='fs13 mt15')

        salario, modalidad = "NA", "NA" # Valores por defecto
        if div_1:
            spans_info = div_1.find_all('span', class_='dIB mr10')
            for span in spans_info:
                # Si el span contiene el ícono de salario...
                if span.find('span', class_='i_salary'):
                    salario = span.get_text(strip=True)
                    #print(f"Salario encontrado: {salario}")
                    # Si el span contiene el ícono de home office...
                elif span.find('span', class_='i_home_office'):
                    modalidad = span.get_text(strip=True)

        oferta_dict = {
            'titulo_puesto': titulo,
            'nombre_empresa': empresa,
            'ubicacion': ubicacion,
            "modalidad": modalidad,
            'salario': salario,
        }
        
        lista_ofertas.append(oferta_dict)
        
    return lista_ofertas

# --- PUNTO DE ENTRADA DEL SCRIPT ---
datos_finales = []
for url_empleo in urls_base:
    numero_pagina = 1
    while True:
        #print(f"Extrayendo datos de la página {numero_pagina} para la categoría: {url_empleo}")
        
        if numero_pagina == 1:
            url_actual = url_empleo
        else:
            url_actual = f"{url_empleo}?p={numero_pagina}"
        
        datos_de_la_pagina = extraer_datos_pagina(url_actual)
        
        if not datos_de_la_pagina:
            print(f"No se encontraron más ofertas. Deteniendo la extracción para esta categoría.")
            break
            
        datos_finales.extend(datos_de_la_pagina)
        
        numero_pagina += 1

df = pd.DataFrame(datos_finales)
nombre_archivo = "datos_crudos_computrabajo.csv"
df.to_csv(f"datos/crudos/{nombre_archivo}", index=False)
print(f"Datos extraídos y guardados en {nombre_archivo}.")
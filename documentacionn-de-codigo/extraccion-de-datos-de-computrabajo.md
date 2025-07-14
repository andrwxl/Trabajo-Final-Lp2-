# EXTRACCION DE DATOS DE COMPUTRABAJO

---

### 🧩 **Fragmento 1: Importaciones y configuraciones iniciales**

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
```

#### 🔍 ¿Qué hace?

Este bloque importa las librerías necesarias para que el script funcione:

* `requests`: Permite hacer solicitudes HTTP (en este caso, para obtener el HTML de las páginas de empleo).
* `BeautifulSoup` (de `bs4`): Permite **parsear** y **navegar** por documentos HTML de forma estructurada.
* `pandas`: Para manipular y guardar datos en estructuras tipo DataFrame y exportarlos a CSV.
* `time`: Aquí se importa, pero solo se usa si se descomenta la línea de `time.sleep()`, que sirve para pausar la ejecución entre solicitudes (útil para evitar sobrecargar el servidor).

---

### 🧩 **Fragmento 2: Configuración de parámetros globales**

```python
PAISES = ['pe', 'co', 'cl', 'mx', 'ar']
```

#### 🔍 ¿Qué hace?

Define una **lista de códigos de países** para los cuales se hará scraping. Son los subdominios de Computrabajo:

* `'pe'` → Perú
* `'co'` → Colombia
* `'cl'` → Chile
* `'mx'` → México
* `'ar'` → Argentina

---

```python
PALABRAS_CLAVE = [
    "informatica",
    "datos",
    "programacion",
    "sistemas",
    "python",
    "power-bi",
    "sql",
    "developer",
    "excel",
    "analista",
]
```

#### 🔍 ¿Qué hace?

Define una lista de palabras clave para realizar búsquedas de empleo. Estas palabras son las que se insertarán en las URLs para buscar puestos relacionados (por ejemplo, `trabajo-de-python`).

---

### 🧩 **Fragmento 3: Mapeo de países y monedas**

#### 1️⃣ **MAPEO\_PAISES**

```python
MAPEO_PAISES = {
    'pe': 'Perú',
    'co': 'Colombia',
    'cl': 'Chile',
    'mx': 'México',
    'ar': 'Argentina'
}
```

#### 🔍 ¿Qué hace?

Este diccionario **convierte los códigos de país** (como `'pe'`, `'co'`, etc.) a su **nombre completo**.
Se usa para que el resultado final en el CSV sea más legible, mostrando “Perú” en lugar de “pe”, por ejemplo.

---

#### 2️⃣ **MONEDAS\_PAISES**

```python
MONEDAS_PAISES = {
    'pe': 'PEN',  # Sol Peruano
    'co': 'COP',  # Peso Colombiano
    'cl': 'CLP',  # Peso Chileno
    'mx': 'MXN',  # Peso Mexicano
    'ar': 'ARS'   # Peso Argentino
}
```

#### 🔍 ¿Qué hace?

Asigna el **código de la moneda oficial** a cada país.
Cuando el script extraiga el salario, también incluirá este código para estandarizar la moneda, por ejemplo:

* `'pe'` → `'PEN'`
* `'cl'` → `'CLP'`

Esto es útil si luego quieres comparar o convertir salarios entre países.

---

### 🧩 **Fragmento 4: Función `peticion_pagina(url)`**

```python
def peticion_pagina(url):
    """
    Realiza una petición GET a la URL proporcionada con un User-Agent.
    Maneja posibles errores de conexión.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
```

#### 🔍 ¿Qué hace esta primera parte?

* Define la función `peticion_pagina`, que recibe una URL.
* Establece un **User-Agent** personalizado dentro de los headers.
  Esto es importante porque algunos servidores bloquean peticiones que no parecen venir de un navegador real.

---

```python
    try:
        respuesta = requests.get(url, headers=headers, timeout=15)
        respuesta.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx.
        return respuesta
```

#### 🔍 ¿Qué hace?

* Usa `requests.get()` para hacer la solicitud HTTP con los headers definidos.
* Define un `timeout=15` segundos para evitar que el script quede colgado si la página no responde.
* `respuesta.raise_for_status()` lanza una excepción si el código de respuesta es un error (como 404 o 500).
* Si todo va bien, retorna el objeto `respuesta`, que contiene el contenido HTML de la página.

---

```python
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la petición a la URL {url}: {e}")
        return None
```

#### 🔍 ¿Qué hace?

* Captura cualquier tipo de error de red (`RequestException`).
* Muestra un mensaje con la URL problemática.
* Devuelve `None` para que el código que la llama sepa que **falló la conexión**.

---

### ✅ En resumen:

Esta función encapsula el comportamiento de hacer peticiones web de forma **segura** y **tolerante a fallos**. Si falla, devuelve `None`; si tiene éxito, devuelve la respuesta HTML.

---

### 🧩 **Fragmento 5: Cabecera de la función**

```python
def extraer_datos_pagina(url, pais_codigo, categoria):
    """
    Extrae la información de todas las ofertas de una única página.
    Recibe el código del país para construir las URLs de las ofertas correctamente.
    """
    respuesta = peticion_pagina(url)
    if not respuesta:
        return []
```

#### 🔍 ¿Qué hace esta parte?

* Se define la función con 3 argumentos:

  * `url`: la URL de la página de ofertas.
  * `pais_codigo`: código del país (`'pe'`, `'co'`, etc.) usado para construir la URL del enlace de cada oferta.
  * `categoria`: palabra clave con la que se buscó la oferta (ej. "python", "sql").

* Llama a la función `peticion_pagina(url)`:

  * Si **falla la solicitud** (devuelve `None`), retorna una **lista vacía**, indicando que no hay ofertas para esa página.

---

### 🧩 **Fragmento 6: Parseo del HTML y búsqueda de contenedores de ofertas**

```python
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    contenedores_ofertas = sopa.find_all('article', class_='box_offer')
    
    if not contenedores_ofertas:
        return []
```

#### 🔍 ¿Qué hace?

* Crea un objeto `sopa` con BeautifulSoup para poder navegar el HTML como estructura DOM.
* Busca todos los `<article>` con clase `'box_offer'`, que representan ofertas de trabajo individuales.
* Si no se encuentra ninguna oferta (lista vacía), también retorna una lista vacía.

---

### 🧩 **Fragmento 7: Iteración sobre las ofertas**

```python
    lista_ofertas = []
    # Itera sobre cada oferta para extraer sus datos
    for oferta in contenedores_ofertas:
```

#### 🔍 ¿Qué hace?

* Inicializa una lista vacía `lista_ofertas` donde se almacenarán los diccionarios con los datos extraídos de cada oferta.
* Recorre cada `oferta` (elemento `<article class="box_offer">`) dentro del HTML.

---

### 🧩 **Fragmento 8: Título del puesto y enlace de la oferta**

```python
        titulo_tag = oferta.find('a', class_='js-o-link fc_base')
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "NA"
        # Construcción dinámica de la URL de la oferta
        url_oferta = f"https://{pais_codigo}.computrabajo.com{titulo_tag['href']}" if titulo_tag and titulo_tag.has_attr('href') else "NA"
```

#### 🔍 ¿Qué hace?

* Busca el enlace al título de la oferta dentro de un `<a>` con clases `js-o-link fc_base`.
* Extrae el texto del enlace como el **nombre del puesto** (`titulo`). Si no se encuentra, asigna `"NA"`.
* Construye el **enlace completo a la oferta** combinando el subdominio del país (`{pais_codigo}`) y el atributo `href` del enlace.

  * Por ejemplo: `https://pe.computrabajo.com/oferta/ejemplo`.

---

### 🧩 **Fragmento 9: Nombre de la empresa**

```python
        empresa_tag = oferta.find('a', class_='fc_base t_ellipsis')
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "NA"
```

#### 🔍 ¿Qué hace?

* Busca el nombre de la empresa, que suele estar dentro de un enlace `<a class="fc_base t_ellipsis">`.
* Extrae el texto, o asigna `"NA"` si no existe.

---

### 🧩 **Fragmento 10: Ubicación geográfica**

```python
        ubicacion_p = oferta.find('p', class_='fs16 fc_base mt5')
        ubicacion = ubicacion_p.find('span').get_text(strip=True) if ubicacion_p and ubicacion_p.find('span') else "NA"
```

#### 🔍 ¿Qué hace?

* Busca el `<p>` que contiene la ubicación (ciudad o región).
* Luego busca el `<span>` interno que guarda el nombre de la ubicación.
* Si no se encuentra correctamente, retorna `"NA"`.

---

### 🧩 **Fragmento 11: Extracción del salario y la modalidad (remoto o presencial)**

```python
        div_1 = oferta.find('div', class_='fs13 mt15')
        salario, modalidad = "NA", "NA"
        if div_1:
            spans_info = div_1.find_all('span', class_='dIB mr10')
            for span in spans_info:
                if span.find('span', class_='i_salary'):
                    salario = span.get_text(strip=True)
                elif span.find('span', class_='i_home_office'):
                    modalidad = span.get_text(strip=True)
```

#### 🔍 ¿Qué hace este bloque?

1. **`div_1`**: Busca el `<div class="fs13 mt15">` que normalmente contiene los iconos de información adicional como salario y tipo de modalidad.
2. Inicializa `salario` y `modalidad` como `"NA"` por defecto.
3. Si `div_1` existe:

   * Busca todos los `<span>` que contienen íconos + texto (`class="dIB mr10"`).
   * Dentro de cada uno:

     * Si encuentra un `<span>` hijo con clase `i_salary`, extrae el texto como el **salario**.
     * Si encuentra un `<span>` hijo con clase `i_home_office`, extrae el texto como el tipo de **modalidad** (por ejemplo, "Remoto", "Presencial", etc.).

Este mecanismo es **flexible y robusto** ante pequeñas variaciones en el orden o estructura del HTML.

---

### 🧩 **Fragmento 12: Construcción del diccionario final de la oferta**

```python
        oferta_dict = {
            'puesto_trabajo': titulo,
            'nombre_empresa': empresa,
            'pais': MAPEO_PAISES.get(pais_codigo, pais_codigo),
            'region_estado': ubicacion,
            'categoria_busqueda': categoria,
            'tipo_contrato': modalidad,
            'salario': salario,
            'moneda_salario': MONEDAS_PAISES[pais_codigo],
            'periodo_salario': 'Mensual',
            'plataforma_origen': 'Computrabajo',
            'tipo_fuente_datos': 'Web Scraping',
            'enlace_oferta': url_oferta,
        }
        lista_ofertas.append(oferta_dict)
```

#### 🔍 ¿Qué hace?

1. Crea un diccionario con los campos estandarizados que se quieren guardar en el dataset.
2. Cada campo tiene una fuente distinta:

   * `puesto_trabajo`, `nombre_empresa`, `salario`, `modalidad`, etc., vienen de la oferta.
   * `pais` y `moneda_salario` se extraen desde los diccionarios `MAPEO_PAISES` y `MONEDAS_PAISES`.
   * Se añade el tipo de fuente (`Web Scraping`) y la plataforma (`Computrabajo`) para poder filtrar después.
3. Agrega ese diccionario a la lista `lista_ofertas`.

---

### 🧩 **Fragmento 13: Retorno de la función**

```python
    return lista_ofertas
```

#### 🔍 ¿Qué hace?

* Devuelve la lista con todas las ofertas encontradas y procesadas en esa página específica.
* Si no se encontró ninguna oferta válida o falló la conexión, devuelve una lista vacía (como vimos al inicio).

---

### 🧩 **Fragmento 14: Bloque principal de scraping y control**

```python
if __name__ == "__main__":
    datos_finales = []

    # Bucle principal que itera sobre cada país
    for pais in PAISES:
        # Bucle anidado que itera sobre cada palabra clave
        for palabra in PALABRAS_CLAVE:
            url_base_busqueda = f"https://{pais}.computrabajo.com/trabajo-de-{palabra}"
            print(f"\n--- Iniciando scraping para '{palabra}' en '{MAPEO_PAISES.get(pais, pais)}' ---")

            numero_pagina = 1
            while True:
                if numero_pagina == 1:
                    url_actual = url_base_busqueda
                else:
                    url_actual = f"{url_base_busqueda}?p={numero_pagina}"

                print(f"Extrayendo datos de: {url_actual}")
                datos_de_la_pagina = extraer_datos_pagina(url_actual, pais, palabra)

                if not datos_de_la_pagina:
                    print(f"No se encontraron más ofertas para '{palabra}' en '{MAPEO_PAISES.get(pais, pais)}'. Pasando a la siguiente búsqueda.")
                    break

                datos_finales.extend(datos_de_la_pagina)
                numero_pagina += 1
                #time.sleep(1)  # Desactivado para velocidad, pero recomendable activarlo si hay bloqueos
```

#### 🔍 ¿Qué hace?

* **Control de ejecución principal**: el bloque se ejecuta solo si el archivo se corre directamente (`__main__`).
* **`datos_finales`**: lista acumuladora donde se guardan todas las ofertas de todos los países y todas las búsquedas.
* **Doble bucle anidado**:

  * Externo → por cada país (`pe`, `co`, etc.).
  * Interno → por cada palabra clave de búsqueda (`python`, `sql`, etc.).
* Construye la URL base para cada búsqueda:
  Ejemplo: `https://pe.computrabajo.com/trabajo-de-python`
* Se hace scraping paginado:

  * Si hay resultados, se sigue avanzando de página (`?p=2`, `?p=3`, etc.).
  * Si no hay resultados en la página actual, rompe el bucle y pasa a la siguiente combinación país-palabra.

---

### 🧩 **Fragmento 15: Exportación de resultados a CSV**

```python
    if datos_finales:
        df = pd.DataFrame(datos_finales)
        nombre_archivo = "datos/crudos/computrabajo_multipaís.csv"
        try:
            df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
            print(f"\n✅ ¡Éxito! {len(df)} ofertas extraídas y guardadas en '{nombre_archivo}'.")
        except Exception as e:
            print(f"Error al guardar el archivo CSV: {e}")
    else:
        print("\nNo se pudo extraer ninguna oferta de trabajo.")
```

#### 🔍 ¿Qué hace?

* Verifica si se extrajo al menos una oferta (`datos_finales` no vacío).
* Crea un **DataFrame de pandas** con los datos.
* Intenta guardar el archivo en `"datos/crudos/computrabajo_multipaís.csv"` con codificación `utf-8-sig` (ideal para Excel).
* Si ocurre un error en la escritura del archivo, lo muestra en consola.
* Si no se extrajo nada, muestra un mensaje informativo.

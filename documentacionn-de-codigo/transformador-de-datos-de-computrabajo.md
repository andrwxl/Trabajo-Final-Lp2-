# TRANSFORMADOR DE DATOS DE COMPUTRABAJO

---

### 📄 **Parte 1: Importaciones, funciones auxiliares y carga de datos**

```python
import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from clustering import obtener_datos_ordenados_por_cluster
import re
from config import STOP_WORDS_ES
```

#### 📦 Importaciones

* Carga de librerías esenciales: `pandas`, `os`, `re`, `sklearn`, etc.
* `obtener_datos_ordenados_por_cluster()` carga el dataset ya agrupado por clusters.
* `STOP_WORDS_ES`: lista de palabras vacías en español para filtrar en los títulos.

---

```python
def eliminar_duplicados_por_columna(df, nombre_columna):
    return df.drop_duplicates(subset=[nombre_columna], keep='first')

def cargar_datos_cluster(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo no se encontró en la ruta '{ruta_archivo}'")
        return None
    print(f"Cargando archivo de clusters: {ruta_archivo}")
    return pd.read_csv(ruta_archivo)
```

#### 🧹 Funciones auxiliares

* `eliminar_duplicados_por_columna`: elimina duplicados en un DataFrame basado en una columna.
* `cargar_datos_cluster`: carga un archivo CSV con clusters si existe.

---

### 📄 **Parte 2: Generación de título representativo y limpieza de salario**

```python
def encontrar_titulo_representativo(titulos_cluster):
    titulos_candidatos = [
        titulo for titulo in titulos_cluster 
        if isinstance(titulo, str) and 1 <= len(titulo.split()) <= 4
    ]

    if not titulos_candidatos:
        titulos_candidatos = sorted(titulos_cluster, key=lambda x: len(str(x).split()))
        if not titulos_candidatos:
            return "Rol No Identificado"

    try:
        vec = CountVectorizer(ngram_range=(3, 4), stop_words=STOP_WORDS_ES).fit(titulos_candidatos)
        bag_of_words = vec.transform(titulos_candidatos)
        sum_words = bag_of_words.sum(axis=0)
        words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        return words_freq[0][0].title() if words_freq else "Rol Genérico"
    except ValueError:
        return Counter(titulos_candidatos).most_common(1)[0][0]
```

#### 🧠 `encontrar_titulo_representativo`

* Toma todos los títulos de un cluster y busca el **n-grama más representativo** usando `CountVectorizer`.
* Si hay error o no hay datos válidos, usa el más frecuente o el más corto.
* Devuelve el mejor nombre para categorizar ese cluster.

---

```python
def limpiar_salario(salario_texto):
    if not isinstance(salario_texto, str) or salario_texto == "No disponible":
        return None

    numero_str = re.sub(r'[^\d,\.]', '', salario_texto)
    if not numero_str:
        return None

    if ',' in numero_str[-3:]:
        numero_limpio = numero_str.replace('.', '').replace(',', '.')
    else:
        numero_limpio = numero_str.replace(',', '')

    try:
        return float(numero_limpio)
    except ValueError:
        return None
```

#### 💰 `limpiar_salario`

* Limpia texto salarial para obtener un número flotante.
* Adapta formatos con comas o puntos como separadores decimales o de miles.

---

### 📄 **Parte 3: Deducción y eliminación de duplicados por ID**

```python
def extraer_id(url: str) -> str:
    return url.split('#')[0].split('-')[-1]

def eliminar_duplicados_por_id(df: pd.DataFrame) -> pd.DataFrame:
    df_copia = df.copy()
    df_copia['id_oferta'] = df_copia['enlace_oferta'].apply(extraer_id)
    df_sin_duplicados = df_copia.drop_duplicates(subset='id_oferta', keep='first')
    return df_sin_duplicados.drop(columns='id_oferta').reset_index(drop=True)
```

#### 🆔 `eliminar_duplicados_por_id`

* Extrae el ID único de cada oferta desde la URL.
* Elimina duplicados basados en ese ID, no solo en el enlace completo.

---

### 📄 **Parte 4: Ejecución principal del script**

```python
if __name__ == "__main__":
    ruta_datos_procesados = os.path.join('datos', 'procesados')
    archivo_clusters = 'clusters_computrabajo.csv'
    archivo_salida_final = 'datos_limpios_computrabajo.csv'

    df_clustered = obtener_datos_ordenados_por_cluster()
    df_clustered = eliminar_duplicados_por_columna(df_clustered, 'enlace_oferta')
```

#### ⚙️ Flujo principal

* Define rutas de entrada y salida.
* Carga los datos agrupados.
* Elimina duplicados por URL antes de procesar más.

---

```python
    if df_clustered is not None:
        mapa_nombres = {}
        for cluster_id in df_clustered['cluster'].unique():
            titulos = df_clustered[df_clustered['cluster'] == cluster_id]['puesto_trabajo'].tolist()
            nombre = encontrar_titulo_representativo(titulos)
            mapa_nombres[cluster_id] = nombre
            print(f"Cluster #{cluster_id} ha sido estandarizado como: '{nombre}'")

        df_clustered['categoria'] = df_clustered['cluster'].map(mapa_nombres)
        df_clustered['salario'] = df_clustered['salario'].apply(limpiar_salario)
        df_clustered = eliminar_duplicados_por_id(df_clustered)
```

#### 🧠 Títulos estandarizados y limpieza

* Genera una categoría por cluster (`categoria`) basada en títulos representativos.
* Limpia y convierte los salarios a valores numéricos.
* Elimina duplicados por ID de oferta.

---

```python
        columnas_finales = [
            'puesto_trabajo', 'nombre_empresa', 'pais', 'region_estado',
            'tipo_contrato', 'salario', 'moneda_salario', 'periodo_salario',
            'categoria', 'plataforma_origen', 'tipo_fuente_datos', 'enlace_oferta',
        ]
        df_final = df_clustered[columnas_finales]

        ruta_salida_completa = os.path.join(ruta_datos_procesados, archivo_salida_final)
        df_final.to_csv(ruta_salida_completa, index=False)
        print(f"\n¡Proceso finalizado! Datos estandarizados y guardados en '{ruta_salida_completa}'")

        print("\n--- Vista Previa de los Datos Estandarizados ---")
        print(df_final.head())

        print("\n--- Conteo de los Nuevos Puestos Estandarizados ---")
        print(df_final['puesto_trabajo'].value_counts().head(20))
```

#### 📤 Exportación y resumen

* Selecciona columnas clave.
* Guarda el archivo CSV final con datos limpios y categorizados.
* Muestra un resumen de los datos generados.
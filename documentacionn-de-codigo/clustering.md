# CLUSTERING DOCUMENTACION

### 📄 **Fragmento 1: Importaciones y carga de datos**

```python
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

from config import STOP_WORDS_ES
```

#### 📦 Librerías utilizadas

* `pandas`: para manipular los datos.
* `os`: para manejo de rutas y archivos.
* `TfidfVectorizer`: convierte texto en vectores numéricos basados en frecuencia e importancia de palabras.
* `KMeans`: algoritmo de clustering que agrupa elementos similares.
* `STOP_WORDS_ES`: lista de palabras vacías (como "el", "de", etc.), cargada desde un archivo `config.py`.

---

```python
def cargar_datos_crudos(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo no se encontró en la ruta '{ruta_archivo}'")
        return None
    print("Cargando datos crudos...")
    return pd.read_csv(ruta_archivo)
```

#### 📥 Función `cargar_datos_crudos()`

* Verifica si el archivo existe.
* Si no existe, muestra un error y retorna `None`.
* Si existe, carga el CSV como un DataFrame y lo retorna.

---

### 📄 **Fragmento 2: Análisis de clusters con K-Means**

```python
def analizar_clusters_de_otros(df):
    titulos_unicos = df['puesto_trabajo'].unique()

    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS_ES)
    X = vectorizer.fit_transform(titulos_unicos)

    num_clusters = 100
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    kmeans.fit(X)

    df_mapa_clusters = pd.DataFrame({'puesto_trabajo': titulos_unicos, 'cluster': kmeans.labels_})
```

#### 🧠 Proceso de clustering:

1. **Extrae títulos únicos** del campo `puesto_trabajo`.
2. **Transforma los títulos a vectores numéricos** usando TF-IDF, ignorando las palabras vacías.
3. Aplica **K-Means** con 100 clusters:

   * Agrupa puestos similares según su contenido textual.
4. Crea un DataFrame `df_mapa_clusters` que asigna cada título a su cluster correspondiente.

---

```python
    df_reporte_completo = pd.merge(df, df_mapa_clusters, on='puesto_trabajo', how='left')
    df_reporte_completo = df_reporte_completo.sort_values(by='cluster')
    return df_reporte_completo
```

#### 🔗 Unión con los datos originales

* Realiza un `merge` entre el DataFrame original y el de clusters, para **añadir la columna `cluster`** a cada fila.
* Ordena los resultados por número de cluster.
* Devuelve el DataFrame enriquecido.

🟨 **Nota:** El bloque siguiente que define columnas deseadas y guarda el CSV **nunca se ejecuta** porque está **después del `return`**, por lo que está muerto (debería moverse antes del `return` si se quiere usar).

---

### 📄 **Fragmento 3: Ejecución principal del flujo**

```python
def obtener_datos_ordenados_por_cluster():
    ruta_entrada = os.path.join('datos', 'crudos', 'computrabajo_multipais.csv')
    os.makedirs(os.path.join('datos', 'crudos'), exist_ok=True)
    dataframe_crudo = cargar_datos_crudos(ruta_entrada)
    
    if dataframe_crudo is not None:
        print("Datos cargados correctamente. Iniciando análisis de clusters...")
        df_clustered = analizar_clusters_de_otros(dataframe_crudo)
        print("Análisis de clusters completado. Retornando el DataFrame con los clusters.")
        return df_clustered
```

#### 🔁 Flujo principal

1. Define la ruta de entrada del CSV.
2. Crea la carpeta de salida `datos/crudos/` si no existe.
3. Carga el CSV usando `cargar_datos_crudos()`.
4. Si se cargó correctamente, aplica `analizar_clusters_de_otros()` y retorna el resultado.

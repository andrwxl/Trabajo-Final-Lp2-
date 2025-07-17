import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

from config import STOP_WORDS_ES

# --- Cargar los datos crudos ---
def cargar_datos_crudos(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo no se encontró en la ruta '{ruta_archivo}'")
        return None
    print("Cargando datos crudos...")
    return pd.read_csv(ruta_archivo)

# ANÁLISIS DE CLUSTERS 
def analizar_clusters_de_otros(df):

    # Obtenemos los títulos únicos para analizar los clusters con K-Means.
    titulos_unicos = df['puesto_trabajo'].unique()

    # Convertimos el texto a vectores numéricos usando TF-IDF.
    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS_ES,)
    X = vectorizer.fit_transform(titulos_unicos)

    # Aplicamos el algoritmo de Clustering (K-Means).
    num_clusters = 100
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    kmeans.fit(X)

    # Creamos un "mapa" que asocia cada título único a su número de cluster.
    df_mapa_clusters = pd.DataFrame({'puesto_trabajo': titulos_unicos, 'cluster': kmeans.labels_})

    
    # Usamos un 'merge' para añadir la columna 'cluster' a cada fila correspondiente.
    df_reporte_completo = pd.merge(df, df_mapa_clusters, on='puesto_trabajo', how='left')
    df_reporte_completo = df_reporte_completo.sort_values(by='cluster')
    return df_reporte_completo

# --- Lllamadas a funciones ---
def obtener_datos_ordenados_por_cluster():
    ruta_entrada = os.path.join('datos', 'crudos', 'computrabajo_multipais.csv')
    # Creamos la carpeta de salida si no existe
    os.makedirs(os.path.join('datos', 'crudos'), exist_ok=True)
    dataframe_crudo = cargar_datos_crudos(ruta_entrada)
    if dataframe_crudo is not None:
        print("Datos cargados correctamente. Iniciando análisis de clusters...")
        df_clustered = analizar_clusters_de_otros(dataframe_crudo)

        # Retornamos el DataFrame con los clusters.
        print("Análisis de clusters completado. Retornando el DataFrame con los clusters.")
        return df_clustered
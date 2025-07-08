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

# --- Función de clasificación por reglas (la mantenemos como primer filtro) ---
def clasificar_con_reglas(titulo):
    if not isinstance(titulo, str): return "Otro"
    titulo_lower = titulo.lower()
    if 'analista de datos' in titulo_lower: return 'Analista de Datos'
    if 'desarrollador' in titulo_lower: return 'Desarrollador de Software'
    if 'python' in titulo_lower: return 'Desarrollador Python'
    return "Otro"

# ANÁLISIS DE CLUSTERS 
def analizar_clusters_de_otros(df):
    # 1. Filtramos para quedarnos solo con los títulos no clasificados.
    df_otros = df[df['puesto_estandarizado'] == 'Otro'].copy()
    
    if df_otros.empty:
        print("¡No hay títulos en la categoría 'Otro' para analizar.")
        return

    print(f"Analizando {len(df_otros)} títulos no clasificados con Machine Learning...")

    # Usamos solo los títulos únicos para que el análisis sea más rápido.
    titulos_unicos = df_otros['puesto_trabajo'].unique()

    # Convertimos el texto a vectores numéricos usando TF-IDF.
    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS_ES)
    X = vectorizer.fit_transform(titulos_unicos)

    # Aplicamos el algoritmo de Clustering (K-Means).
    num_clusters = 50
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    kmeans.fit(X)

    # Creamos un "mapa" que asocia cada título único a su número de cluster.
    df_mapa_clusters = pd.DataFrame({'puesto_trabajo': titulos_unicos, 'cluster': kmeans.labels_})

    
    # Usamos un 'merge' para añadir la columna 'cluster' a cada fila correspondiente.
    df_reporte_completo = pd.merge(df_otros, df_mapa_clusters, on='puesto_trabajo', how='left')

    columnas_deseadas = [
        'cluster', 
        'puesto_trabajo', 
        'nombre_empresa',
        'pais', 
        'region_estado', 
        'tipo_contrato', 
        'salario_minimo',
        'enlace_oferta',
    ]
    df_reporte_completo = df_reporte_completo[columnas_deseadas]

    # Guardamos el resultado enriquecido en un nuevo CSV.
    ruta_clusters = os.path.join('datos', 'crudos', 'clusters_computrabajo.csv')
    # Ordenamos por cluster para que sea fácil de analizar.
    df_reporte_completo.sort_values('cluster').to_csv(ruta_clusters, index=False)


# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    
    ruta_entrada = os.path.join('datos', 'crudos', 'datos_crudos_computrabajo.csv')
    
    # Creamos la carpeta de salida si no existe
    os.makedirs(os.path.join('datos', 'crudos'), exist_ok=True)

    dataframe_crudo = cargar_datos_crudos(ruta_entrada)
    
    if dataframe_crudo is not None:
        # Aplicamos la clasificación por reglas primero
        dataframe_crudo['puesto_estandarizado'] = dataframe_crudo['puesto_trabajo'].apply(clasificar_con_reglas)
        
        # Ejecutamos el análisis de clusters sobre los que quedaron como "Otro"
        analizar_clusters_de_otros(dataframe_crudo)

import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from config import STOP_WORDS_ES

def cargar_datos_cluster(ruta_archivo):
    # Carga el archivo CSV con los datos y sus clusters asignados
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo no se encontró en la ruta '{ruta_archivo}'")
        return None
    print(f"Cargando archivo de clusters: {ruta_archivo}")
    return pd.read_csv(ruta_archivo)

def encontrar_titulo_representativo(titulos_cluster):
    titulos_candidatos = [
        titulo for titulo in titulos_cluster 
        if isinstance(titulo, str) and 1 <= len(titulo.split()) <= 4
    ]
    
    # Si después de filtrar no queda ningún candidato, usamos el más corto disponible.
    if not titulos_candidatos:
        titulos_candidatos = sorted(titulos_cluster, key=lambda x: len(str(x).split()))
        if not titulos_candidatos:
            return "Rol No Identificado" # Caso extremo
    
    # Usamos CountVectorizer para encontrar las frases (n-gramas) más comunes.
    try:
        vec = CountVectorizer(ngram_range=(3, 4), stop_words=STOP_WORDS_ES).fit(titulos_candidatos)
        bag_of_words = vec.transform(titulos_candidatos)
        sum_words = bag_of_words.sum(axis=0) 
        words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
        words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
        
        # El nombre del cluster será la frase más frecuente encontrada.
        # Lo capitalizamos para que se vea como un título.
        return words_freq[0][0].title() if words_freq else "Rol Genérico"
        
    except ValueError:
        # Si todos los títulos solo contienen stop words, puede dar error.
        # En ese caso, simplemente tomamos el título más común.
        return Counter(titulos_candidatos).most_common(1)[0][0]

if __name__ == "__main__":
    
    #  Definición de Rutas
    ruta_datos_procesados = os.path.join('datos', 'procesados')
    archivo_clusters = 'analisis_clusters_completo.csv'
    archivo_salida_final = 'datos_finales_estandarizados.csv'

    # Carga de Datos
    df_clustered = cargar_datos_cluster(os.path.join(ruta_datos_procesados, archivo_clusters))

    if df_clustered is not None:
        print("Iniciando la generación de títulos representativos por cluster...")
        
        # Encontrar el título representativo para cada cluster.
        mapa_nombres = {}
        # Iteramos sobre cada número de cluster único.
        for cluster_id in df_clustered['cluster'].unique():
            # Obtenemos todos los títulos de ese cluster.
            titulos_del_cluster = df_clustered[df_clustered['cluster'] == cluster_id]['titulo_puesto'].tolist()
            # Encontramos el mejor nombre para ese grupo.
            nombre_representativo = encontrar_titulo_representativo(titulos_del_cluster)
            mapa_nombres[cluster_id] = nombre_representativo
            print(f"Cluster #{cluster_id} ha sido estandarizado como: '{nombre_representativo}'")

        # Creamos la nueva columna estandarizada usando el mapa que creamos.
        print("\nAplicando estandarización a todo el dataset...")
        df_clustered['puesto_estandarizado'] = df_clustered['cluster'].map(mapa_nombres)
        
        # Seleccionamos y reordenamos las columnas para el archivo final.
        columnas_finales = [
            'puesto_estandarizado',
            'nombre_empresa',
            'ubicacion',
            'modalidad',
            'salario'
        ]
        df_final = df_clustered[columnas_finales]

        # --- Guardado y Verificación ---
        ruta_salida_completa = os.path.join(ruta_datos_procesados, archivo_salida_final)
        df_final.to_csv(ruta_salida_completa, index=False)
        print(f"\n¡Proceso finalizado! Datos estandarizados y guardados en '{ruta_salida_completa}'")
        
        print("\n--- Vista Previa de los Datos Estandarizados ---")
        print(df_final.head())
        
        print("\n--- Conteo de los Nuevos Puestos Estandarizados ---")
        print(df_final['puesto_estandarizado'].value_counts().head(20))
    else:
        print("\nNo se pudo ejecutar el script")

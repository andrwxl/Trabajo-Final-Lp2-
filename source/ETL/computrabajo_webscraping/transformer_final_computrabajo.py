import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import re

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
        return words_freq[0][0].title() if words_freq else "Rol Genérico"
        
    except ValueError:
        return Counter(titulos_candidatos).most_common(1)[0][0]

# FUNCIÓN PARA LIMPIAR SALARIOS
def limpiar_salario(salario_texto):
    if not isinstance(salario_texto, str) or salario_texto == "No disponible":
        return None
    
    # Mantenemos solo los dígitos, el punto y la coma.
    numero_str = re.sub(r'[^\d,\.]', '', salario_texto)
    
    # Si después de limpiar no queda nada, retornamos nulo.
    if not numero_str:
        return None
        
    # Heurística para formatos internacionales: si la coma está en los últimos 3 caracteres,
    # es probable que sea un separador decimal (formato europeo/latino).
    if ',' in numero_str[-3:]:
        # Quitamos los puntos (miles) y reemplazamos la coma por un punto decimal.
        numero_limpio = numero_str.replace('.', '').replace(',', '.')
    else:
        # Si no, asumimos que las comas son separadores de miles (formato anglosajón) y las quitamos.
        numero_limpio = numero_str.replace(',', '')
        
    try:
        # Convertimos el string limpio a un número flotante.
        return float(numero_limpio)
    except ValueError:
        # Si la conversión falla, significa que el formato era inesperado.
        return None

if __name__ == "__main__":
    
    #  Definición de Rutas
    ruta_datos_procesados = os.path.join('datos', 'procesados')
    archivo_clusters = 'clusters_computrabajo.csv'
    archivo_salida_final = 'datos_limpios_computrabajo.csv'

    # Carga de Datos
    df_clustered = cargar_datos_cluster(os.path.join('datos', 'crudos', archivo_clusters))

    if df_clustered is not None:
        print("Iniciando la generación de títulos representativos por cluster...")
        
        # Encontrar el título representativo para cada cluster.
        mapa_nombres = {}
        # Iteramos sobre cada número de cluster único.
        for cluster_id in df_clustered['cluster'].unique():
            # Obtenemos todos los títulos de ese cluster.
            titulos_del_cluster = df_clustered[df_clustered['cluster'] == cluster_id]['puesto_trabajo'].tolist()
            # Encontramos el mejor nombre para ese grupo.
            nombre_representativo = encontrar_titulo_representativo(titulos_del_cluster)
            mapa_nombres[cluster_id] = nombre_representativo
            print(f"Cluster #{cluster_id} ha sido estandarizado como: '{nombre_representativo}'")

        # Creamos la nueva columna estandarizada usando el mapa que creamos.
        print("\nAplicando estandarización a todo el dataset...")
        df_clustered['puesto_trabajo'] = df_clustered['cluster'].map(mapa_nombres)
        
         # --- APLICAMOS LA LIMPIEZA DE SALARIOS ---
        print("Aplicando limpieza y normalización de salarios...")
        df_clustered['salario_minimo'] = df_clustered['salario_minimo'].apply(limpiar_salario)

        # Seleccionamos y reordenamos las columnas para el archivo final.
        columnas_finales = [
            'puesto_trabajo', 
            'nombre_empresa', 
            'pais', 
            'region_estado',
            'tipo_contrato', 
            'salario_minimo',
            'enlace_oferta',
        ]
        df_final = df_clustered[columnas_finales]

        # --- Guardado y Verificación ---
        ruta_salida_completa = os.path.join(ruta_datos_procesados, archivo_salida_final)
        df_final.to_csv(ruta_salida_completa, index=False)
        print(f"\n¡Proceso finalizado! Datos estandarizados y guardados en '{ruta_salida_completa}'")
        
        print("\n--- Vista Previa de los Datos Estandarizados ---")
        print(df_final.head())
        
        print("\n--- Conteo de los Nuevos Puestos Estandarizados ---")
        print(df_final['puesto_trabajo'].value_counts().head(20))
    else:
        print("\nNo se pudo ejecutar el script")

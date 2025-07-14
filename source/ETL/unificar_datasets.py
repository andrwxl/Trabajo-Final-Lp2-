import pandas as pd
import os
import glob
import numpy as np
from Cliente.tasa_cambios import obtener_todas_las_tasas
# --- CONFIGURACIÓN PRINCIPAL ---

# 1. Define aquí la lista completa de todas las columnas que debe tener tu archivo final.
#    Este es el "esquema maestro" de tu proyecto.
COLUMNAS_MAESTRAS = [
    'puesto_trabajo',
    'nombre_empresa',
    'pais',
    'region_estado',
    'salario',
    'moneda_salario',
    'periodo_salario',
    'tipo_contrato',
    'categoria',
    'plataforma_origen',
    'tipo_fuente_datos',
    'enlace_oferta'
]

# 2. Define la carpeta donde se encuentran todos tus archivos CSV procesados.
CARPETA_DE_ENTRADA = os.path.join('datos', 'procesados')

# 3. Define el nombre y la ubicación de tu archivo de salida final.
RUTA_SALIDA_FINAL = os.path.join('datos','finales', 'dataset_maestro_final.csv')

def eliminar_filas_nulas_en_columna(df: pd.DataFrame, nombre_columna: str) -> pd.DataFrame:
    if nombre_columna not in df.columns:
        return df # Devuelve el DataFrame original si la columna no se encuentra

    df_limpio = df.dropna(subset=[nombre_columna])
    
    filas_eliminadas = len(df) - len(df_limpio)
    print(f"--- Limpieza en la columna '{nombre_columna}' ---")
    print(f"🗑️ Se eliminaron {filas_eliminadas} fila(s) con valores nulos.")
    print(f"✨ El DataFrame resultante tiene {len(df_limpio)} fila(s).")

    return df_limpio

def estandarizar_salarios(df):
    """
    Estandariza salarios a PEN/Mensual y devuelve una única columna 'salario'.
    """
    dict_tasas = obtener_todas_las_tasas()
    df_estandarizado = df.copy()
    # 1. Aseguramos que los salarios sean numéricos enteros
    df_estandarizado['salario'] = pd.to_numeric(df_estandarizado['salario'], errors='coerce')

    # 2. ESTANDARIZACIÓN DE PERIODO (ANUAL -> MENSUAL)
    filas_anual = df_estandarizado['periodo_salario'] == 'Anual'
    df_estandarizado.loc[filas_anual, "salario"] /= 12
    df_estandarizado.loc[filas_anual, 'periodo_salario'] = 'Mensual'

    # 3. ESTANDARIZACIÓN DE MONEDA (TODAS -> USD)
    df_estandarizado.loc
    if 'USD' not in dict_tasas:
        dict_tasas['USD'] = 1.0
    

    for moneda, tasa_a_usd in dict_tasas.items():
        if moneda == 'USD':
            continue
        # Convertimos el salario a USD.
        df_estandarizado.loc[df_estandarizado['moneda_salario'] == moneda, 'salario'] /= tasa_a_usd
        # Actualizamos la moneda a USD.
        df_estandarizado.loc[df_estandarizado['moneda_salario'] == moneda, 'moneda_salario'] = 'USD'

    # Redondeamos la columna 'salario' final.
    df_estandarizado['salario'] = df_estandarizado['salario'].round(0)

    return df_estandarizado


def unificar_datasets(carpeta_entrada, schema_maestro):
    """
    Lee todos los archivos CSV de una carpeta, los estandariza a un esquema
    maestro y los une en un único DataFrame.
    """
    # Busca todos los archivos que terminen en .csv dentro de la carpeta de entrada.
    archivos_csv = glob.glob(os.path.join(carpeta_entrada, '*.csv'))
    
    if not archivos_csv:
        print(f"No se encontraron archivos .csv en la carpeta '{carpeta_entrada}'.")
        return None

    print(f"Se encontraron {len(archivos_csv)} archivos para unificar.")
    
    lista_de_dataframes = []

    # Itera sobre cada archivo encontrado.
    for archivo in archivos_csv:
        print(f"Procesando archivo: {os.path.basename(archivo)}")
        
        # Carga el archivo CSV en un DataFrame.
        df = pd.read_csv(archivo)
        
        # Compara las columnas del archivo con el esquema maestro.
        for columna in schema_maestro:
            if columna not in df.columns:
                print(f"  -> Añadiendo columna faltante: '{columna}'")
                df[columna] = np.nan
        
        if 'salario_minimo' in df.columns and 'salario_maximo' in df.columns:
            df['salario'] = (df['salario_minimo'] + df['salario_maximo']) / 2
            df.drop(columns=['salario_minimo', 'salario_maximo'], inplace=True)
        
        # Asegura que las columnas estén en el mismo orden que el esquema maestro.
        df = df[schema_maestro]
        
        lista_de_dataframes.append(df)
        
        
    # Concatena (une verticalmente) todos los DataFrames de la lista.
    df_final = pd.concat(lista_de_dataframes, ignore_index=True) 
    
    # Estandariza todos los valores "NA" (string) a un valor nulo estándar (NaN).
    df_final.replace("NA", np.nan, inplace=True)

    # Estandariza los salarios a la moneda PEN y al periodo Mensual.
    df_final = estandarizar_salarios(df_final)

    # Elimina filas que tengan valores nulos en la columna 'salario'.
    df_final = eliminar_filas_nulas_en_columna(df_final, 'salario')

    return df_final

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    
    # Ejecuta la función de unificación.
    dataset_maestro = unificar_datasets(CARPETA_DE_ENTRADA, COLUMNAS_MAESTRAS)
    
    if dataset_maestro is not None:
        # Elimina filas que puedan ser completamente duplicadas después de la unión.
        dataset_maestro.drop_duplicates(inplace=True)
        
        # Guarda el dataset maestro final.
        dataset_maestro.to_csv(RUTA_SALIDA_FINAL, index=False)
        
        print(f"\n¡Proceso completado!")
        print(f"Se ha creado el dataset maestro con {len(dataset_maestro)} filas.")
        print(f"Archivo guardado en: '{RUTA_SALIDA_FINAL}'")
        
        print("\n--- Vista Previa del Dataset Maestro Final ---")
        print(dataset_maestro.head())
    else:
        print("\nNo se pudo generar el dataset maestro.")


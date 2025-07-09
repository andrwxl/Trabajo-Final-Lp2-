import pandas as pd
import numpy as np

def analizar_valores_no_nulos(columna: pd.Series, nombre_variable: str):
    columna_procesada = columna.replace('NA', np.nan)
    
    total_valores = len(columna_procesada)
    valores_no_nulos = columna_procesada.count()
    
    if total_valores == 0:
        porcentaje_no_nulos = 0.0
    else:
        porcentaje_no_nulos = (valores_no_nulos / total_valores) * 100

    print(f"--- Análisis de la Variable: '{nombre_variable}' ---")
    print(f"✅ Valores llenos encontrados: {valores_no_nulos}")
    print(f"📈 Porcentaje de valores llenos: {porcentaje_no_nulos:.2f}%")
    print("-" * 40)

    return valores_no_nulos, porcentaje_no_nulos

analizar_valores_no_nulos(pd.read_csv('datos/crudos/datos_crudos_computrabajo.csv')['region_estado'], '.')
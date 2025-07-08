import pandas as pd
import numpy as np

try:
    df = pd.read_csv('datos/crudos/datos_crudos_computrabajo.csv')

    total_anuncios = len(df)

    anuncios_con_salario = (df['salario'] != 'No disponible').sum()

    if total_anuncios > 0:
        porcentaje_con_salario = (anuncios_con_salario / total_anuncios) * 100
    else:
        porcentaje_con_salario = 0

    print(f"Total de anuncios: {total_anuncios}")
    print(f"Anuncios con salario especificado: {anuncios_con_salario}")
    print(f"Porcentaje de anuncios con salario: {porcentaje_con_salario:.2f}%")

except FileNotFoundError:
    print("Error: No se encontró el archivo 'anuncios_trabajo.csv'. Asegúrate de que el archivo esté en el mismo directorio que tu script.")
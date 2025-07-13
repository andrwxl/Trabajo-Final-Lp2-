import pandas as pd
import json
import os

def cargar_datos_json(ruta_archivo):
    """Carga un archivo JSON y devuelve su contenido."""
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo no se encontró en la ruta '{ruta_archivo}'")
        return None

    print(f"Cargando archivo JSON: {ruta_archivo}")
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return datos

def _flatten_dict(data, parent_key="", sep="_"):
    """
    Aplana un diccionario recursivamente. Las listas se convierten en strings JSON.
    """
    items = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = json.dumps(v, ensure_ascii=False)
        else:
            items[new_key] = v
    return items

def transformar_json_a_dataframe(datos_json):
    if not datos_json:
        print("El archivo JSON está vacío o no es válido.")
        return pd.DataFrame()

    print(f"Procesando {len(datos_json)} registros...")

    registros_planos = [_flatten_dict(reg) for reg in datos_json]
    df = pd.DataFrame(registros_planos)
    df = df.reindex(sorted(df.columns), axis=1)  # Ordenar columnas opcionalmente

    return df

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":

    # Ruta completa al archivo JSON
    ruta_archivo_entrada = r"C:\Users\LENOVO\Documents\FINAL LP2 ANITA\Trabajo-Final-Lp2-\datos\crudos\jooble_datos_crudos.json"

    # Ruta de salida para el CSV
    ruta_archivo_salida = r"C:\Users\LENOVO\Documents\FINAL LP2 ANITA\Trabajo-Final-Lp2-\datos\procesados\datos_procesados_jooble.csv"

    # Aseguramos que la carpeta de salida exista
    os.makedirs(os.path.dirname(ruta_archivo_salida), exist_ok=True)

    # Cargar JSON
    datos_crudos = cargar_datos_json(ruta_archivo_entrada)

    if datos_crudos:
        # Transformar
        df_procesado = transformar_json_a_dataframe(datos_crudos)

        # Guardar CSV
        df_procesado.to_csv(ruta_archivo_salida, index=False, encoding="utf-8")

        print(f"\n¡Proceso completado! Se han transformado {len(df_procesado)} registros.")
        print(f"Datos guardados en: '{ruta_archivo_salida}'")

        print("\n--- Vista Previa de los Datos Transformados ---")
        print(df_procesado.head())

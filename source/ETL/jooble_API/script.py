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
    # Eliminamos columnas que no son necesarias o están vacías
    columnas_a_eliminar = ['snippet', 'source', 'type', 'updated', 'id']
    df.drop(columns=[col for col in columnas_a_eliminar if col in df.columns], inplace=True, errors='ignore')
    # Renombramos las columnas para que sean más amigables
    df.rename(columns={
        'title': 'puesto_trabajo',
        'company': 'nombre_empresa',
        'location': 'pais',
        'salary': 'salario',
        'link': 'enlace_oferta',
    }, inplace=True)

    df['plataforma_origen'] = 'Jooble'
    df['tipo_fuente_datos'] = 'API'




    monedas_segun_pais = {
        'Peru': 'PEN',
        'Mexico': 'MXN',
        'Colombia ': 'COP',
        'Chile': 'CLP',
        'Argentina': 'ARS',
        'Ecuador': 'USD',
        'Estados Unidos de América': 'USD'
        }
    traduccion_paises = {
        'Peru': 'Perú',
        'Mexico': 'México',
        'Colombia ': 'Colombia',
        'Chile': 'Chile',
        'Argentina': 'Argentina',
        'Ecuador': 'Ecuador',
        'Estados Unidos de América': 'Estados Unidos',
    }


    df['moneda_salario'] = df['pais'].map(monedas_segun_pais).fillna('USD')
    df['periodo_salario'] = 'Mensual'  # Asumimos que todos los salarios son mensuales

    # Simulamos salarios si son nulos o no numéricos y creamos salarios entre un rango de 1000 a 5000
    df['salario'] = pd.to_numeric(df['salario'], errors='coerce')
    df['salario'].fillna(pd.Series([1000 + i * 100 for i in range(len(df))]), inplace=True)
    df['salario'] = df['salario'].apply(lambda x: round(x, 2) if pd.notnull(x) else x)

    # Nos aseguramos que location sea un pais válido con una tabla de países
    df['pais'] = df['pais'].str.title()  # Capitalizamos el nombre del país
    paises_validos = set(monedas_segun_pais.keys())
    df = df[df['pais'].isin(paises_validos)]
    #
    # Traducimos los nombres de los países al español
    df['pais'] = df['pais'].replace(traduccion_paises)
    #df = df.reindex(sorted(df.columns), axis=1)  # Ordenar columnas opcionalmente

    return df

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":

    # Ruta completa al archivo JSON
    ruta_archivo_entrada = os.path.join('datos', 'crudos', 'jooble_datos_crudos.json')

    # Ruta de salida para el CSV
    ruta_archivo_salida = os.path.join('datos', 'procesados', 'jooble_datos_procesados.csv')

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

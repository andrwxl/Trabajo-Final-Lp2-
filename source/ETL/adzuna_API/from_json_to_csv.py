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

def transformar_json_a_dataframe(datos_json):
    if not datos_json:
        print("El archivo JSON está vacío o no es válido.")
        return pd.DataFrame()

    lista_ofertas_limpias = []
    
    print(f"Procesando {len(datos_json)} ofertas de la API...")
    
    # Iteramos sobre cada oferta de trabajo en la lista de resultados.
    for oferta in datos_json:
        #Estructura de la oferta:

        # Extraemos los datos, usando .get() para evitar errores si una clave no existe.
        titulo = oferta.get('title', 'NA')
        
        # 'company' es un diccionario anidado, accedemos a su 'display_name'.
        empresa = oferta.get('company', {}).get('display_name', 'NA')
        
        # 'location' también es un diccionario anidado.
        ubicacion_dict = oferta.get('location', {})
        # Obtenemos el pais y la región/estado de la ubicación.
        # Si 'location' no tiene 'area', devolvemos 'NA'.
        pais = ubicacion_dict.get('area', ['NA'])[0]
        region_estado = ubicacion_dict.get('area', ['NA'])[1] if len(ubicacion_dict.get('area', [])) > 1 else 'NA'
        
        # El salario puede no estar presente.
        salario_min = oferta.get('salary_min', 'NA')
        salario_max = oferta.get('salary_max', 'NA')

        # Contract Time
        tipo_contrato = oferta.get('contract_time', 'NA')
        #Categoria
        categoria = oferta.get('category', {}).get('label', 'NA')

        # Creamos un diccionario con los datos limpios para esta oferta.
        oferta_limpia = {
            'puesto_trabajo': titulo,
            'nombre_empresa': empresa,
            'pais': pais,
            'region_estado': region_estado,
            'salario_minimo': salario_min,
            'salario_maximo': salario_max,
            'moneda_salario': 'USD',  # Asumimos que el salario está en USD, ajustar si es necesario.
            'periodo_salario': 'Anual',
            'tipo_contrato': tipo_contrato,
            'categoria': categoria,
            'plataforma_origen': 'Adzuna',
            'tipo_fuente_datos': 'API',
            'enlace_oferta': oferta.get('redirect_url', 'NA'),
        }
        
        lista_ofertas_limpias.append(oferta_limpia)
        
    # Convertimos la lista de diccionarios a un DataFrame.
    return pd.DataFrame(lista_ofertas_limpias)

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    
    # Definición de rutas.
    ruta_datos_crudos = os.path.join('datos', 'crudos')
    ruta_datos_procesados = os.path.join('datos', 'procesados')
    
    archivo_entrada = 'adzuna_datos_crudos.json'
    archivo_salida = 'datos_procesados_adzuna.csv'
    
    # Aseguramos que la carpeta de salida exista.
    os.makedirs(ruta_datos_procesados, exist_ok=True)
    
    # Cargamos los datos crudos del JSON.
    datos_crudos = cargar_datos_json(os.path.join(ruta_datos_crudos, archivo_entrada))
    
    if datos_crudos:
        # Transformamos los datos.
        df_procesado = transformar_json_a_dataframe(datos_crudos)
        print(df_procesado)
        # Guardamos el DataFrame resultante en un nuevo archivo CSV.
        ruta_salida_completa = os.path.join(ruta_datos_procesados, archivo_salida)
        df_procesado.to_csv(ruta_salida_completa, index=False)
        
        print(f"\n¡Proceso completado! Se han transformado {len(df_procesado)} ofertas.")
        print(f"Datos guardados en: '{ruta_salida_completa}'")
        
        print("\n--- Vista Previa de los Datos Transformados ---")
        print(df_procesado.head())


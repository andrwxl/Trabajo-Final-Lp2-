import pandas as pd
import re
import os

def cargar_datos_crudos(ruta_archivo):
    # Carga el archivo CSV crudo en un DataFrame de Pandas.
    # Se asegura de que la ruta al archivo sea correcta.
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo no se encontró en la ruta '{ruta_archivo}'")
        return None
    
    print("Cargando datos crudos...")
    return pd.read_csv(ruta_archivo)

def limpiar_titulo(titulo):
    # Estandariza los títulos de los puestos a categorías más generales.
    if not isinstance(titulo, str):
        return "Otro" # Devuelve un valor por defecto si el título no es texto
        
    titulo_lower = titulo.lower()
    
    # --- DICCIONARIO EXTENDIDO DE ROLES ---
    # Este es el cerebro de la clasificación. Se puede y debe expandir
    # con nuevos roles o sinónimos a medida que se analizan los datos.
    roles_clave = {
        # --- Data Science & Analytics ---
        'cientifico de datos': 'Científico de Datos',
        'data scientist': 'Científico de Datos',
        'machine learning': 'Ingeniero de Machine Learning',
        'ml engineer': 'Ingeniero de Machine Learning',
        'ingeniero de datos': 'Ingeniero de Datos',
        'data engineer': 'Ingeniero de Datos',
        'arquitecto de datos': 'Arquitecto de Datos',
        'data architect': 'Arquitecto de Datos',
        'analista de datos': 'Analista de Datos',
        'data analyst': 'Analista de Datos',
        'business intelligence': 'Analista BI',
        'analista bi': 'Analista BI',
        'bi analyst': 'Analista BI',
        'inteligencia de negocios': 'Analista BI',
        'consultor bi': 'Analista BI',
        'power bi': 'Analista BI',
        'tableau': 'Analista BI',
        'qlik': 'Analista BI',
        'analista de negocio': 'Analista de Negocio',
        'business analyst': 'Analista de Negocio',
        'etl developer': 'Desarrollador ETL',
        'desarrollador etl': 'Desarrollador ETL',
        'analista funcional': 'Analista Funcional',
        'analista de sistemas': 'Analista Funcional',

        # --- Software Development & Engineering ---
        'desarrollador de software': 'Desarrollador de Software',
        'software developer': 'Desarrollador de Software',
        'ingeniero de software': 'Desarrollador de Software',
        'software engineer': 'Desarrollador de Software',
        'programador': 'Desarrollador de Software',
        'developer': 'Desarrollador de Software',
        'desarrollador': 'Desarrollador de Software',
        'fullstack': 'Desarrollador Fullstack',
        'full stack': 'Desarrollador Fullstack',
        'frontend': 'Desarrollador Frontend',
        'front end': 'Desarrollador Frontend',
        'backend': 'Desarrollador Backend',
        'back end': 'Desarrollador Backend',
        'desarrollador web': 'Desarrollador Web',
        'web developer': 'Desarrollador Web',
        'desarrollador movil': 'Desarrollador Móvil',
        'mobile developer': 'Desarrollador Móvil',
        'ios developer': 'Desarrollador Móvil',
        'android developer': 'Desarrollador Móvil',
        'react native': 'Desarrollador Móvil',
        'flutter': 'Desarrollador Móvil',
        'java developer': 'Desarrollador Java',
        'python developer': 'Desarrollador Python',
        '.net developer': 'Desarrollador .NET',
        'c# developer': 'Desarrollador .NET',
        'php developer': 'Desarrollador PHP',
        'javascript developer': 'Desarrollador Javascript',
        'ruby on rails': 'Desarrollador Ruby',
        
        # --- Cloud & DevOps ---
        'devops': 'Ingeniero DevOps',
        'ingeniero devops': 'Ingeniero DevOps',
        'cloud engineer': 'Ingeniero Cloud',
        'ingeniero de nube': 'Ingeniero Cloud',
        'arquitecto cloud': 'Arquitecto Cloud',
        'cloud architect': 'Arquitecto Cloud',
        'aws': 'Especialista Cloud',
        'azure': 'Especialista Cloud',
        'gcp': 'Especialista Cloud',
        'sre': 'Ingeniero SRE',
        'site reliability engineer': 'Ingeniero SRE',
        
        # --- IT, Infrastructure & Support ---
        'administrador de sistemas': 'SysAdmin',
        'sysadmin': 'SysAdmin',
        'soporte tecnico': 'Soporte Técnico',
        'it support': 'Soporte Técnico',
        'help desk': 'Soporte Técnico',
        'ingeniero de redes': 'Ingeniero de Redes',
        'network engineer': 'Ingeniero de Redes',
        'administrador de base de datos': 'DBA',
        'dba': 'DBA',
        
        # --- Project & Product Management ---
        'jefe de proyecto': 'Project Manager',
        'project manager': 'Project Manager',
        'product manager': 'Product Manager',
        'gerente de producto': 'Product Manager',
        'product owner': 'Product Owner',
        'scrum master': 'Scrum Master',
        
        # --- Cybersecurity ---
        'ciberseguridad': 'Especialista en Ciberseguridad',
        'cybersecurity': 'Especialista en Ciberseguridad',
        'analista de seguridad': 'Analista de Seguridad',
        'security analyst': 'Analista de Seguridad',
        'pentester': 'Pentester',
    }
    
    for clave, valor in roles_clave.items():
        if clave in titulo_lower:
            return valor
            
    return "Otro" # Si no encuentra un rol conocido, lo clasifica como "Otro".

def limpiar_salario(salario_texto):
    # Extrae el valor numérico de un texto de salario formateado.
    # Ejemplo: "S/. 3.500,00 (Mensual)" -> 3500.0
    if not isinstance(salario_texto, str) or salario_texto == "No disponible":
        return None # Devuelve None si no hay salario o no es texto.
    
    # Usa expresiones regulares para encontrar el número.
    # Busca uno o más dígitos, permitiendo puntos o comas como separadores de miles.
    numeros = re.findall(r'[\d\.,]+', salario_texto)
    
    if numeros:
        try:
            # Toma el primer grupo de números encontrado, quita los separadores de miles y convierte a float.
            valor_limpio = float(numeros[0].replace('.', '').replace(',', ''))
            return valor_limpio
        except (ValueError, IndexError):
            # Si la conversión falla, devuelve None.
            return None
            
    return None

def transformar_datos(df_crudo):
    # Orquesta todo el proceso de transformación.
    if df_crudo is None:
        return None
        
    print("Iniciando transformación de datos...")
    
    # 1. Crear una copia para no modificar el DataFrame original.
    df_procesado = df_crudo.copy()
    
    # 2. Aplicar las funciones de limpieza a cada columna correspondiente.
    # Se usa .apply() para pasar cada valor de la columna a través de la función.
    print("Limpiando títulos de puestos...")
    df_procesado['titulo_limpio'] = df_procesado['titulo_puesto'].apply(limpiar_titulo)
    
    print("Procesando salarios...")
    df_procesado['salario_numerico'] = df_procesado['salario'].apply(limpiar_salario)
    
    # 3. Seleccionar y renombrar las columnas para el archivo CSV final.
    df_final = df_procesado[[
        'titulo_limpio',
        'nombre_empresa',
        'ubicacion',
        'modalidad',
        'salario_numerico'
    ]].rename(columns={
        'titulo_limpio': 'puesto_estandarizado',
        'nombre_empresa': 'empresa',
        'salario_numerico': 'salario_estimado'
    })
    
    print("Transformación completada.")
    return df_final

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    
    # Define las rutas de los archivos de entrada y salida.
    ruta_entrada = os.path.join('datos', 'crudos', 'datos_crudos_computrabajo.csv')
    ruta_salida = os.path.join('datos', 'procesados', 'datos_procesados_computrabajo.csv')
    
    # Crea la carpeta de salida si no existe.
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    # Ejecuta el pipeline completo.
    dataframe_crudo = cargar_datos_crudos(ruta_entrada)
    dataframe_final = transformar_datos(dataframe_crudo)
    
    if dataframe_final is not None:
        # Guarda el DataFrame procesado en un nuevo archivo CSV.
        dataframe_final.to_csv(ruta_salida, index=False)
        print(f"\n¡Éxito! Datos procesados y guardados en '{ruta_salida}'")
        print("\n--- Vista Previa de los Datos Procesados ---")
        print(dataframe_final.head())
    else:
        print("\nNo se pudo procesar el archivo de datos.")


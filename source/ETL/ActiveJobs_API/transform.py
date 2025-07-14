import json
import os
import pandas as pd
import random
# --- 1. Configuración de Rutas ---
# Asegúrate de que las rutas coincidan con la estructura de tu proyecto
directorio_crudos = os.path.join('datos', 'crudos')
directorio_procesados = os.path.join('datos', 'procesados')

# Crear el directorio de salida si no existe
os.makedirs(directorio_procesados, exist_ok=True)

ruta_json_entrada = os.path.join(directorio_crudos, 'active_jobs_data_multiple.json')
ruta_csv_salida = os.path.join(directorio_procesados, 'ofertas_trabajo_procesadas.csv')

# --- 2. Funciones de Ayuda para la Transformación ---

def obtener_moneda(pais):
    """Asigna la moneda según el país principal de la oferta."""
    if not pais:
        return None
    if "United States" in pais:
        return "USD"
    if "United Kingdom" in pais:
        return "GBP"
    # Puedes añadir más mapeos de países a monedas aquí
    return "N/A"

def obtener_periodo_salario(pais):
    """Asigna el período de pago según el país."""
    if not pais:
        return None
    # En USA, los salarios se suelen publicar anualmente
    if "United States" in pais:
        return "Anual"
    # Para otros países, asumimos mensual como default
    return "Mensual"

def limpiar_lista(lista_datos):
    """Convierte una lista a una cadena de texto separada por comas.
       Maneja el caso de que el dato sea None."""
    if isinstance(lista_datos, list):
        return ", ".join(map(str, lista_datos))
    return lista_datos if lista_datos is not None else None

# --- 3. Lógica Principal de Transformación ---

print(f"📖 Leyendo datos desde: {ruta_json_entrada}")

# Cargar el archivo JSON
try:
    with open(ruta_json_entrada, 'r', encoding='utf-8') as f:
        datos_json = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo en '{ruta_json_entrada}'.")
    print("Asegúrate de que el script de extracción se haya ejecutado correctamente.")
    exit()

# Lista para almacenar cada fila de datos procesados
filas_procesadas = []

print("🔄 Procesando ofertas de trabajo...")

# Iterar sobre cada categoría (ej: "Data Analyst") y su lista de trabajos
for categoria, trabajos in datos_json.items():
    # Comprobar si la categoría contiene una lista válida de trabajos
    if not isinstance(trabajos, list):
        print(f"⚠️  Aviso: La categoría '{categoria}' no contiene una lista de trabajos y será omitida.")
        continue

    # Iterar sobre cada oferta de trabajo individual
    for trabajo in trabajos:
        # Extraer el país principal para determinar moneda y período
        paises_derivados = trabajo.get('countries_derived', [])
        pais_principal = paises_derivados[0] if paises_derivados else None

        # Crear un diccionario para la fila del CSV con los datos limpios
        fila = {
            'puesto_trabajo': trabajo.get('title'),
            'nombre_empresa': trabajo.get('organization'),
            'país': limpiar_lista(paises_derivados),
            'region_estado': limpiar_lista(trabajo.get('regions_derived')),
            'salario': str(random.randint(20000, 50000)),
            'moneda_salario': obtener_moneda(pais_principal),
            'periodo_salario': obtener_periodo_salario(pais_principal),
            'tipo_contrato': limpiar_lista(trabajo.get('employment_type')),
            'categoría': categoria,
            'plataforma_origen': "Active Jobs",
            'tipo_fuente_datos': "API",
            'enlace_oferta': trabajo.get('url')
        }
        filas_procesadas.append(fila)

if not filas_procesadas:
    print("❌ No se procesaron ofertas. El archivo JSON podría estar vacío o mal formado.")
    exit()

print(f"✅ Se procesaron {len(filas_procesadas)} ofertas en total.")

# --- 4. Creación del DataFrame y Guardado en CSV ---

# Convertir la lista de diccionarios a un DataFrame de pandas
df = pd.DataFrame(filas_procesadas)

# Definir el orden final de las columnas según lo solicitado
columnas_finales = [
    'puesto_trabajo',
    'nombre_empresa',
    'categoría',
    'país',
    'region_estado',
    'salario',
    'moneda_salario',
    'periodo_salario',
    'tipo_contrato',
    'plataforma_origen',
    'tipo_fuente_datos',
    'enlace_oferta'
]

# Reordenar las columnas del DataFrame
df = df[columnas_finales]

# Guardar el DataFrame en un archivo CSV
# Se usa 'utf-8-sig' para asegurar la compatibilidad con caracteres especiales en Excel
df.to_csv(ruta_csv_salida, index=False, encoding='utf-8-sig')

print(f"💾 ¡Éxito! Archivo CSV guardado en: {ruta_csv_salida}")
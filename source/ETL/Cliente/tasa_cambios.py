import requests

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL
# -----------------------------------------------------------------------------

API_KEY = "da7f1b7bdc85c3fb30daa9ad"

# URL base correcta de la API para obtener datos.
BASE_URL = "https://v6.exchangerate-api.com/v6"

# -----------------------------------------------------------------------------
# 2. LÓGICA DE PETICIÓN A LA API
# -----------------------------------------------------------------------------
VALORES_POR_DEFECTO = {
    "PEN": 3.50,
    "EUR": 0.95,
    "COP": 4000.00,
    "MXN": 20.00,
    "CLP": 800.00,
    "ARS": 150.00
}
def run(moneda_base="USD"):
    """
    Realiza una petición GET a ExchangeRate-API para obtener las últimas tasas de cambio.
    """
    # Construimos la URL completa para la petición.
    url = f"{BASE_URL}/{API_KEY}/latest/{moneda_base}"
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"-> Error en la petición. Código de estado: {response.status_code}")

            return None

    except requests.exceptions.RequestException as e:
        print(f"-> Error de Conexión: No se pudo establecer la comunicación con la API.")
        print(f"-> Detalle del error: {e}")
        return None

# -----------------------------------------------------------------------------
# 3. LÓGICA DE EXTRACCIÓN GENÉRICA
# -----------------------------------------------------------------------------
def obtener_tasa_especifica(moneda_origen, moneda_destino):
    """
    Utiliza el cliente API para obtener la tasa de cambio específica entre dos monedas.

    Args:
        moneda_origen (str): El código de la moneda de la cual se parte (ej. "USD").
        moneda_destino (str): El código de la moneda a la que se quiere llegar (ej. "PEN").

    Returns:
        float: El valor numérico de la tasa de cambio si la extracción es exitosa.
        None: Si no se pueden obtener los datos o no se encuentra la tasa específica.
    """
    print(f"\n--- Obteniendo tasa de {moneda_origen} a {moneda_destino} ---")
    
    # 1. Uso del Cliente: Hacemos la petición usando la moneda de origen como base.
    datos_completos = run(moneda_origen)

    # Verificación inicial.
    if not datos_completos or datos_completos.get("result") != "success":
        print(f"Error: No se pudo obtener una respuesta válida de la API para la base {moneda_origen}.")

        # Plan de respaldo: si falla la API, devolvemos un valor por defecto.
        return VALORES_POR_DEFECTO[moneda_destino] if moneda_destino in VALORES_POR_DEFECTO else None

    # 2. Parseo de JSON para la moneda de destino.    
    tasas = datos_completos.get('conversion_rates', {})
    tasa_especifica = tasas.get(moneda_destino)

    # 3. Extracción de Valor
    if tasa_especifica is not None:
        return tasa_especifica
    else:
        print(f"Error: La tasa de cambio para '{moneda_destino}' no fue encontrada en la respuesta.")
        return None


# --- Constantes y Configuración ---

# Define la moneda base contra la que quieres comparar las demás.
MONEDA_BASE = "USD"

# Lista de monedas para las cuales quieres obtener la tasa de cambio.
# ¡Puedes agregar o quitar las que necesites!
MONEDAS_OBJETIVO = ["PEN", "EUR", "COP", "MXN", "CLP", "ARS"]

def obtener_todas_las_tasas():
    """
    Obtiene las tasas de cambio para una lista predefinida de monedas contra
    una moneda base y las devuelve en un diccionario.

    Returns:
        dict: Un diccionario con las monedas como llaves y sus tasas de cambio como valores.
              Ej: {'PEN': 3.75, 'EUR': 0.92}
              Retorna un diccionario vacío si la API falla para todas las monedas.
    """
    tasas_obtenidas = {}

    for moneda_destino in MONEDAS_OBJETIVO:
        # Llama a la función que contacta a la API para un par específico.
        tasa = obtener_tasa_especifica(MONEDA_BASE, moneda_destino)

        if tasa is not None:
            tasas_obtenidas[moneda_destino] = tasa

    # Plan de respaldo: si después de todos los intentos el diccionario está vacío,
    # podemos devolver valores por defecto para no romper la aplicación.
    if not tasas_obtenidas:
        print("ADVERTENCIA: Falló la obtención de TODAS las tasas. Usando valores por defecto.")
        return VALORES_POR_DEFECTO

    return tasas_obtenidas

print(obtener_tasa_especifica("USD", "PEN"))
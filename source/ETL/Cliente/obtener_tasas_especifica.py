# extractor_tasa.py

# -----------------------------------------------------------------------------
# 1. REUTILIZACIÓN DEL CLIENTE
# -----------------------------------------------------------------------------
# Importamos la función que ya creamos y validamos.
from obtener_tasas_de_cambio import run


# -----------------------------------------------------------------------------
# 2. LÓGICA DE EXTRACCIÓN GENÉRICA
# -----------------------------------------------------------------------------
def rana(moneda_origen, moneda_destino):
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
        return None

    # 2. Parseo de JSON para la moneda de destino.
    print(f"Respuesta válida recibida. Buscando la tasa para '{moneda_destino}'...")
    
    tasas = datos_completos.get('conversion_rates', {})
    tasa_especifica = tasas.get(moneda_destino)

    # 3. Extracción de Valor
    if tasa_especifica is not None:
        print(f"¡Tasa encontrada! 1 {moneda_origen} = {tasa_especifica} {moneda_destino}")
        return tasa_especifica
    else:
        print(f"Error: La tasa de cambio para '{moneda_destino}' no fue encontrada en la respuesta.")
        return None

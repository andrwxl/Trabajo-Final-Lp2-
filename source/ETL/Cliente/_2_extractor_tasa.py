# extractor_tasa.py

# -----------------------------------------------------------------------------
# 1. REUTILIZACIÓN DEL CLIENTE
# -----------------------------------------------------------------------------
# Importamos la función que ya creamos y validamos.
from _1_cliente_api_equipo import obtener_tasas_de_cambio

# -----------------------------------------------------------------------------
# 2. LÓGICA DE EXTRACCIÓN GENÉRICA
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
    datos_completos = obtener_tasas_de_cambio(moneda_origen)

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

# -----------------------------------------------------------------------------
# 3. EJECUCIÓN DE PRUEBA
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("--- Iniciando prueba del extractor de tasas de cambio ---")
    
    # --- Prueba 1: Dólar a Sol (USD -> PEN) ---
    tasa_usd_pen = obtener_tasa_especifica("USD", "PEN")
    if tasa_usd_pen:
        print(f"Resultado final: La tasa de USD a PEN es {tasa_usd_pen}")
    else:
        print("No se pudo obtener la tasa de USD a PEN.")

    # --- Prueba 2: Euro a Dólar (EUR -> USD) ---
    tasa_eur_usd = obtener_tasa_especifica("EUR", "USD")
    if tasa_eur_usd:
        print(f"Resultado final: La tasa de EUR a USD es {tasa_eur_usd}")
        
        # Ejemplo de uso
        monto_eur = 100
        monto_usd = monto_eur * tasa_eur_usd
        print(f"Cálculo de ejemplo: €{monto_eur} EUR son ${monto_usd:.2f} USD")
    else:
        print("No se pudo obtener la tasa de EUR a USD.")
    # --- Prueba 3: Yen Japonés a Dólar (JPY -> USD) ---
    tasa_jpy_usd = obtener_tasa_especifica("JPY", "USD")
    if tasa_jpy_usd:
        print(f"Resultado final: La tasa de JPY a USD es {tasa_jpy_usd}")
        
        # Ejemplo de uso
        monto_jpy = 10000
        monto_usd = monto_jpy * tasa_jpy_usd
        print(f"Cálculo de ejemplo: ¥{monto_jpy} JPY son ${monto_usd:.2f} USD")
    else:
        print("No se pudo obtener la tasa de JPY a USD.")
# -----------------------------------------------------------------------------
# Fin del script principal
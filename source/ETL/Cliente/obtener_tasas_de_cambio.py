# cliente_api_equipo.py

# -----------------------------------------------------------------------------
# 1. IMPORTACIÓN DE LIBRERÍAS
# -----------------------------------------------------------------------------
# Solo necesitamos 'requests' porque la clave estará directamente en el código.
import requests

# -----------------------------------------------------------------------------
# 2. CONFIGURACIÓN INICIAL
# -----------------------------------------------------------------------------
# API Key "hardcodeada" (escrita directamente en el código).
# Esto facilita que todo el equipo pueda ejecutar el script sin configurar un .env
# ¡ADVERTENCIA! No subir este archivo a un repositorio PÚBLICO de GitHub.
API_KEY = "093cdfe918a4eca90bec6179"

# URL base correcta de la API para obtener datos.
BASE_URL = "https://v6.exchangerate-api.com/v6"

# -----------------------------------------------------------------------------
# 3. LÓGICA DE PETICIÓN A LA API
# -----------------------------------------------------------------------------
def run(moneda_base="USD"):
    """
    Realiza una petición GET a ExchangeRate-API para obtener las últimas tasas de cambio.
    """
    # Construimos la URL completa para la petición.
    url = f"{BASE_URL}/{API_KEY}/latest/{moneda_base}"
    
    print(f"-> Realizando petición a la API: {url}")

    try:
        response = requests.get(url)

        if response.status_code == 200:
            print("-> ¡Conexión Exitosa! Respuesta recibida (HTTP 200 OK).")
            return response.json()
        else:
            print(f"-> Error en la petición. Código de estado: {response.status_code}")
            print(f"-> Mensaje de la API: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"-> Error de Conexión: No se pudo establecer la comunicación con la API.")
        print(f"-> Detalle del error: {e}")
        return None

# -----------------------------------------------------------------------------
# 4. EJECUCIÓN DE PRUEBA
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("--- Iniciando prueba del cliente API (Versión para equipo) ---")
    
    datos_tasas = run("USD")
    
    if datos_tasas and datos_tasas.get("result") == "success":
        print("\n--- Procesando Respuesta Válida ---")
        
        moneda_base = datos_tasas.get("base_code")
        tasas = datos_tasas.get("conversion_rates")
        
        print(f"Moneda Base consultada: {moneda_base}")
        print(f"Tasa de cambio para el Euro (EUR): {tasas.get('EUR')}")
        print(f"Tasa de cambio para el Sol Peruano (PEN): {tasas.get('PEN')}")
        
        print("\n¡El cliente está listo y funcionando correctamente!")
        
    else:
        print("\n--- La prueba ha fallado. No se pudieron obtener los datos. ---")


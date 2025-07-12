import streamlit as st
# Asumimos que esta función ya la tienes y funciona correctamente.
# Proviene de tu módulo Cliente/obtener_tasas_especifica.py
from obtener_tasas_especifica import rana

# --- Constantes y Configuración ---

# Define la moneda base contra la que quieres comparar las demás.
MONEDA_BASE = "USD"

# Lista de monedas para las cuales quieres obtener la tasa de cambio.
# ¡Puedes agregar o quitar las que necesites!
MONEDAS_OBJETIVO = ["PEN", "EUR", "BRL", "COP", "MXN", "CLP"]

def obtener_todas_las_tasas():
    """
    Obtiene las tasas de cambio para una lista predefinida de monedas contra
    una moneda base y las devuelve en un diccionario.

    Returns:
        dict: Un diccionario con las monedas como llaves y sus tasas de cambio como valores.
              Ej: {'PEN': 3.75, 'EUR': 0.92}
              Retorna un diccionario vacío si la API falla para todas las monedas.
    """
    print(f"Obteniendo tasas de cambio actualizadas contra {MONEDA_BASE}...")
    tasas_obtenidas = {}

    for moneda_destino in MONEDAS_OBJETIVO:
        print(f" -> Solicitando tasa para {MONEDA_BASE} -> {moneda_destino}...")
        
        # Llama a la función que contacta a la API para un par específico.
        tasa = rana(MONEDA_BASE, moneda_destino)

        if tasa is not None:
            tasas_obtenidas[moneda_destino] = tasa
            print(f"    Tasa obtenida: {tasa}")
        else:
            # Si la API falla para una moneda, lo registramos y continuamos.
            # No se añade al diccionario para no tener datos incorrectos.
            print(f"    ADVERTENCIA: Falló la obtención de la tasa para {moneda_destino}.")

    # Plan de respaldo: si después de todos los intentos el diccionario está vacío,
    # podemos devolver valores por defecto para no romper la aplicación.
    if not tasas_obtenidas:
        print("ADVERTENCIA: Falló la obtención de TODAS las tasas. Usando valores por defecto.")
        return {
            "PEN": 3.70,
            "EUR": 0.95 
        } # Puedes añadir más valores por defecto aquí

    return tasas_obtenidas

# Usamos la caché de Streamlit para eficiencia. La API solo se llamará una vez cada hora.
# La función cacheada ahora es la que obtiene TODAS las tasas.
@st.cache_data(ttl=3600) # ttl=3600 segundos (1 hora)
def obtener_tasas_cacheada():
    """
    Función envoltorio que llama a la lógica principal y cuyo resultado
    es almacenado en la caché de Streamlit.
    """
    return obtener_todas_las_tasas()

# --- Punto de Entrada Principal ---

# Llamamos a la función para obtener el diccionario de tasas (ya sea de la caché o de la API)
# Esta es la variable que importarás en otros archivos de tu aplicación.
TASAS_DE_CAMBIO = obtener_tasas_cacheada()

# Ejemplo de cómo podrías usarlo en este mismo archivo para probar:
if __name__ == "__main__":
    print("\n--- Resultados Finales ---")
    print("El diccionario de tasas de cambio es:")
    print(TASAS_DE_CAMBIO)
    
    # Ejemplo de cómo acceder a una tasa específica:
    tasa_sol_peruano = TASAS_DE_CAMBIO.get("PEN")
    if tasa_sol_peruano:
        print(f"\nLa tasa de cambio para el Sol Peruano (PEN) es: {tasa_sol_peruano}")
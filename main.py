# Contenido para: main.py

# Esta es una importación ABSOLUTA. Le dice a Python la ruta completa
# desde la raíz del proyecto (la carpeta 'source').
from source.ETL.Cliente.tasa_cambios import TASAS_DE_CAMBIO

def iniciar_aplicacion():
    """
    Función principal que ejecuta el programa.
    """
    print("--- ¡Aplicación iniciada correctamente! ---")
    print("El diccionario de tasas de cambio obtenido es:")
    
    # La variable TASAS_DE_CAMBIO fue importada desde tu módulo
    print(TASAS_DE_CAMBIO)

    # NOTA: En el futuro, aquí es donde iniciarías tu aplicación de Streamlit.
    # Por ejemplo, llamarías a una función que construya la interfaz.

# Esta es una buena práctica para asegurar que el código se ejecute solo
# cuando corres este archivo directamente.
if __name__ == "__main__":
    iniciar_aplicacion()
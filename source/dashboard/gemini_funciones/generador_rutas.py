import streamlit as st
import google.generativeai as genai
import json
#from config import GEMINI_API_KEY
GEMINI_API_KEY = "AIzaSyCyxpK5dsK8YwVwsr9lCpS-8UKPul5lcbc"
# --- Configuración del Modelo de IA ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error al configurar la API de Gemini: {e}")
    model = None

# --- Funciones de Lógica ---

def generar_ruta_de_carrera_ia(rol_actual, rol_deseado, habilidades_disponibles):
    """
    Llama a la API de Gemini para generar una ruta de aprendizaje de 3 pasos,
    restringiendo las habilidades a una lista predefinida.
    """
    if not model:
        return "Error: El modelo de IA no está disponible."

    # Convertimos la lista de habilidades a un string para el prompt.
    habilidades_str = ", ".join(habilidades_disponibles)

    # Creamos el prompt estructurado y muy específico.
    prompt = f"""
    Actúa como un consejero de carrera experto.
    Crea una ruta de aprendizaje para una persona que actualmente es '{rol_actual}' y quiere convertirse en '{rol_deseado}'.
    Si el rol actual es 'ninguno' o está vacío, asume que empieza desde cero.
    La ruta debe tener exactamente 3 pasos lógicos y concisos.
    Para cada paso, debes elegir UNA SOLA habilidad principal de la siguiente lista de habilidades permitidas:
    ---
    LISTA DE HABILIDADES PERMITIDAS:
    {habilidades_str}
    ---
    Tu respuesta DEBE ser un objeto JSON válido con la siguiente estructura:
    {{
      "paso1": {{"habilidad": "NombreDeLaHabilidad1", "descripcion": "Descripción del paso 1"}},
      "paso2": {{"habilidad": "NombreDeLaHabilidad2", "descripcion": "Descripción del paso 2"}},
      "paso3": {{"habilidad": "NombreDeLaHabilidad3", "descripcion": "Descripción del paso 3"}}
    }}
    Asegúrate de que el nombre de la habilidad en el JSON coincida EXACTAMENTE con uno de la lista permitida.
    No incluyas ningún texto adicional, solo el JSON.
    """

    try:
        with st.spinner("Diseñando tu ruta de carrera personalizada..."):
            respuesta = model.generate_content(prompt)
            # Limpiamos la respuesta para asegurarnos de que sea un JSON válido
            json_text = respuesta.text.strip().replace("```json", "").replace("```", "")
            return json.loads(json_text)
    except Exception as e:
        st.error(f"Ocurrió un error al generar la ruta de carrera: {e}")
        st.error(f"Respuesta recibida de la IA (puede no ser JSON válido): {respuesta.text}")
        return None

# --- Función Principal del Componente ---

def mostrar_generador_rutas():
    """
    Muestra la sección completa del Generador de Rutas de Carrera en el dashboard.
    """
    st.header("🗺️ Generador de Rutas de Carrera con IA")
    st.write("Define tu punto de partida y tu meta profesional. La IA trazará un plan de 3 pasos lógicos para ayudarte a llegar allí, basado en habilidades clave del mercado.")

    # --- DATOS DE EJEMPLO ---
    # En tu app.py real, estos datos vendrían de tu scraping o de un archivo.
    mapa_habilidades_links = {
        "Python": "https://docs.python.org/3/",
        "SQL": "https://www.w3schools.com/sql/",
        "Power BI": "https://learn.microsoft.com/en-us/power-bi/",
        "AWS": "https://aws.amazon.com/documentation/",
        "React": "https://react.dev/",
        "Docker": "https://docs.docker.com/",
        "Kubernetes": "https://kubernetes.io/docs/home/",
        "Java": "https://dev.java/learn/",
        "TypeScript": "https://www.typescriptlang.org/docs/"
    }
    lista_habilidades_disponibles = list(mapa_habilidades_links.keys())

    col1, col2 = st.columns(spec=[0.7,0.3])
    with col1:
        rol_actual = st.text_input("Tu rol o punto de partida actual:", placeholder="Ej: Analista de Datos, o 'ninguno'")
    with col2:
        rol_deseado = st.text_input("El rol al que aspiras:", placeholder="Ej: Ingeniero de Machine Learning")

    if st.button("Generar mi Ruta de Carrera", key="btn_generar_ruta"):
        if rol_deseado:
            ruta = generar_ruta_de_carrera_ia(rol_actual, rol_deseado, lista_habilidades_disponibles)
            
            if ruta:
                st.subheader(f"Tu Ruta de '{rol_actual or 'Cero'}' a '{rol_deseado}'")

                # --- Visualización de la Línea de Tiempo ---
                st.markdown("---")
                st.markdown("##### 📍 AHORA")
                
                for i, (paso_key, paso_data) in enumerate(ruta.items()):
                    habilidad = paso_data.get("habilidad", "N/A")
                    descripcion = paso_data.get("descripcion", "N/A")
                    link = mapa_habilidades_links.get(habilidad, "#")

                    st.markdown("""
                        <div style="margin-left: 20px; border-left: 3px solid #4A5568; padding-left: 20px; padding-bottom: 20px;">
                            <p><strong>Paso {}:</strong> {}</p>
                            <p>🎯 <strong>Habilidad Clave:</strong> {} <a href="{}" target="_blank" style="text-decoration: none;">🔗</a></p>
                        </div>
                    """.format(i + 1, descripcion, habilidad, link), unsafe_allow_html=True)

                st.markdown("##### 🏁 GOAL")
                st.markdown("---")
        else:
            st.warning("Por favor, ingresa el rol al que aspiras.")


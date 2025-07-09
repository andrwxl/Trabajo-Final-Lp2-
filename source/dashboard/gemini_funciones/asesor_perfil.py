import streamlit as st
import pandas as pd
import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyCyxpK5dsK8YwVwsr9lCpS-8UKPul5lcbc"

# --- Configuración del Modelo de IA ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    st.error(f"Error al configurar la API de Gemini: {e}")
    model = None

# --- Funciones de Lógica ---

def procesar_input_habilidades(skills_input):
    if not skills_input:
        return []
    habilidades = [skill.strip().lower() for skill in skills_input.split(',')]
    return list(filter(None, habilidades))

def analizar_con_datos_locales(df, habilidades_usuario):
    if not habilidades_usuario:
        return "N/A", 0, 0

    df['puesto_trabajo_lower'] = df['puesto_trabajo'].str.lower()
    
    # Filtra ofertas que contengan CUALQUIERA de las habilidades del usuario
    mask = df['puesto_trabajo_lower'].apply(lambda x: any(skill in x for skill in habilidades_usuario))
    df_relevante = df[mask]

    if df_relevante.empty:
        return "Baja", 0, 0

    num_ofertas = len(df_relevante)
    salario_estimado = df_relevante['salario_anual_usd'].mean()

    if num_ofertas > 100:
        demanda = "Alta"
    elif num_ofertas > 20:
        demanda = "Media"
    else:
        demanda = "Baja"
        
    return demanda, salario_estimado, num_ofertas

def generar_respuesta_ia(prompt):
    if not model:
        return "El modelo de IA no está disponible."
    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"Error al contactar la API de IA"

# --- Función Principal del Componente ---

def mostrar_asesor_perfil(df, moneda, periodo, tipo_cambio):
    st.header("🧠 Asesor de Perfil Inteligente")
    st.write("Ingresa tus habilidades para obtener un análisis 360° que combina datos reales del mercado con inteligencia artificial estratégica.")

    skills_input = st.text_area(
        "Ingresa tus habilidades (separadas por comas):",
        placeholder="Ej: Python, SQL, Power BI, AWS, React",
        height=100,
        key="skills_input_asesor"
    )

    if st.button("Analizar mi Perfil", key="btn_analizar_asesor"):
        habilidades_usuario = procesar_input_habilidades(skills_input)
        
        if habilidades_usuario:
            
            with st.spinner("Realizando análisis híbrido (Datos + IA)..."):
                # 1. Consulta a tus Datos (Evidencia Real)
                demanda, salario_usd, num_ofertas = analizar_con_datos_locales(df, habilidades_usuario)

                # 2. Peticiones a la IA (Inteligencia Estratégica)
                habilidades_str = ", ".join(habilidades_usuario)
                
                
                 # --- INICIO DE LA MODIFICACIÓN: LOG DE PROGRESO ---
            
                # Creamos un contenedor para los logs que se irá actualizando.
                log_container = st.empty()

                # Paso 1: Análisis de datos locales
                log_container.info("Paso 1 de 3: Analizando la base de datos local para calcular demanda y salario...")
                demanda, salario_usd, num_ofertas = analizar_con_datos_locales(df, habilidades_usuario)
                log_container.success("Paso 1 completado: Análisis de datos locales finalizado.")

                # Paso 2: Petición a la IA para sugerencias
                log_container.info("Paso 2 de 3: Consultando a la IA para obtener sugerencias de habilidades...")
                habilidades_str = ", ".join(habilidades_usuario)
                prompt_sugerencias = f"Un profesional tiene las siguientes habilidades: {habilidades_str}. Recomienda 3 tecnologías que complementen su perfil para potenciar su carrera. Devuelve solo una lista de texto plano, donde cada sugerencia esté en una nueva línea y empiece con un guion."
                sugerencias_ia = generar_respuesta_ia(prompt_sugerencias)
                log_container.success("Paso 2 completado: Sugerencias de la IA recibidas.")

                # Paso 3: Petición a la IA para mensaje
                log_container.info("Paso 3 de 3: Consultando a la IA para generar un mensaje personalizado...")
                prompt_mensaje = f"Escribe un mensaje alentador y profesional de 2 líneas para alguien con las siguientes habilidades: {habilidades_str}, destacando su valor en el mercado actual."
                mensaje_ia = generar_respuesta_ia(prompt_mensaje)
                log_container.success("¡Análisis híbrido completado!")
            
                # --- FIN DE LA MODIFICACIÓN ---

            st.success(f"Análisis completado. Se encontraron {num_ofertas} ofertas relevantes para tu perfil.")
            
            # --- 3. Presentación de Resultados ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Análisis de Mercado (Datos Reales)")
                st.metric("Demanda del Perfil", demanda)
                
                salario_display = salario_usd
                if periodo == 'Mensual':
                    salario_display /= 12
                simbolo = "S/" if moneda == 'PEN' else "$"
                if moneda == 'PEN':
                    salario_display *= tipo_cambio
                
                st.metric(f"Salario Estimado {periodo} ({moneda})", f"{simbolo}{salario_display:,.0f}" if salario_usd > 0 else "N/A")

            with col2:
                st.subheader("Consejos de la IA")
                st.info(f"**Mensaje para ti:**\n\n{mensaje_ia}")
                st.markdown("**Habilidades sugeridas para potenciar tu perfil:**")
                st.markdown(sugerencias_ia)
        else:
            st.warning("Por favor, ingresa al menos una habilidad para analizar.")


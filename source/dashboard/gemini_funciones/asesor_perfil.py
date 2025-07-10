import streamlit as st
import pandas as pd
import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyCyxpK5dsK8YwVwsr9lCpS-8UKPul5lcbc"

# --- Configuración del Modelo de IA ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
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
        return "N/A", 0, 0, pd.DataFrame()

    df['puesto_trabajo_lower'] = df['puesto_trabajo'].str.lower()
    
    # Filtra ofertas que contengan CUALQUIERA de las habilidades del usuario
    mask = df['puesto_trabajo_lower'].apply(lambda x: any(skill in x for skill in habilidades_usuario))
    df_relevante = df[mask]

    if df_relevante.empty:
        return "Baja", 0, 0, pd.DataFrame()

    num_ofertas = len(df_relevante)
    salario_estimado = df_relevante['salario_anual_usd'].mean()    
    if pd.isna(salario_estimado):
        salario_estimado = 0
    if num_ofertas > 100:
        demanda = "Alta"
    elif num_ofertas > 20:
        demanda = "Media"
    else:
        demanda = "Baja"
        
    return demanda, salario_estimado, num_ofertas, df_relevante

def generar_respuesta_ia(prompt):
    if not model:
        return "El modelo de IA no está disponible."
    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"Error al contactar la API de IA"

# --- Función Principal del Componente ---

def mostrar_asesor_perfil(df, moneda, periodo, tipo_cambio, paises):
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
            
            df_empleos_sugeridos = pd.DataFrame() 
            with st.spinner("Realizando análisis híbrido (Datos + IA)..."):
                # Creamos un contenedor para los logs que se irá actualizando.
                log_container = st.empty()

                # Paso 1: Análisis de datos locales
                log_container.info("Paso 1 de 3: Analizando la base de datos local para calcular demanda y salario...")
                demanda, salario_usd, num_ofertas, df_empleos_sugeridos = analizar_con_datos_locales(df, habilidades_usuario)
                
                # Convertimos el salario a la moneda seleccionada y ajustamos el periodo
                if salario_usd > 0 and salario_usd is not None:
                    df_empleos_sugeridos['salario_display'] = df_empleos_sugeridos['salario_anual_usd'] * tipo_cambio if moneda == 'PEN' else df_empleos_sugeridos['salario_anual_usd']
                    df_empleos_sugeridos['salario_display'] = df_empleos_sugeridos['salario_display'] / (12 if periodo == 'Mensual' else 1)

                    salario_usd = salario_usd * tipo_cambio if moneda == 'PEN' else salario_usd
                    salario_display = salario_usd / (12 if periodo == 'Mensual' else 1)
                else:
                    salario_display = "N/A"


                log_container.success("Paso 1 completado: Análisis de datos locales finalizado.")

                # Paso 2: Petición a la IA para sugerencias
                log_container.info("Paso 2 de 3: Consultando a la IA para obtener sugerencias de habilidades...")
                habilidades_str = ", ".join(habilidades_usuario)
                prompt_sugerencias = f"Un profesional tiene las siguientes habilidades: {habilidades_str}. Recomienda 3 tecnologías que complementen su perfil para potenciar su carrera. Devuelve solo una lista de texto plano, donde cada sugerencia esté en una nueva línea y empiece con un guion."
                sugerencias_ia = generar_respuesta_ia(prompt_sugerencias)
                log_container.success("Paso 2 completado: Sugerencias de la IA recibidas.")
                # Paso 3: Petición a la IA para mensaje
                log_container.info("Paso 3 de 3: Consultando a la IA para generar un mensaje personalizado...")
                prompt_mensaje = f"Escribe un mensaje alentador y profesional de 2 líneas para alguien con las siguientes habilidades: {habilidades_str}, destacando su valor en el mercado actual que según los datos analizados es {demanda} y el salario promedio es {salario_display} {tipo_cambio} al {periodo}. El mensaje debe corto y directo como si estas en una conversación de WhatsApp."
                mensaje_ia = generar_respuesta_ia(prompt_mensaje)
                log_container.success("¡Análisis híbrido completado!")
            
            st.success(f"Análisis completado. Se encontraron {num_ofertas} ofertas relevantes para tu perfil.")
            
            # --- 3. Presentación de Resultados ---
            col1, col2 = st.columns(spec=[0.7,0.3])
            
            with col1:
                varPais = " a nivel global"
                if len(paises) == 1:
                    varPais = f" en {paises[0]}"
                
                st.subheader(f"Análisis de Mercado (Datos Reales {varPais})")
                st.metric("Demanda del Perfil", demanda)
                
                simbolo = "S/" if moneda == 'PEN' else "$"
                salario_display = salario_usd
                if periodo == 'Mensual':
                    salario_display /= 12
                
                st.metric(f"Salario Estimado {periodo} ({moneda})", f"{simbolo}{salario_display:,.0f}" if salario_display > 0 else "N/A")

                st.data_editor(
                    df_empleos_sugeridos,
                    column_config={
                        # Le decimos a Streamlit que la columna 'enlace_oferta'
                        # debe ser tratada como una columna de enlaces.
                        "enlace_oferta": st.column_config.LinkColumn(
                            "Link a la Oferta", # El título que se mostrará en la cabecera de la columna.
                            display_text="Ver Oferta" # El texto que se mostrará en cada celda.
                        )
                    },
                    # Definimos las columnas que queremos mostrar y su orden.
                    column_order=(
                        "puesto_trabajo", 
                        "nombre_empresa", 
                        "pais", 
                        "salario_display", 
                        "enlace_oferta"
                    ),
                    hide_index=True, # Ocultamos el índice del DataFrame para un look más limpio.
                    use_container_width=True # Hacemos que la tabla use todo el ancho del contenedor.
                )
            with col2:
                st.subheader("Consejos de la IA")
                st.info(f"**Mensaje para ti:**\n\n{mensaje_ia}")
                st.markdown("**Habilidades sugeridas para potenciar tu perfil:**")
                st.markdown(sugerencias_ia)
            return df_empleos_sugeridos
        else:
            st.warning("Por favor, ingresa al menos una habilidad para analizar.")


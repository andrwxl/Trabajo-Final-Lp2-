import streamlit as st
import pandas as pd
from collections import Counter

# --- Funciones para el Comparador de Perfiles ---

def procesar_input_habilidades(skills_input):
    """Limpia y convierte el string de habilidades del usuario en una lista."""
    if not skills_input:
        return []
    # Convierte a minúsculas, divide por comas y quita espacios en blanco.
    habilidades = [skill.strip().lower() for skill in skills_input.split(',')]
    # Elimina elementos vacíos que puedan resultar de comas extra.
    return list(filter(None, habilidades))

def analizar_perfil_usuario(df, habilidades_usuario):
    """
    Analiza el DataFrame de ofertas para encontrar coincidencias, calcular métricas
    y sugerir nuevas habilidades.
    """
    if not habilidades_usuario:
        return None, None, None, None

    # Asegurarnos de que la columna de habilidades sea una lista de strings.
    # Esto es crucial si se lee de un CSV.
    df['puesto_trabajo'] = df['puesto_trabajo'].fillna('').astype(str)

    # Calculamos el puntaje de coincidencia para cada oferta.
    def calcular_coincidencia(habilidades_oferta):
        # Cuenta cuántas habilidades del usuario están en la oferta.
        habilidades_oferta_lower = [str(s).lower() for s in habilidades_oferta.split()]
        return len(set(habilidades_usuario) & set(habilidades_oferta_lower))

    df['coincidencia'] = df['puesto_trabajo'].apply(calcular_coincidencia)

    # Filtramos las ofertas que son relevantes (coinciden con al menos una habilidad).
    df_relevante = df[df['coincidencia'] > 0].copy()

    if df_relevante.empty:
        return "Baja", 0, [], 0

    # --- Cálculo de Métricas ---
    
    # 1. Demanda del Perfil
    num_ofertas_relevantes = len(df_relevante)
    if num_ofertas_relevantes > 100:
        demanda = "Alta"
    elif num_ofertas_relevantes > 20:
        demanda = "Media"
    else:
        demanda = "Baja"
        
    # 2. Salario Estimado
    salario_estimado = df_relevante['salario_anual_usd'].mean()

    # 3. Habilidades Sugeridas
    # Juntamos todas las habilidades de las ofertas relevantes en una gran lista.
    todas_las_habilidades = []
    for habilidades in df_relevante['puesto_trabajo']:
        todas_las_habilidades.extend([s.lower() for s in str(habilidades).split()])
    
    # Contamos la frecuencia de cada habilidad.
    conteo_habilidades = Counter(todas_las_habilidades)
    
    # Eliminamos las habilidades que el usuario ya tiene.
    for skill in habilidades_usuario:
        del conteo_habilidades[skill]
        
    # Las 3 más comunes son las sugeridas.
    habilidades_sugeridas = [skill for skill, count in conteo_habilidades.most_common(3)]

    return demanda, salario_estimado, habilidades_sugeridas, num_ofertas_relevantes

def mostrar_comparador_perfiles(df, moneda, periodo, tipo_cambio):
    """
    Muestra la sección completa del comparador de perfiles en el dashboard.
    """
    st.header("Comparador de Perfiles")
    
    # Usamos st.session_state para "recordar" el input del usuario.
    if 'skills_input' not in st.session_state:
        st.session_state.skills_input = "Python, SQL, Power BI"

    skills_input = st.text_area(
        "Ingresa tus habilidades (separadas por comas)",
        value=st.session_state.skills_input,
        height=100,
        key="skills_input_area"
    )

    if st.button("Analizar mi Perfil"):
        st.session_state.skills_input = skills_input # Actualizamos el estado
        
        habilidades_usuario = procesar_input_habilidades(skills_input)
        
        if habilidades_usuario:
            with st.spinner("Analizando el mercado para tu perfil..."):
                demanda, salario, sugerencias, num_ofertas = analizar_perfil_usuario(df, habilidades_usuario)
            
            st.success(f"Análisis completado. Se encontraron {num_ofertas} ofertas relevantes para tu perfil.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Resultados de tu Perfil")
                # Mostramos los resultados en tarjetas de métricas.
                st.metric("Demanda del Perfil", demanda)
                
                # Lógica de conversión para el salario estimado
                salario_display = salario
                if periodo == 'Mensual':
                    salario_display /= 12
                simbolo = "S/" if moneda == 'PEN' else "$"
                if moneda == 'PEN':
                    salario_display *= tipo_cambio
                
                st.metric(f"Salario Estimado {periodo} ({moneda})", f"{simbolo}{salario_display:,.0f}" if salario > 0 else "N/A")

            with col2:
                st.subheader("Habilidades para Potenciar tu Perfil")
                if sugerencias:
                    for skill in sugerencias:
                        st.info(f"💡 Considera aprender **{skill.title()}**. Es una habilidad muy demandada en los roles que coinciden con tu perfil.")
                else:
                    st.info("¡Tu perfil es muy completo! No encontramos sugerencias obvias en este momento.")
        else:
            st.warning("Por favor, ingresa al menos una habilidad para analizar.")


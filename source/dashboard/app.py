import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
from gemini_funciones.asesor_perfil import mostrar_asesor_perfil
from gemini_funciones.generador_rutas import mostrar_generador_rutas
import time
import re


import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import ETL.Cliente.tasa_cambios as tasa_cambios
# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Mercado Laboral",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Llamamos a la función para obtener la tasa (ya sea de la caché o de la API)
TIPO_DE_CAMBIO_USD_PEN = tasa_cambios.obtener_tasa_especifica("USD", "PEN")
if not TIPO_DE_CAMBIO_USD_PEN:
    TIPO_DE_CAMBIO_USD_PEN = 3.50

# --- Funciones de Carga y Procesamiento ---


# --- LISTA DE HABILIDADES PREDEFINIDAS ---
LISTA_HABILIDADES_PREDEFINIDAS = sorted([
    "Python", "SQL", "Power BI", "Tableau", "AWS", "Azure", "GCP", "React",
    "JavaScript", "Excel", "Machine Learning", "Deep Learning", "Pandas",
    "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Airflow", "Docker",
    "Kubernetes", "Spark", "Data Warehouse", "ETL", "Big Data", "NoSQL",
    "MongoDB", "PostgreSQL", "Git", "Linux", "R", "Java", "C++", "HTML", "CSS"
])


@st.dialog("¡Bienvenido! Cuéntanos sobre ti")
def dialogo_de_registro():
    """
    Muestra un diálogo de bienvenida rediseñado para que el usuario seleccione
    sus habilidades de una lista predefinida de forma interactiva.
    """
    st.write(
        "**Selecciona tus habilidades clave de la lista.** "
        "Esto nos ayudará a encontrar tu trabajo ideal y darte recomendaciones personalizadas."
    )

    # Creamos un formulario dentro del diálogo.
    with st.form(key="registro_dialog_form"):
        # --- NUEVO: Selector de habilidades múltiples ---
        # st.multiselect es perfecto para simular la selección de "cajitas" o etiquetas.
        habilidades_seleccionadas = st.multiselect(
            "Tus habilidades:",
            options=LISTA_HABILIDADES_PREDEFINIDAS,
            placeholder="Elige una o más habilidades"
        )
        
        # Botón de envío del formulario.
        submitted = st.form_submit_button("Registrar y Empezar", use_container_width=True)

        if submitted:
            # Verificamos que el usuario haya seleccionado al menos una habilidad.
            if habilidades_seleccionadas:
                # --- NUEVO: Animación de carga ---
                # Usamos st.spinner para mostrar un mensaje mientras se procesa.
                with st.spinner('¡Personalizando tu experiencia! Un momento...'):
                    # Guardamos la lista en el estado de la sesión (en minúsculas por consistencia).
                    st.session_state.habilidades_usuario = [skill.lower() for skill in habilidades_seleccionadas]
                    
                    # Simulamos un pequeño retraso para que la animación sea visible.
                    time.sleep(2)
                
                # Forzamos un re-run para que el dashboard principal se cargue.
                # El diálogo se cierra automáticamente al finalizar la función después del rerun.
                st.rerun()
            else:
                # Si no seleccionó ninguna, mostramos una advertencia.
                st.warning("Por favor, selecciona al menos una habilidad para continuar.")

def mostrar_pantalla_registro():
    """
    Esta función no necesita cambios. Sigue funcionando perfectamente
    con el nuevo diálogo de registro.
    """
    # Si las habilidades no están en el estado de la sesión, llamamos a la función de diálogo.
    if "habilidades_usuario" not in st.session_state:
        dialogo_de_registro()

    # Si el usuario cierra el diálogo sin registrarse, st.stop() detiene la ejecución.
    if "habilidades_usuario" not in st.session_state:
        st.info("Por favor, completa el registro de habilidades para ver el contenido del dashboard.")
        st.stop()

    # Si llegamos aquí, significa que el usuario ya se registró. Devolvemos las habilidades.
    return st.session_state.habilidades_usuario


@st.cache_data
def cargar_y_preprocesar_datos(ruta_archivo):
    """
    Carga, limpia y estandariza el dataset maestro final.
    Crea una columna base 'salario_anual_usd' para todos los cálculos.
    """
    if not os.path.exists(ruta_archivo):
            st.error(f"Error: No se encontró el archivo en la ruta: {ruta_archivo}")
            return None
    
    try:
        df = pd.read_csv(ruta_archivo)
        for col in ['pais', 'puesto_trabajo', 'moneda_salario', 'periodo_salario']:
            if col in df.columns:
                df[col] = df[col].str.strip()
        
        for col in ['salario']:
             if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['salario_anual_base'] = np.where(df['periodo_salario'] == 'Mensual', df['salario'] * 12, df['salario'])
        df['salario_anual_usd'] = np.where(df['moneda_salario'] == 'PEN', df['salario_anual_base'] / TIPO_DE_CAMBIO_USD_PEN, df['salario_anual_base'])
        return df
    except Exception as e:
        st.error(f"Error al cargar o procesar el archivo CSV: {e}")
        return None


def mostrar_buscador_ofertas(df_filtrado, moneda, periodo, tipo_cambio, diccionario_habilidades):
    """
    Muestra una sección de búsqueda interactiva con paginación que ahora incluye
    enlaces para aprender habilidades relevantes para cada oferta.

    Args:
        df_filtrado (pd.DataFrame): El DataFrame con las ofertas ya filtradas.
        moneda (str): La moneda seleccionada ('PEN' o 'USD').
        periodo (str): El periodo salarial seleccionado ('Mensual' o 'Anual').
        tipo_cambio (float): La tasa de cambio de USD a PEN.
        diccionario_habilidades (dict): El diccionario con las habilidades y sus URLs.
    """
    st.header("🔍 Buscador Interactivo de Ofertas")

    # --- 1. Campo de búsqueda y estado de sesión (sin cambios) ---
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    search_query = st.text_input(
        "Busca por puesto, empresa o tecnología:",
        value=st.session_state.search_query,
        placeholder="Ej: Data Analyst, Google, Python...",
        key="search_query_input"
    )

    # --- 2. Lógica de filtrado en tiempo real (sin cambios) ---
    df_resultados = df_filtrado.copy()
    if search_query:
        query = search_query.lower()
        df_resultados = df_filtrado[
            df_filtrado['puesto_trabajo'].str.lower().str.contains(query, na=False) |
            df_filtrado['nombre_empresa'].str.lower().str.contains(query, na=False) |
            df_filtrado['categoria'].str.lower().str.contains(query, na=False)
        ]

    if df_resultados.empty:
        st.info(f"No se encontraron ofertas para la búsqueda: '{search_query}'")
        return

    # --- 3. Lógica de Paginación (sin cambios) ---
    items_por_pagina = 8
    total_items = len(df_resultados)
    total_paginas = -(-total_items // items_por_pagina)
    if 'pagina_actual_busqueda' not in st.session_state or st.session_state.pagina_actual_busqueda > total_paginas:
        st.session_state.pagina_actual_busqueda = 1
    pagina_actual = st.session_state.pagina_actual_busqueda
    start_idx = (pagina_actual - 1) * items_por_pagina
    end_idx = start_idx + items_por_pagina
    df_pagina = df_resultados.iloc[start_idx:end_idx]
    st.caption(f"Mostrando {len(df_pagina)} de {total_items} ofertas encontradas.")

    # --- 4. Visualización en Tarjetas (CON LA NUEVA LÓGICA) ---
    for i in range(0, len(df_pagina), 4):
        cols = st.columns(4)
        fila_ofertas = df_pagina.iloc[i:i+4]
        
        for col_idx, (row_idx, oferta) in enumerate(fila_ofertas.iterrows()):
            with cols[col_idx]:
                with st.container(border=True):
                    # Contenido de la tarjeta (título, empresa, salario, etc.)
                    st.markdown(f"**{oferta.get('puesto_trabajo', 'N/A')}**")
                    st.caption(f"{oferta.get('nombre_empresa', 'N/A')} • {oferta.get('pais', 'N/A')}, {oferta.get('region_estado', 'N/A')}")
                    st.caption(f"Fuente: {oferta.get('tipo_fuente_datos', 'N/A')} - {oferta.get('plataforma_origen', 'N/A')}")

                    salario_display = oferta.get('salario_anual_usd')
                    if pd.notna(salario_display):
                        if periodo == 'Mensual': salario_display /= 12
                        if moneda == 'PEN': salario_display *= tipo_cambio
                        simbolo_moneda = "S/" if moneda == 'PEN' else "$"
                        st.markdown(f"**Salario:** {simbolo_moneda}{salario_display:,.0f}")
                    else:
                        st.markdown("**Salario:** No especificado")

                    st.markdown("---", help=None)

                    # --- INICIO: Lógica de Enlaces de Aprendizaje ---
                    lista_habilidades = encontrar_habilidades_relevantes(
                        oferta['puesto_trabajo'], 
                        diccionario_habilidades
                    )
                    
                    html_enlaces_aprender = ""
                    if lista_habilidades:
                        enlaces = [
                            f"<a href='{url}' target='_blank' class='card-link'>Aprender {nombre} 🎓</a>"
                            for nombre, url in lista_habilidades
                        ]
                        html_enlaces_aprender = " • ".join(enlaces)

                    link_ver_oferta = f"<a href='{oferta.get('enlace_oferta', '#')}' target='_blank' class='card-link'>Ver Oferta →</a>"

                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex-grow: 1; font-size: 0.9em;'>{html_enlaces_aprender}</div>
                        <div style='white-space: nowrap; margin-left: 10px;'>{link_ver_oferta}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # --- FIN: Lógica de Enlaces de Aprendizaje ---
    
    st.markdown("---")

    # --- 5. Controles de Paginación (sin cambios) ---
    if total_paginas > 1:
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        with col_pag1:
            if st.button("← Anterior", disabled=(pagina_actual == 1), key="btn_anterior_busqueda", use_container_width=True):
                st.session_state.pagina_actual_busqueda -= 1
                st.rerun()
        with col_pag2:
            st.write(f"Página **{pagina_actual}** de **{total_paginas}**")
        with col_pag3:
            if st.button("Siguiente →", disabled=(pagina_actual >= total_paginas), key="btn_siguiente_busqueda", use_container_width=True):
                st.session_state.pagina_actual_busqueda += 1
                st.rerun()


# --- Funciones de Componentes del Dashboard ---

def mostrar_sidebar(df): # Funcion para mostrar la barra lateral con filtros
    st.sidebar.header("Filtros Globales")
    
    # --- Filtro por País (sin cambios) ---
    paises_disponibles = sorted(df['pais'].dropna().unique())
    paises_seleccionados = st.sidebar.multiselect(
        'Selecciona el País', 
        options=paises_disponibles, 
        default=paises_disponibles
    )

    
    # Filtro por Categoría
    categorias_disponibles = sorted(df['categoria'].dropna().unique())
    categorias_seleccionadas = st.sidebar.multiselect(
        'Selecciona la Categoría del Puesto', 
        options=categorias_disponibles, 
        default=[] # Por defecto, no hay ninguna categoría seleccionada.
    )
    

    # --- Filtros de Moneda y Periodo (sin cambios) ---
    moneda_seleccionada = st.sidebar.radio("Ver Salario en:", ('PEN', 'USD'), index=0, horizontal=True)
    #Mostrar un indicador de tasa de cambio actual y fuente
    st.sidebar.markdown(f"**Tasa de Cambio Actual:** 1 USD = {TIPO_DE_CAMBIO_USD_PEN:.2f} PEN")
    st.sidebar.markdown("Fuente: [API ExchangeRate](https://api.exchangerate-api.com/v4/latest/USD)")
    #
    periodo_seleccionado = st.sidebar.radio("Ver Periodo Salarial:", ('Mensual', 'Anual'), index=0, horizontal=True)
    # Filtro por tipo de fuente de datos
    st.sidebar.subheader("Plataforma de Fuente de Datos")
    tipo_fuente_disponible = sorted(df['plataforma_origen'].dropna().unique())
    seleccion_checkbox_fuente = {}
    for fuente in tipo_fuente_disponible:
        seleccion_checkbox_fuente[fuente] = st.sidebar.checkbox(
            fuente,
            value=True,
            key=f'fuente_{fuente}',
        )
    # Filtramos las fuentes seleccionadas
    tipo_fuente_seleccionadaente = [fuente for fuente, seleccionado in seleccion_checkbox_fuente.items() if seleccionado]

    # Filtro por tipo de extraccion
    tipo_extraccion_disponible = sorted(df['tipo_fuente_datos'].dropna().unique())

    st.sidebar.subheader("Tipo de Extracción de Datos")
    seleccion_checkbox = {}
    for tipo in tipo_extraccion_disponible:
        seleccion_checkbox[tipo] =  st.sidebar.checkbox(
            tipo,
            value=True,
            key=f'tipo_fuente_{tipo}',
        )
    # Filtramos las extraccion seleccionadas
    tipo_extraccion_seleccionada = [tipo for tipo, seleccionado in seleccion_checkbox.items() if seleccionado]

    # Devolvemos la nueva lista de categorías seleccionadas.
    return paises_seleccionados, categorias_seleccionadas, moneda_seleccionada, periodo_seleccionado, tipo_extraccion_seleccionada, tipo_fuente_seleccionadaente

def mostrar_kpis(df, moneda, periodo):
    """
    Calcula y muestra las métricas clave (KPIs) con un diseño personalizado
    que incluye íconos y se integra con el CSS.
    """
    st.header("Vista General del Mercado (Filtrada)")

    # --- 1. Cálculos (sin cambios) ---
    total_ofertas = len(df)
    salario_promedio = df['salario_anual_usd'].mean()
    puesto_comun = df['puesto_trabajo'].mode()[0] if not df['puesto_trabajo'].empty else "N/A"
    pais_principal = df['pais'].mode()[0] if not df['pais'].empty else "N/A"

    salario_display = salario_promedio
    if periodo == 'Mensual':
        salario_display /= 12
    
    if moneda == 'PEN':
        salario_display *= TIPO_DE_CAMBIO_USD_PEN
        simbolo_moneda = "S/"
    else:
        simbolo_moneda = "$"
    
    # --- 2. Íconos SVG (ligeros y personalizables) ---
    # Usamos SVG directamente para no depender de URLs externas.
    icon_ofertas = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-4.44a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.84a2 2 0 0 0-.59-1.42l-4.44-4.44a2 2 0 0 0-1.42-.58z"/><path d="M18 18h-6"/><path d="M18 14h-6"/><path d="M18 10h-6"/></svg>'
    icon_salario = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
    icon_puesto = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 5 4 4"/><path d="M17.45 2.55a1 1 0 0 1 1.41 0l1.59 1.59a1 1 0 0 1 0 1.41l-9 9L2 22l7.45-2.55 9-9z"/></svg>'
    icon_pais = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>'

    # --- 3. Renderizado con HTML y CSS ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="color: var(--color-acento-primario);">{icon_ofertas}</div>
                <div>
                    <p style="font-size: 0.9rem; color: var(--color-texto-secundario); margin: 0;">Total de Ofertas</p>
                    <p style="font-size: 1.5rem; font-weight: 600; margin: 0;">{total_ofertas:,}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="color: var(--color-acento-primario);">{icon_salario}</div>
                <div>
                    <p style="font-size: 0.9rem; color: var(--color-texto-secundario); margin: 0;">Salario Promedio {periodo}</p>
                    <p style="font-size: 1.5rem; font-weight: 600; margin: 0;">{simbolo_moneda}{salario_display:,.0f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="color: var(--color-acento-primario);">{icon_puesto}</div>
                <div>
                    <p style="font-size: 0.9rem; color: var(--color-texto-secundario); margin: 0;">Puesto Más Común</p>
                    <p style="font-size: 1.5rem; font-weight: 600; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{puesto_comun}">{puesto_comun}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="color: var(--color-acento-primario);">{icon_pais}</div>
                <div>
                    <p style="font-size: 0.9rem; color: var(--color-texto-secundario); margin: 0;">País Principal</p>
                    <p style="font-size: 1.5rem; font-weight: 600; margin: 0;">{pais_principal}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def cargar_habilidades_aprendizaje(ruta_csv_habilidades):
    """
    Carga las habilidades y sus URLs desde un archivo CSV.
    Maneja correctamente múltiples habilidades por fila, separadas por comas.
    """
    try:
        df_habilidades = pd.read_csv(ruta_csv_habilidades)
        # Asignamos nombres de columna para evitar errores
        df_habilidades.columns = ['habilidad', 'url']
        
        diccionario_habilidades = {}
        
        for index, row in df_habilidades.iterrows():
            # Dividimos las habilidades que vienen separadas por coma
            habilidades_individuales = str(row.habilidad).split(',')
            for habilidad_ind in habilidades_individuales:
                # Limpiamos cada habilidad (quitamos espacios y a minúsculas)
                habilidad_limpia = habilidad_ind.strip().lower()
                if habilidad_limpia: # Nos aseguramos de que no esté vacía
                    # Si la habilidad ya existe, no la sobreescribimos
                    # (la primera URL encontrada para una habilidad tiene prioridad)
                    if habilidad_limpia not in diccionario_habilidades:
                        diccionario_habilidades[habilidad_limpia] = row.url
                        
        return diccionario_habilidades
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de habilidades en: {ruta_csv_habilidades}")
        return {}
    except Exception as e:
        st.error(f"Error al procesar el archivo de habilidades: {e}")
        return {}


diccionario_habilidades = cargar_habilidades_aprendizaje(os.path.join('datos', 'conocimiento_filtrado_habilidades.csv'))
print(diccionario_habilidades)

def mostrar_feed_recomendaciones(df_filtrado, moneda, periodo, habilidades_usuario):
    """
    Analiza el DataFrame filtrado basado en las habilidades del usuario,
    y muestra un feed con las ofertas de trabajo más relevantes.
    """
    st.header("Principales empleos que te recomendamos")
    st.write("En función de las habilidades que registraste, estas son algunas de las ofertas más relevantes para ti en la selección actual.")

    # Si el usuario no ha registrado habilidades, no mostramos nada.
    if not habilidades_usuario:
        st.info("Registra tus habilidades en la pantalla de bienvenida para ver recomendaciones personalizadas.")
        return

    # --- Lógica de Coincidencia de Habilidades ---
    def calcular_relevancia(titulo_puesto, skills_usuario):
        if not isinstance(titulo_puesto, str):
            return 0
        # Contamos cuántas de las habilidades del usuario aparecen en el título del puesto.

        score = sum(1 for skill in skills_usuario if skill.lower() in titulo_puesto.lower()) 
        return score

    # Creamos una copia para no modificar el DataFrame original.
    df_recomendados = df_filtrado.copy()
    df_recomendados['relevancia'] = df_recomendados['puesto_trabajo'].apply(
        lambda x: calcular_relevancia(x, habilidades_usuario)
    )
    
    # Filtramos por ofertas que tengan al menos una coincidencia y ordenamos por relevancia.
    df_recomendados = df_recomendados[df_recomendados['relevancia'] > 0].sort_values(
        by=['relevancia', 'salario'], ascending=[False, False]
    )

    if df_recomendados.empty:
        st.warning("No encontramos ofertas que coincidan directamente con tus habilidades en la selección actual. ¡Intenta con otros filtros!")
        return

    # --- Visualización del Feed ---
    # Mostramos hasta 4 recomendaciones en tarjetas.
    num_recomendaciones_a_mostrar = min(len(df_recomendados), 4)
    
    # Creamos columnas para cada tarjeta.
    cols = st.columns(num_recomendaciones_a_mostrar)
    for i in range(num_recomendaciones_a_mostrar):
        with cols[i]:
            # Usamos un contenedor con borde para simular una "tarjeta".
            with st.container(border=True):
                oferta = df_recomendados.iloc[i]
                
                st.markdown(f"**{oferta['puesto_trabajo']}**")
                st.caption(f"{oferta['nombre_empresa']} • {oferta['pais']}, {oferta['region_estado']}")
                # Mostramos la fuente extraccion y plataforma de origen.
                st.caption(f"Fuente: {oferta['tipo_fuente_datos']} - {oferta['plataforma_origen']}")
                # Mostramos el salario con el símbolo de la moneda.
                salario_display = oferta['salario_anual_usd']
                if pd.notna(salario_display):
                    if periodo == 'Mensual':
                        salario_display /= 12
                    if moneda == 'PEN':
                        salario_display *= TIPO_DE_CAMBIO_USD_PEN
                    simbolo_moneda = "S/" if moneda == 'PEN' else "$"
                    st.caption(f"**Salario:** {simbolo_moneda}{salario_display:,.0f}")

                # Añadimos un pequeño espacio.
                st.markdown("---", help=None)

                # Preparamos los enlaces
                link_ver_oferta = f"<a href='{oferta['enlace_oferta']}' target='_blank' class='card-link'>Ver Oferta →</a>"
                
                habilidades_para_aprender = encontrar_habilidades_relevantes(
                oferta['puesto_trabajo'], 
                diccionario_habilidades
                )

                html_enlaces_aprender = ""
                if habilidades_para_aprender:
                    enlaces = []
                    for nombre_habilidad, url_habilidad in habilidades_para_aprender:
                        enlaces.append(
                            f"<a href='{url_habilidad}' target='_blank' class='card-link'>Aprender {nombre_habilidad} 🎓</a>"
                        )
                    # Unimos los enlaces con un separador para que se vean bien
                    html_enlaces_aprender = " • ".join(enlaces)

                    # Preparamos el enlace de la oferta
                    link_ver_oferta = f"<a href='{oferta['enlace_oferta']}' target='_blank' class='card-link'>Ver Oferta →</a>"

                    # Renderizamos los enlaces en la tarjeta
                    st.markdown(f"""
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex-grow: 1;'>{html_enlaces_aprender}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown(link_ver_oferta, unsafe_allow_html=True)
                else:
                    # Si no hay habilidad, solo mostramos el enlace de la oferta
                    st.markdown(link_ver_oferta, unsafe_allow_html=True)
            


    # --- Botón para Ver Todas las Ofertas ---
    if len(df_recomendados) > num_recomendaciones_a_mostrar:
        st.markdown("") # Espacio
        # Aquí iría la lógica para cambiar a una nueva "página" o vista.
        logica_boton_ver_todo(df_recomendados)

def mostrar_pagina_completa_recomendaciones(moneda, periodo):
    """
    Dibuja una "página" dedicada a mostrar la lista completa de ofertas
    recomendadas en formato de tarjetas y con paginación.
    """
    st.title("📄 Todas las Ofertas Recomendadas para tu Perfil")
    
    # Botón para regresar al dashboard principal.
    if st.button("← Volver al Dashboard Principal", key="volver_dashboard"):
        st.session_state.view = 'main_dashboard'
        st.rerun()

    # Recuperamos el DataFrame completo que guardamos en el estado de la sesión.
    df_completas = st.session_state.get('ofertas_recomendadas_completas', pd.DataFrame())

    if not df_completas.empty:
        st.write(f"Hemos encontrado {len(df_completas)} ofertas que coinciden con tus habilidades. ¡Explóralas!")
        
        # --- Lógica de Paginación ---
        items_por_pagina = 12
        total_paginas = -(-len(df_completas) // items_por_pagina) # División de techo
        
        # Inicializamos la página actual en el estado de la sesión si no existe.
        if 'pagina_actual_recs' not in st.session_state:
            st.session_state.pagina_actual_recs = 1
            
        pagina_actual = st.session_state.pagina_actual_recs

        # Calculamos los índices de inicio y fin para la página actual.
        start_idx = (pagina_actual - 1) * items_por_pagina
        end_idx = start_idx + items_por_pagina
        
        # Obtenemos solo las ofertas para la página actual.
        df_pagina = df_completas.iloc[start_idx:end_idx]

        # --- Visualización en Tarjetas ---
        # Creamos 4 columnas para un layout de 4x3.
        for i in range(0, len(df_pagina), 4):
            cols = st.columns(4)
            # Obtenemos un subconjunto de 4 ofertas para esta fila.
            fila_ofertas = df_pagina.iloc[i:i+4]
            
            for col_idx, (row_idx, oferta) in enumerate(fila_ofertas.iterrows()):
                with cols[col_idx]:
                    with st.container(border=True):
                        st.markdown(f"**{oferta['puesto_trabajo']}**")
                        st.caption(f"{oferta['nombre_empresa']} • {oferta['pais']}, {oferta['region_estado']}")
                        st.caption(f"Fuente: {oferta['tipo_fuente_datos']} - {oferta['plataforma_origen']}")
                        
                        salario_display = oferta['salario_anual_usd']
                        if pd.notna(salario_display):
                            if periodo == 'Mensual':
                                salario_display /= 12
                            if moneda == 'PEN':
                                salario_display *= TIPO_DE_CAMBIO_USD_PEN
                            simbolo_moneda = "S/" if moneda == 'PEN' else "$"
                            st.caption(f"**Salario:** {simbolo_moneda}{salario_display:,.0f}")

                        st.markdown("---", help=None)
                        st.markdown(
                            f"<a href='{oferta['enlace_oferta']}' target='_blank' style='text-decoration: none; color: #60a5fa;'>Ver Oferta →</a>", 
                            unsafe_allow_html=True
                        )
        
        st.markdown("---")

        # --- Controles de Paginación ---
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])

        with col_pag1:
            if st.button("← Anterior", disabled=(pagina_actual == 1), key="btn_anterior_recs"):
                st.session_state.pagina_actual_recs -= 1
                st.rerun()
        
        with col_pag2:
            st.write(f"Página {pagina_actual} de {total_paginas}")

        with col_pag3:
            if st.button("Siguiente →", disabled=(pagina_actual >= total_paginas), key="btn_siguiente_recs"):
                st.session_state.pagina_actual_recs += 1
                st.rerun()

    else:
        st.warning("No hay datos de recomendaciones para mostrar. Vuelve al dashboard y prueba con otros filtros.")

def logica_boton_ver_todo(df_recomendados):
    """
    Muestra el botón "Ver todas las ofertas" y maneja el cambio de estado.
    """
    st.markdown("")
    if st.button("Ver todas las ofertas para mí", use_container_width=True, key="ver_todas_ofertas"):
        # 1. Guardamos el DataFrame completo en el estado de la sesión.
        st.session_state.ofertas_recomendadas_completas = df_recomendados
        # 2. Cambiamos el estado de la vista para mostrar la nueva "página".
        st.session_state.view = 'all_recommendations'
        # 3. Forzamos un re-run del script para que se cargue la nueva vista.
        st.rerun()

def mostrar_analisis_geografico(df, paises_seleccionados):
    """Muestra el mapa mundial o el gráfico de barras de regiones según la selección."""
    st.header("Análisis Geográfico: ¿Dónde están las Oportunidades?")
    col1, col2 = st.columns(spec=[0.7,0.3])


    if len(paises_seleccionados) == 0:
        st.info("Selecciona al menos un país en el filtro para ver el análisis geográfico.")
        return
    def mapa_paises():
            ofertas_por_pais = df['pais'].value_counts().reset_index()
            ofertas_por_pais.columns = ['pais', 'numero_de_ofertas']

            # Creamos un diccionario para "traducir" los nombres de los países
            mapa_nombres_paises = {
                'Perú': 'Peru',
                'US': 'United States',
                'México': 'Mexico',
            }
        
            # Reemplazamos los nombres en la columna 'pais' usando el diccionario.
            ofertas_por_pais['pais_mapeado'] = ofertas_por_pais['pais'].replace(mapa_nombres_paises)

            fig_mapa = px.choropleth(ofertas_por_pais, 
                                    # Usamos la nueva columna con los nombres corregidos
                                    locations="pais_mapeado", 
                                    locationmode="country names",
                                    color="numero_de_ofertas", 
                                    # Mostramos el nombre original en el hover para claridad
                                    hover_name="pais", 
                                    color_continuous_scale=px.colors.sequential.Plasma,
                                    title="Distribución de Ofertas por País")
            st.plotly_chart(fig_mapa, use_container_width=True)
    def mapa_regiones(pais):
        # Gráfico 2: Top 10 regiones combinadas de los países seleccionados
            df_paises = df[df['pais'].isin(paises_seleccionados)].copy()
            # Creamos una columna combinada para el gráfico (ej: "Lima, Perú")
            df_paises['region_pais'] = df_paises['region_estado'].astype(str) + ", " + df_paises['pais'].astype(str)
            
            ofertas_combinadas = df_paises['region_pais'].value_counts().nlargest(10).sort_values()

            if not ofertas_combinadas.empty:
                fig_combinada = px.bar(
                    ofertas_combinadas,
                    x=ofertas_combinadas.values,
                    y=ofertas_combinadas.index,
                    orientation='h',
                    labels={'x': 'Número de Ofertas', 'y': 'Región'},
                    title="Top 10 Regiones (Combinadas)",
                    text=ofertas_combinadas.values
                )
                fig_combinada.update_traces(texttemplate='%{text}', textposition='outside')
                fig_combinada.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_combinada, use_container_width=True)
            else:
                st.info("No hay datos de regiones para los países seleccionados.")
    
    with col1:
        st.subheader("Mapa Mundial de Oportunidades")
        mapa_paises()
    with col2:
        st.subheader("Distribución de Ofertas por País")
        mapa_regiones(paises_seleccionados)

def mostrar_demanda_por_categoria(df):
    """
    Calcula y muestra un gráfico de barras con las categorías de puestos más demandadas,
    utilizando una escala de color para representar la magnitud.
    """
    st.subheader("Demanda por Categoría de Puesto")

    # Contamos la frecuencia de cada categoría y tomamos el top 15.
    demanda_categorias = df['categoria'].value_counts().nlargest(15).sort_values()

    if not demanda_categorias.empty:
        # Creamos la figura del gráfico de barras horizontales.
        fig = px.bar(
            demanda_categorias,
            x=demanda_categorias.values,
            y=demanda_categorias.index,
            orientation='h',
            labels={'x': 'Número de Ofertas', 'y': 'Categoría'},
            text=demanda_categorias.values,
            title="Top 15 Categorías con Mayor Demanda",
            color=demanda_categorias.values, # Coloreamos según la magnitud de la demanda
            color_continuous_scale='Tealgrn'
        )
        
        # Configuramos el gráfico para que sea más legible.
        fig.update_layout(
            # Ocultamos la barra de escala de color para un look más limpio.
            coloraxis_showscale=False,
            yaxis={'categoryorder':'total ascending'}
        )
        
        # Actualizamos el texto para que sea visible y se posicione correctamente.
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        # Mostramos el gráfico en el dashboard.
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para mostrar el gráfico de demanda por categoría.")

def mostrar_demanda_vs_salario(df, moneda_seleccionada, periodo_seleccionado, tipo_cambio):
    st.header("🎯 Análisis: Demanda vs. Salario")

    # 1. Agregamos los datos por categoría
    #    Contamos el número de ofertas y calculamos el salario promedio para cada una.
    analisis_categorias = df.groupby('categoria').agg(
        numero_de_ofertas=('puesto_trabajo', 'count'),
        salario_promedio_usd=('salario_anual_usd', 'mean')
    ).reset_index()

    # Filtramos para quedarnos con categorías que tengan un número mínimo de ofertas (ej: más de 5)
    # para que el promedio de salario sea significativo.
    analisis_categorias = analisis_categorias[analisis_categorias['numero_de_ofertas'] > 5]

    if not analisis_categorias.empty:
        # --- Lógica de conversión para la visualización ---
        df_display = analisis_categorias.copy()
        salario_col_display = 'salario_promedio_usd'
        
        if periodo_seleccionado == 'Mensual':
            df_display[salario_col_display] = df_display[salario_col_display] / 12
        
        if moneda_seleccionada == 'PEN':
            df_display[salario_col_display] = df_display[salario_col_display] * tipo_cambio
        
        simbolo_moneda = "S/" if moneda_seleccionada == 'PEN' else "$"
        label_eje_y = f"Salario Promedio {periodo_seleccionado} ({moneda_seleccionada})"

        fig = px.scatter(
            df_display,
            x="numero_de_ofertas",
            y=salario_col_display,
            size="numero_de_ofertas",  # El tamaño de la burbuja también representa la demanda
            color="categoria",         # Cada categoría tiene un color diferente
            opacity=0.23,             # Opacidad para que las burbujas se vean mejor
            hover_name="categoria",    # Muestra el nombre de la categoría al pasar el mouse
            text="categoria",          # Muestra el nombre directamente en el punto
            log_x=True,                # Usamos escala logarítmica en X para manejar grandes diferencias en demanda
            size_max=60,               # Tamaño máximo de las burbujas
            labels={
                "numero_de_ofertas": "Demanda (Nº de Ofertas)",
                "salario_promedio_usd": label_eje_y
            },
            #title="Análisis de Oportunidad: Demanda vs. Compensación por Categoría"
        )

        # 3. Configuramos el gráfico para que sea más legible
        fig.update_traces(textposition='top center')
        fig.update_layout(
            showlegend=False,
            yaxis_title=label_eje_y,
            xaxis_title="Demanda (Nº de Ofertas) - Escala Logarítmica"
        )
        
        # Formateamos el eje Y para que muestre el símbolo de la moneda
        fig.update_yaxes(tickprefix=simbolo_moneda, tickformat=",.0f")

        # 4. Mostramos el gráfico en el dashboard
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para generar el gráfico de dispersión. Intenta con otros filtros.")

def mostrar_seccion_descarga(df_filtrado):
    st.header("📥 Descargar Datos")
    st.write("Haz clic en el botón para descargar los datos actualmente filtrados en formato .csv.")

    # Convertimos el DataFrame a formato CSV en memoria.
    # Es importante usar to_csv() con index=False para no incluir el índice de pandas en el archivo.
    # Lo codificamos en UTF-8 para asegurar la compatibilidad con caracteres especiales (tildes, etc.).
    csv = df_filtrado.to_csv(index=False).encode('utf-8')

    # Creamos el botón de descarga. Streamlit se encarga de la magia.
    st.download_button(
        label="Descargar Datos (.csv)",
        data=csv,
        file_name='datos_filtrados_mercado_laboral.csv',
        mime='text/csv',
    )

def mostrar_salario_por_categoria(df, moneda_seleccionada, periodo_seleccionado, tipo_cambio):
    st.subheader(f"Distribución de Salarios por Categoría ({moneda_seleccionada} - {periodo_seleccionado})")

    # Para que el gráfico sea legible, nos enfocamos en las 10 categorías con más ofertas.
    top_10_categorias = df['categoria'].value_counts().nlargest(10).index
    df_top_categorias = df[df['categoria'].isin(top_10_categorias)]

    if not df_top_categorias.empty:
        # Hacemos una copia para no modificar el DataFrame original.
        df_display = df_top_categorias.copy()

        # --- Lógica de conversión para la visualización ---
        salario_columna_display = 'salario_anual_usd'
        if periodo_seleccionado == 'Mensual':
            salario_columna_display = 'salario_mensual_display'
            df_display[salario_columna_display] = df_display['salario_anual_usd'] / 12
        
        if moneda_seleccionada == 'PEN':
            df_display[salario_columna_display] = df_display[salario_columna_display] * tipo_cambio

        # Creamos el gráfico de cajas.
        fig = px.box(
            df_display,
            x='categoria',
            y=salario_columna_display,
            color='categoria',
            labels={'categoria': 'Categoría del Puesto', 'salario_anual_usd': f'Salario {periodo_seleccionado} ({moneda_seleccionada})'},
            title="Rango de Salarios para las Categorías Top"
        )
        # Ocultamos la leyenda para un look más limpio.
        fig.update_layout(showlegend=False)
        
        # Mostramos el gráfico en el dashboard.
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para mostrar el gráfico de salarios por categoría.")

def mostrar_tabla_de_datos(df, moneda, periodo):
    """Muestra la tabla de datos filtrada con la conversión de moneda y periodo aplicada."""
    st.subheader("Vista Previa de los Datos Filtrados")
    
    df_display = df.copy()
    
    df_display['salario_display'] = df_display['salario_anual_usd']
    if periodo == 'Mensual':
        df_display['salario_display'] /= 12
    
    simbolo = "S/" if moneda == 'PEN' else "$"
    if moneda == 'PEN':
        df_display['salario_display'] *= TIPO_DE_CAMBIO_USD_PEN

    df_display['salario_display'] = df_display['salario_display'].map(lambda x: f"{simbolo}{x:,.0f}" if pd.notna(x) else "N/A")
    
    columnas_a_mostrar = (
        'puesto_trabajo', 'nombre_empresa', 'pais', 'region_estado', 
        'salario_display', 'tipo_contrato', 'categoria', 
        'plataforma_origen', 'tipo_fuente_datos', 'enlace_oferta'
    )
    st.data_editor(
                    df_display,
                    column_config={
                        "enlace_oferta": st.column_config.LinkColumn(
                            "Link a la Oferta", # El título que se mostrará en la cabecera de la columna.
                            display_text="Ver Oferta" # El texto que se mostrará en cada celda.
                        )
                    },
                    # Definimos las columnas que queremos mostrar y su orden.
                    column_order=columnas_a_mostrar,
                    hide_index=True, # Ocultamos el índice de pandas.
                    use_container_width=True # Hacemos que la tabla use todo el ancho del contenedor.
                )

def encontrar_habilidades_relevantes(titulo_puesto, diccionario_habilidades):
    if not isinstance(titulo_puesto, str):
        return []

    titulo_lower = titulo_puesto.lower()
    habilidades_encontradas = []

    # Iteramos sobre todas las habilidades de nuestro diccionario
    for habilidad, url in diccionario_habilidades.items():
        # Usamos una expresión regular más flexible que busca la habilidad
        # incluso si está junto a paréntesis, comas, etc.
        # re.escape maneja habilidades con caracteres especiales como 'c++'.
        patron = r'\b' + re.escape(habilidad) + r'\b'
        if re.search(patron, titulo_lower):
            # Añadimos la habilidad y su URL a nuestra lista de resultados
            habilidades_encontradas.append((habilidad.title(), url))

    return habilidades_encontradas


# Estilos
def inyectar_estilos_css(archivo_css):
    try:
        with open(archivo_css) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: No se pudo encontrar el archivo CSS en la ruta: {archivo_css}")

# ---  Principal de la Aplicación ---

st.title("Análisis del Mercado Laboral Global")
st.write("Una vista interactiva de las tendencias y oportunidades en el sector tecnológico.")

inyectar_estilos_css('source/dashboard/styles.css')

ruta_dataset = os.path.join('datos', 'finales', 'dataset_maestro_final.csv')
df_original = cargar_y_preprocesar_datos(ruta_dataset)

habilidades_del_usuario = None
if df_original is not None:
    # 1. Mostrar la barra lateral y obtener los filtros del usuario.
    paises, categorias, moneda, periodo, extraccion, fuente  = mostrar_sidebar(df_original)

    # 2. Filtrar el DataFrame principal según la selección.
    df_filtrado = df_original.copy()
    
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categorias)]
    if paises:
        df_filtrado = df_filtrado[df_filtrado['pais'].isin(paises)]
    if extraccion:
        df_filtrado = df_filtrado[df_filtrado['tipo_fuente_datos'].isin(extraccion)]
    if fuente:
        df_filtrado = df_filtrado[df_filtrado['plataforma_origen'].isin(fuente)]


    # 3. Mostrar los componentes del dashboard con los datos ya filtrados.
    if not df_filtrado.empty:
        if 'view' not in st.session_state:
            st.session_state.view = 'main_dashboard'
        if st.session_state.view == 'main_dashboard':
            mostrar_kpis(df_filtrado, moneda, periodo)
            st.markdown("---")
            habilidades_del_usuario = mostrar_pantalla_registro()
            if habilidades_del_usuario:
                mostrar_feed_recomendaciones(df_filtrado, moneda, periodo, habilidades_del_usuario)
                st.markdown("---")
            # mostrar_buscador_ofertas
            mostrar_buscador_ofertas(df_filtrado, moneda, periodo, TIPO_DE_CAMBIO_USD_PEN, diccionario_habilidades)
            st.markdown("---")
            mostrar_analisis_geografico(df_filtrado, paises)
            st.markdown("---")
            # Mostramos el análisis por categoría de puesto.
            st.header("Análisis por Categoría de Puesto")
            # Creamos dos columnas para poner los gráficos uno al lado del otro.
            col_demanda, col_salario = st.columns(2)
            with col_demanda:
                mostrar_demanda_por_categoria(df_filtrado)
            with col_salario:
                mostrar_salario_por_categoria(df_filtrado, moneda, periodo, TIPO_DE_CAMBIO_USD_PEN)
            st.markdown("---")
            # Simplemente llamas a la función en la nueva sección de tu dashboard.
            mostrar_demanda_vs_salario(df_filtrado, moneda, periodo, TIPO_DE_CAMBIO_USD_PEN)
            st.markdown("---")
            mostrar_asesor_perfil(df_filtrado, moneda, periodo, TIPO_DE_CAMBIO_USD_PEN, paises)
            st.markdown("---")
            mostrar_generador_rutas()
            # Si el usuario no ha registrado sus habilidades, mostramos la pantalla de registro.

            st.markdown("---")
            mostrar_tabla_de_datos(df_filtrado, moneda, periodo)
            # Mostrar todas nuestras fuentes csv
            st.markdown("---")
            df_empleos_sugeridos = mostrar_seccion_descarga(df_filtrado)
        # --- NUEVO: Manejo de la vista de "Ver todas las ofertas para mí" ---
        elif st.session_state.view == 'all_recommendations':
            # Si el usuario ha hecho clic en "Ver todas las ofertas para mí", mostramos la página completa.
            mostrar_pagina_completa_recomendaciones(moneda, periodo)
    else:
        st.warning("No se encontraron resultados para los filtros seleccionados. Por favor, ajusta tu búsqueda.")
else:
    st.error("No se pudieron cargar los datos iniciales.")


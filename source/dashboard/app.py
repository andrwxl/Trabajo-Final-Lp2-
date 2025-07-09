import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.express as px
import comparador_de_perfiles as comparador
from gemini_funciones.asesor_perfil import mostrar_asesor_perfil

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Mercado Laboral",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constantes ---
TIPO_DE_CAMBIO_USD_PEN = 3.75

# --- Funciones de Carga y Procesamiento ---

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
        
        for col in ['salario_minimo', 'salario_maximo']:
             if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['salario_anual_base'] = np.where(df['periodo_salario'] == 'Mensual', df['salario_maximo'] * 12, df['salario_maximo'])
        df['salario_anual_usd'] = np.where(df['moneda_salario'] == 'PEN', df['salario_anual_base'] / TIPO_DE_CAMBIO_USD_PEN, df['salario_anual_base'])
        return df
    except Exception as e:
        st.error(f"Error al cargar o procesar el archivo CSV: {e}")
        return None

# --- Funciones de Componentes del Dashboard ---

def mostrar_sidebar(df):
    """
    Muestra la barra lateral de filtros y devuelve las selecciones del usuario.
    Ahora filtra por 'categoria' y permite selección múltiple.
    """
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

    

    # --- Filtro de Salario (sin cambios) ---
    salario_min = int(df['salario_anual_usd'].fillna(0).min())
    salario_max = int(df['salario_anual_usd'].fillna(0).max())
    
    rango_salario = st.sidebar.slider(
        'Rango Salarial (Anual en USD)', 
        min_value=salario_min, 
        max_value=salario_max, 
        value=(salario_min, salario_max)
    )

    # --- Filtros de Moneda y Periodo (sin cambios) ---
    moneda_seleccionada = st.sidebar.radio("Ver Salario en:", ('PEN', 'USD'), index=0, horizontal=True)
    periodo_seleccionado = st.sidebar.radio("Ver Periodo Salarial:", ('Anual', 'Mensual'), index=0, horizontal=True)
    
    # Filtro por tipo de fuente
    tipo_fuente_disponible = sorted(df['tipo_fuente_datos'].dropna().unique())

    st.sidebar.subheader("Tipo de Fuente de Datos")
    seleccion_checkbox = {}
    for tipo in tipo_fuente_disponible:
        seleccion_checkbox[tipo] =  st.sidebar.checkbox(
            tipo,
            value=True,
            key=f'tipo_fuente_{tipo}',
        )
    # Filtramos las fuentes seleccionadas
    tipo_fuente_seleccionada = [tipo for tipo, seleccionado in seleccion_checkbox.items() if seleccionado]

    # Devolvemos la nueva lista de categorías seleccionadas.
    return paises_seleccionados, categorias_seleccionadas, rango_salario, moneda_seleccionada, periodo_seleccionado, tipo_fuente_seleccionada

def mostrar_kpis(df, moneda, periodo):
    """Calcula y muestra las métricas clave (KPIs) en la parte superior."""
    st.header("Vista General del Mercado (Filtrada)")

    total_ofertas = len(df)
    salario_promedio_anual_usd = df['salario_anual_usd'].mean()
    tecnologia_demandada = df['puesto_trabajo'].mode()[0] if not df['puesto_trabajo'].empty else "N/A"
    pais_con_mas_ofertas = df['pais'].mode()[0] if not df['pais'].empty else "N/A"

    salario_display = salario_promedio_anual_usd
    if periodo == 'Mensual':
        salario_display /= 12
    
    if moneda == 'PEN':
        salario_display *= TIPO_DE_CAMBIO_USD_PEN
        simbolo_moneda = "S/"
    else:
        simbolo_moneda = "$"
    
    label_salario = f"Salario Promedio {periodo} ({moneda})"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total de Ofertas", value=f"{total_ofertas:,}")
    col2.metric(label=label_salario, value=f"{simbolo_moneda}{salario_display:,.0f}")
    col3.metric(label="Puesto Más Común", value=tecnologia_demandada)
    col4.metric(label="País Principal", value=pais_con_mas_ofertas)

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
                # 'España': 'Spain',
                # 'México': 'Mexico',
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
    Calcula y muestra un gráfico de barras con las categorías de puestos más demandadas.
    
    Args:
        df (pd.DataFrame): El DataFrame filtrado con los datos de las ofertas.
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
            title="Top 15 Categorías con Mayor Demanda"
        )
        # Configuramos el gráfico para que sea más legible.
        fig.update_layout(
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        # Mostramos el gráfico en el dashboard.
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para mostrar el gráfico de demanda por categoría.")
# --- Función para la Sección de Descarga ---
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
# --- Función para Gráfico de Salario por Categoría ---

def mostrar_salario_por_categoria(df, moneda_seleccionada, periodo_seleccionado, tipo_cambio):
    """
    Calcula y muestra un gráfico de cajas (boxplot) con la distribución de salarios
    para las categorías más demandadas.
    
    Args:
        df (pd.DataFrame): El DataFrame filtrado.
        moneda_seleccionada (str): La moneda elegida por el usuario ('PEN' o 'USD').
        periodo_seleccionado (str): El periodo elegido ('Anual' o 'Mensual').
        tipo_cambio (float): La tasa de conversión de USD a PEN.
    """
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
    
    columnas_a_mostrar = [
        'puesto_trabajo', 'nombre_empresa', 'pais', 'region_estado', 
        'salario_display', 'tipo_contrato', 'categoria', 
        'plataforma_origen', 'tipo_fuente_datos', 'enlace_oferta'
    ]
    st.dataframe(df_display[columnas_a_mostrar])

# --- Flujo Principal de la Aplicación ---

st.title("📊 Análisis del Mercado Laboral Global")
st.write("Una vista interactiva de las tendencias y oportunidades en el sector tecnológico.")

ruta_dataset = os.path.join('datos', 'finales', 'dataset_maestro_final.csv')
df_original = cargar_y_preprocesar_datos(ruta_dataset)

if df_original is not None:
    # 1. Mostrar la barra lateral y obtener los filtros del usuario.
    paises, categorias, salario, moneda, periodo, fuente = mostrar_sidebar(df_original)

    # 2. Filtrar el DataFrame principal según la selección.
    df_filtrado = df_original.copy()
    
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categorias)]
    if paises:
        df_filtrado = df_filtrado[df_filtrado['pais'].isin(paises)]
    if fuente:
        df_filtrado = df_filtrado[df_filtrado['tipo_fuente_datos'].isin(fuente)]

    df_filtrado = df_filtrado[
        (df_filtrado['salario_anual_usd'].fillna(salario[0]) >= salario[0]) & 
        (df_filtrado['salario_anual_usd'].fillna(salario[1]) <= salario[1])
    ]

    # 3. Mostrar los componentes del dashboard con los datos ya filtrados.
    if not df_filtrado.empty:
        mostrar_kpis(df_filtrado, moneda, periodo)
        st.markdown("---")
        mostrar_analisis_geografico(df_filtrado, paises)
        st.markdown("---")
        st.header("Análisis por Categoría de Puesto")
        # Creamos dos columnas para poner los gráficos uno al lado del otro.
        col_demanda, col_salario = st.columns(2)
        with col_demanda:
            mostrar_demanda_por_categoria(df_filtrado)
        with col_salario:
            mostrar_salario_por_categoria(df_filtrado, moneda, periodo, TIPO_DE_CAMBIO_USD_PEN)
        st.markdown("---")
        mostrar_asesor_perfil(df_filtrado, moneda, periodo, TIPO_DE_CAMBIO_USD_PEN, paises)


        # AL FINAL, mostramos la tabla de datos filtrados.
        mostrar_tabla_de_datos(df_filtrado, moneda, periodo)
        st.markdown("---")
        df_empleos_sugeridos = mostrar_seccion_descarga(df_filtrado)
        st.dataframe(df_empleos_sugeridos)
    else:
        st.warning("No se encontraron resultados para los filtros seleccionados. Por favor, ajusta tu búsqueda.")
else:
    st.error("No se pudieron cargar los datos iniciales.")


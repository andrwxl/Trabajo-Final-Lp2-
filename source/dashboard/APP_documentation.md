🏛️ Documentación del Dashboard: Atlas de Oportunidades Laborales
Este documento desglosa la arquitectura, la lógica y el funcionamiento del script app.py, la aplicación principal construida con Streamlit que sirve como la interfaz visual e interactiva para todo el ecosistema del "Atlas de Oportunidades Laborales". Esta no es solo una página de visualización, sino una aplicación web de datos completa, diseñada para ser el punto de encuentro entre el análisis de mercado y el desarrollo profesional del usuario.

# 1. Propósito y Visión General
El app.py es el destino final y la cara visible de nuestro complejo pipeline de datos. Su misión principal es transformar los archivos CSV masivos y estáticos, generados por el scraper y el clasificador, en una experiencia de usuario intuitiva, interactiva, personalizada y, sobre todo, accionable. El dashboard va más allá de simplemente mostrar gráficos; busca empoderar al usuario. Permite a estudiantes, profesionales en transición y desarrolladores experimentados explorar la demanda de habilidades, comparar salarios entre regiones, encontrar ofertas de trabajo relevantes y, en un paso que cierra el ciclo, conectar esas oportunidades con los recursos educativos necesarios para adquirirlas y crecer profesionalmente. En esencia, responde no solo al "¿Qué se busca?", sino también al "¿Cómo lo consigo?".

# 2. Estructura y Componentes Clave
La aplicación está organizada en una serie de funciones modulares, cada una responsable de una parte específica de la interfaz de usuario (UI) o de la lógica de datos. Esta arquitectura de "separación de intereses" es fundamental para la mantenibilidad y escalabilidad del proyecto.

## Configuración Inicial e Imports
# --- Configuración de la Página ---
st.set_page_config(...)

# --- Imports y Conexiones ---
import streamlit as st
import pandas as pd
import plotly.express as px
from gemini_funciones.asesor_perfil import mostrar_asesor_perfil
# ...
import ETL.Cliente.tasa_cambios as tasa_cambios

st.set_page_config: Este es el primer comando de Streamlit que se debe ejecutar. Establece los metadatos globales de la página, como el título que aparece en la pestaña del navegador, el ícono (favicon) y, de manera crucial, el layout="wide". Esta configuración permite que el dashboard utilice todo el ancho de la pantalla, lo cual es esencial para visualizaciones de datos complejas y para un diseño de aspecto profesional.

Imports Estratégicos: La selección de imports revela la arquitectura modular del proyecto. Además de las librerías estándar de análisis de datos (pandas, plotly), el script se conecta con otros módulos del ecosistema:

gemini_funciones: Indica la integración de una capa de inteligencia artificial generativa. Estas funciones no son solo para visualización, sino para crear contenido nuevo y personalizado (consejos, rutas de aprendizaje) basado en los datos del usuario y del mercado.

ETL.Cliente.tasa_cambios: Este import demuestra que el dashboard es el consumidor final de un pipeline de Extracción, Transformación y Carga (ETL). En lugar de tener una tasa de cambio estática, la aplicación llama a un módulo dedicado que obtiene datos financieros actualizados, asegurando que la estandarización de salarios sea precisa y relevante.

# 3. El Flujo de Datos: De CSV a Dashboard
El corazón de la aplicación es su capacidad para cargar, procesar y visualizar datos de manera eficiente. Este flujo está optimizado para el rendimiento y la precisión.

## cargar_y_preprocesar_datos(ruta_archivo)
Propósito: Actúa como la puerta de entrada principal para los datos del mercado laboral. Su responsabilidad es cargar el dataset_maestro_final.csv, que es el producto consolidado de todo nuestro esfuerzo de scraping.

Inteligencia: Esta función es más que un simple pd.read_csv. Contiene lógica de pre-procesamiento vital:

Limpieza: Realiza una limpieza de datos fundamental, como eliminar espacios en blanco (.str.strip()) que pueden causar errores en los filtros, y convertir columnas a sus tipos de datos correctos (pd.to_numeric), manejando posibles errores de conversión.

Estandarización de Salarios: La creación de la columna salario_anual_usd es el paso más crítico. Esta columna se convierte en la "única fuente de verdad" para todos los cálculos y comparaciones salariales. La función toma salarios en diferentes monedas (PEN, USD) y periodos (Mensual, Anual) y los normaliza a un único estándar: el salario anual en dólares. Esto permite comparar de manera justa una oferta en Lima con una en Estados Unidos.

Cacheo (@st.cache_data): Esta anotación es la clave del rendimiento de la aplicación. Le indica a Streamlit que, la primera vez que esta función se ejecuta, debe guardar el DataFrame resultante en una caché de memoria. Para todas las interacciones posteriores del usuario (como cambiar un filtro en la barra lateral), Streamlit recuperará instantáneamente los datos de la caché en lugar de volver a leer y procesar el pesado archivo CSV desde el disco. Esto reduce los tiempos de carga de varios segundos a milisegundos.

## cargar_habilidades_aprendizaje(ruta_csv_habilidades)
Propósito: Esta función es el puente que conecta el análisis con la acción. Carga el archivo conocimiento_filtrado_habilidades.csv, que es el resultado de nuestro clasificador inteligente.

Funcionamiento: Su objetivo es crear un diccionario de Python que sirva como una tabla de búsqueda rápida, mapeando cada habilidad específica (ej. "python", "react", "cálculo") a la URL del mejor recurso educativo que nuestro scraper encontró. Este diccionario es el motor que alimenta la funcionalidad "Aprender 🎓" en las tarjetas de ofertas, haciendo del dashboard una herramienta de desarrollo profesional activo.

# 4. La Experiencia de Usuario: Componentes Interactivos
La aplicación está diseñada para ser altamente interactiva y personalizada, utilizando el session_state de Streamlit para crear una experiencia dinámica.

## dialogo_de_registro() y mostrar_pantalla_registro()
Propósito: Crear una experiencia de bienvenida y onboarding fluida y atractiva. El objetivo es obtener información clave del usuario desde el primer momento para personalizar el contenido.

Funcionamiento:

Utiliza st.dialog, una característica moderna de Streamlit, para mostrar una ventana emergente que no interrumpe el flujo de la página principal.

Dentro del diálogo, un st.multiselect actúa como un selector de etiquetas interactivo, permitiendo al usuario elegir sus habilidades de una lista curada.

Las habilidades seleccionadas se guardan en el st.session_state, que es el mecanismo de "memoria a corto plazo" de Streamlit. Este diccionario especial persiste entre las recargas de la página, permitiendo que la aplicación "recuerde" al usuario a lo largo de su sesión.

Una vez registradas, st.rerun() fuerza una recarga del script. Como las habilidades ya están en el session_state, el diálogo no vuelve a aparecer y el dashboard principal se renderiza con el contenido ya personalizado.

## mostrar_sidebar(df)
Propósito: Funciona como el "centro de control" del usuario, permitiéndole explorar y segmentar los datos a su gusto.

Funcionamiento: Crea la barra lateral y la puebla con widgets de filtro (multiselects, radios). Cada vez que un usuario interactúa con un widget, Streamlit detecta el cambio y vuelve a ejecutar el script app.py de arriba a abajo. La función mostrar_sidebar devuelve los valores actuales de todos los filtros, que se utilizan para segmentar el DataFrame principal antes de pasarlo a los componentes de visualización.

## mostrar_kpis(df, moneda, periodo)
Propósito: Ofrecer una vista de "ojo de pájaro" con las métricas más importantes de la selección de datos actual.

Funcionamiento: Calcula métricas clave (Total de Ofertas, Salario Promedio, etc.). Para ir más allá de los componentes básicos, utiliza HTML y SVG incrustados dentro de st.markdown. Esto permite un control total sobre el estilo (usando clases CSS) y el uso de íconos vectoriales ligeros, dando a la aplicación un aspecto más pulido y de producto final.

## mostrar_feed_recomendaciones(...) y mostrar_pagina_completa_recomendaciones(...)
Propósito: Es el motor de personalización y engagement del dashboard. Su objetivo es mostrar al usuario las ofertas que son más relevantes para él.

Funcionamiento:

Implementa un algoritmo de recomendación simple pero efectivo: cuenta cuántas de las habilidades del usuario (del session_state) aparecen en el título de cada oferta para generar un "score de relevancia".

Ordena las ofertas por este score (y secundariamente por salario) y muestra las 4 mejores en la página principal.

Para no abrumar la vista principal, ofrece un botón "Ver todas". Al hacer clic, este botón modifica una variable en el session_state (st.session_state.view = 'all_recommendations') y fuerza una recarga. El script, al detectar este nuevo estado, renderiza una "página" completamente nueva dedicada a mostrar todas las recomendaciones con su propia paginación.

## mostrar_buscador_ofertas(...)
Propósito: Darle al usuario el poder de la exploración libre, permitiéndole buscar cualquier término que le interese.

Funcionamiento:

Un st.text_input captura la búsqueda del usuario.

El DataFrame se filtra en tiempo real, buscando coincidencias en el título, la empresa o la categoría.

Integración Clave: Aquí es donde la magia ocurre. La función llama a encontrar_habilidades_relevantes para cada oferta. Si el título contiene una habilidad que existe en nuestro diccionario de conocimiento (cargado por cargar_habilidades_aprendizaje), el dashboard muestra dinámicamente un enlace "Aprender [Habilidad] 🎓". Este es el punto exacto donde los dos grandes pilares del proyecto (análisis de mercado y base de datos de conocimiento) convergen para crear un valor único.

# 5. Visualizaciones de Datos con Plotly
La aplicación utiliza plotly.express por su capacidad para crear gráficos interactivos, estéticamente agradables y que se integran perfectamente con Streamlit. Cada gráfico está diseñado para responder a una pregunta de negocio específica.

mostrar_analisis_geografico(...): Responde "¿Dónde están las oportunidades?". El mapa de coropletas (px.choropleth) ofrece una visión macro de la distribución global, mientras que el gráfico de barras de regiones permite una comparación más detallada entre ciudades específicas.

mostrar_demanda_por_categoria(...): Responde "¿Cuáles son los campos más populares?". El gráfico de barras horizontales es ideal para comparar categorías y se ordena automáticamente para mostrar las más demandadas en la parte superior.

mostrar_salario_por_categoria(...): Responde "¿Cuánto se puede ganar en cada campo?". El gráfico de cajas (px.box) es una herramienta de análisis muy potente porque muestra la distribución completa de los salarios: la mediana, los percentiles y los valores atípicos. Permite identificar roles donde, aunque la mediana no sea la más alta, existe un gran potencial de ingresos para los perfiles más altos.

mostrar_demanda_vs_salario(...): Responde a la pregunta estratégica más importante: "¿Dónde está la mejor oportunidad?". Este gráfico de dispersión (px.scatter) es la joya del análisis. Al mapear la demanda (eje X) contra la compensación (eje Y), permite identificar visualmente los "cuadrantes de oportunidad":

Cuadrante Superior Derecho: Alta demanda, alto salario (el "santo grial").

Cuadrante Inferior Derecho: Alta demanda, bajo salario (roles de entrada o muy competidos).

Cuadrante Superior Izquierdo: Baja demanda, alto salario (nichos de alta especialización).

Cuadrante Inferior Izquierdo: Baja demanda, bajo salario (roles menos atractivos).

# 6. Integración con IA Generativa
## mostrar_asesor_perfil(...) y mostrar_generador_rutas()
Propósito: Añadir una capa de inteligencia artificial avanzada y conversacional, transformando el dashboard de una herramienta de visualización a un asesor de carrera personal.

Funcionamiento: Estas funciones actúan como puntos de entrada a otro módulo del proyecto (gemini_funciones). La lógica probable es que toman el contexto actual (los datos filtrados en el dashboard y las habilidades del usuario), lo empaquetan en un "prompt" bien estructurado y lo envían a un modelo de lenguaje grande como Gemini. La respuesta del modelo, que puede ser un plan de carrera detallado, una lista de cursos recomendados con justificaciones, o consejos para mejorar el perfil, se muestra directamente en la interfaz, ofreciendo un valor añadido inmenso y personalizado.

# 7. Flujo Principal de la Aplicación
El script sigue un flujo de ejecución reactivo, típico de Streamlit, que se repite con cada interacción del usuario:

Se configura la página y se cargan los datos y estilos. El uso de @st.cache_data asegura que la carga de datos pesados solo ocurra una vez.

Se muestra la pantalla de registro si el session_state no contiene las habilidades del usuario.

Se renderiza la barra lateral, y sus valores actuales se usan para filtrar el DataFrame principal.

Se comprueba la variable st.session_state.view para decidir qué "página" o vista mostrar.

Si la vista es 'main_dashboard', se renderizan todos los componentes en orden: KPIs, recomendaciones, buscador, gráficos y la tabla de datos.

Si la vista es 'all_recommendations', se renderiza la página dedicada a ello, mostrando la lista completa de ofertas recomendadas con su propia paginación.

Si en algún punto los filtros aplicados resultan en un DataFrame vacío, se muestra un mensaje de advertencia am
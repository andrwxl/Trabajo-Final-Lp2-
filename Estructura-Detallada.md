## 📊 Diagrama de Flujo del Proceso ETL y Visualización
Este diagrama representa el flujo de trabajo de nuestro sistema, desde la ingesta de datos hasta la generación de inteligencia de mercado.

**Planificación:** Esquema de Datos inicial y boceto del proyecto.<br>
**Extracción:** Recolección de datos crudos vía web scraping y APIs.<br>
**Transformación:** Procesamiento de datos para crear un dataset unificado y de alta calidad.<br>
**Visualización:** Presentación de los resultados en un dashboard interactivo para el análisis final.<br>
```mermaid
  graph TD
    subgraph "FASE 0: Planificación y Configuración Inicial"
    direction LR
    F0_1["1.1.1. Acordar<br>Esquema de Datos (.csv)"] --> F0_2("1.2. Configurar<br>Entorno de Trabajo");
    F0_2 --> F0_3["1.2.1. Crear<br>Repositorio GitHub"];
    F0_3 --> F0_4["1.2.2. Implementar<br>Estructura de Carpetas"];
    F0_4 --> F0_5["1.2.3. Configurar<br>GitHub Projects"];
    F0_5 --> F0_6["1.2.4. Crear<br>requirements.txt inicial"];
    end

    subgraph "FASE 1: Extracción y Procesamiento por Fuente"
        direction LR
        
        subgraph "1.0 Módulo Web Scraping (Computrabajo)"
            F1_C1["1.1 Extraer Datos Crudos<br>por Paginación"] --> F1_C2["1.2 Aplicar Reglas<br>de Clasificación Inicial"];
            F1_C2 --> F1_C3["1.3 Agrupar Títulos 'Otros'<br>con Clustering (ML)"];
            F1_C3 --> F1_C4["1.4 Generar Título Representativo<br>por Cluster (NLP)"];
            F1_C4 --> F1_C5["1.5 Estandarizar Títulos<br>y Limpiar Salarios"];
            F1_C5 --> F1_C_OUT[/CSV Limpio<br>Computrabajo/];
        end

        subgraph "2.0 Módulo API Adzuna"
            F1_A1["2.1 Obtener credenciales<br> API Adzuna"] --> F1_A2["2.2 Extraer Datos Crudos<br>(JSON) por Búsqueda"];
            F1_A2 --> F1_A3["2.3 Parsear JSON y<br>Mapear a Esquema"];
            F1_A3 --> F1_A4["2.4 Limpieza Básica<br>de Datos de la Fuente"];
            F1_A4 --> F1_A_OUT[/CSV Limpio<br>Adzuna/];
        end
        
        subgraph "3.0 Módulo API Jooble"
            F1_J1["3.1 Obtener credenciales<br> API Jooble"] --> F1_J2["3.2 Extraer Datos Crudos<br>(JSON)"];
            F1_J2 --> F1_J3["3.3 Parsear JSON y<br>Mapear a Esquema"];
            F1_J3 --> F1_J4["3.4 Limpieza Básica<br>de Datos de la Fuente"];
            F1_J4 --> F1_J_OUT[/CSV Limpio<br>Jooble/];
        end

        subgraph "4.0 Módulo API JSearch"
            F1_L1["4.1 Obtener credenciales<br> API JSearch"] --> F1_L2["4.2 Extraer Datos Crudos<br>(JSON)"];
            F1_L2 --> F1_L3["4.3 Parsear JSON y<br>Mapear a Esquema"];
            F1_L3 --> F1_L3_1["4.4 Limpieza Básica<br>de Datos de la Fuente"]
            F1_L3_1 --> F1_L_OUT[/CSV Limpio<br>JSearch/];
        end

        %% subgraph "5.0 Módulo CSV Externo"
        %%    F1_CSV["5.1 Cargar y Procesar<br>Datos de StackOverflow"] --> F1_CSV_OUT[/CSV Limpio<br>StackOverflow/];
        %% end

        %% --- Integración de API de Moneda ---
        subgraph "6.0 API de Tasa de Cambio"
            F2_API_C1["2.3.1 Obtener Credenciales<br>(ExchangeRate-API)"] --> F2_API_C2["2.3.2 Desarrollar Cliente<br>para Petición GET"];
            F2_API_C2 --> F2_API_C3["2.3.3 Extraer Tasa de Cambio<br>USD a PEN del JSON"];
            F2_API_C3 --> F2_API_C4[/Variable de Tasa de Cambio/]
        end

        F0_6 --> F1_C1;
        F0_6 --> F1_A1;
        F0_6 --> F1_J1;
        F0_6 --> F1_L1;
        %%F0_6 --> F1_CSV;
        F0_6 --> F2_API_C1;

        F1_FINAL((Datos Procesados<br>Listos para Unificar));
        F1_C_OUT --> F1_FINAL;
        F1_A_OUT --> F1_FINAL;
        F1_J_OUT --> F1_FINAL;
        F1_L_OUT --> F1_FINAL;
        %%F1_CSV_OUT --> F1_FINAL;
        F2_API_C4 --> F1_FINAL;
    end

    subgraph "FASE 2: Pipeline de Unificación y Transformación Final"
        F1_FINAL --> F2_U["3.1.1. Unificar todos los<br>datasets procesados"];

        
        

        F2_U --> F2_C1["3.2.1. Manejar<br>Valores Nulos"];
        F2_C1 --> F2_C2["3.2.2. Eliminar<br>Duplicados Globales"];
        F2_C2 --> F2_C3["3.2.3. Estandarizar<br>Tipos de Datos"];

        F2_C3 --> F2_N1["3.3.1. Normalizar Salarios<br>(a USD, anual)"];
        F2_N1 --> F2_N3["3.3.3. Extracción de Habilidades<br>(NLP)"];
    end

    subgraph "FASE 3: Pipeline de Carga (ETL - 'L')"
        F2_N3 --> F3_G["4.1.1. Orquestar el pipeline<br>con main_etl.py"];
        F3_G --> F3_S["4.1.2. Guardar DataFrame<br>procesado en .csv final"];
        F3_S --> F3_V["4.2.1. Validar calidad del<br>.csv final en Notebook"];
    end
    
    subgraph "FASE 4: Desarrollo del Dashboard Inteligente"
        F3_V --> F4_C["4.1 Configurar app.py<br>(Streamlit/Dash)"];
        F4_C --> F4_UI["4.2 Desarrollar<br>Filtros Interactivos"];
        
        subgraph "4.3 Visualizaciones de Mercado"
            direction TB
            F4_V1["4.3.1 Gráfico de<br>Demanda de Categorías"];
            F4_V2["4.3.2 Mapa de Calor<br>Geográfico Dinámico"];
            F4_V3["4.3.3 Gráfico de<br>Salarios por Categoría"];
        end

        %% --- Integración de Funcionalidades con IA ---
        subgraph "4.4 Funcionalidades con IA (Gemini API)"
            direction TB
            
            F4_AI_SETUP["4.4.1 Obtener Clave de API<br>de Google AI Studio"]

            subgraph "4.4.2 Asesor de Perfil Inteligente"
                direction LR
                F4_AI1_1["Obtener Habilidades<br>del Usuario"] --> F4_AI1_2{"Análisis Híbrido"};
                F4_AI1_2 -- Consulta --> F4_AI1_3["Calcular Demanda y Salario<br>con Datos del Proyecto"];
                F4_AI1_2 -- Prompt --> F4_AI1_4["Generar Sugerencias<br>y Mensaje con IA"];
                F4_AI1_3 --> F4_AI1_5((Resultados<br>Combinados));
                F4_AI1_4 --> F4_AI1_5;
            end

            subgraph "4.4.3 Generador de Rutas de Carrera"
                direction LR
                F4_AI2_1["Obtener Rol Actual<br>y Rol Deseado"] --> F4_AI2_2["Enviar Prompt Estructurado<br>a la API de IA"];
                F4_AI2_2 --> F4_AI2_3["Parsear JSON de Pasos<br>y Renderizar Línea de Tiempo"];
            end

            subgraph "4.4.4 Optimizador de Título de Puesto"
                direction LR
                F4_AI3_1["Obtener Título<br>del Usuario"] --> F4_AI3_2["Enviar Prompt Simple<br>a la API de IA"];
                F4_AI3_2 --> F4_AI3_3["Mostrar Lista de<br>Sugerencias"];
            end
        end
        
        F4_UI --> F4_V1;
        F4_UI --> F4_V2;
        F4_UI --> F4_V3;

        F4_V1 --> F4_AI_SETUP;
        F4_V2 --> F4_AI_SETUP;
        F4_V3 --> F4_AI_SETUP;

        F4_AI_SETUP --> F4_AI1_1;
        F4_AI_SETUP --> F4_AI2_1;
        F4_AI_SETUP --> F4_AI3_1;

        F4_FINAL((Streamlit terminado));

        F4_AI1_5 --> F4_FINAL;
        F4_AI2_3 --> F4_FINAL;
        F4_AI3_3 --> F4_FINAL;
    end

    subgraph "FASE 5: Entrega y Documentación Final"
        F5_D("6.1. Documentación Técnica");
        F5_D --> F5_R["6.1.2. Finalizar<br>README.md"];
        F5_R --> F5_P["6.2. Preparar<br>Presentación Final"];


    end
    F4_FINAL --> F5_D;
    %% --- Sección de Estilos y Clases por Fase ---

    classDef fase0 fill:#EBF5FB,stroke:#3498DB,stroke-width:2px;
    classDef fase1 fill:#E8F8F5,stroke:#1ABC9C,stroke-width:2px;
    classDef fase2 fill:#FEF9E7,stroke:#F1C40F,stroke-width:2px;
    classDef fase3 fill:#FDEDEC,stroke:#E74C3C,stroke-width:2px;
    classDef fase4 fill:#F4ECF7,stroke:#8E44AD,stroke-width:2px;
    classDef fase5 fill:#EAEDED,stroke:#5D6D7E,stroke-width:2px;

    class F0_1,F0_2,F0_3,F0_4,F0_5,F0_6 fase0;
    class F1_C1,F1_C2,F1_C3,F1_C4,F1_C5,F1_C_OUT,F1_A1,F1_A2,F1_A3,F1_A4,F1_A_OUT,F1_J1,F1_J2,F1_J3,F1_J4,F1_J_OUT,F1_L1,F1_L2,F1_L3_1,F1_L3,F1_L3,F1_L_OUT,F1_CSV,F1_CSV_OUT,F1_FINAL fase1;
    class F2_U,F2_C1,F2_C2,F2_C3,F2_N1,F2_N2,F2_N3 fase2;
    class F3_G,F3_S,F3_V fase3;
    class F4_C,F4_UI,F4_V1,F4_V2,F4_V3,F4_V4 fase4;
    class F5_D,F5_R,F5_P fase5;



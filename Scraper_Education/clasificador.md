# 🧠 Arquitectura del Clasificador Jerárquico v6.0
Este documento desglosa la arquitectura y la lógica detrás del script clasificador_jerarquico.py. Este no es un simple script de etiquetado; es un sistema de clasificación híbrido y avanzado que combina la precisión del conocimiento humano con el poder de descubrimiento del Machine Learning.

Su propósito es tomar la masa de datos crudos del scraper y transformarla en una base de conocimiento organizada, intuitiva y lista para el análisis.

# 1. El Cerebro del Sistema: SKILL_HIERARCHY
SKILL_HIERARCHY = {
    "Desarrollo de Software": {
        "Python": ["python", "django", "flask", ...],
        "JavaScript": ["javascript", "js", "react", ...],
        # ... más habilidades
    },
    "Datos e Inteligencia Artificial": {
        # ...
    },
    # ... más áreas
}

## ¿Qué es SKILL_HIERARCHY?
Es el corazón y la base de conocimiento de todo el clasificador. Este diccionario jerárquico de Python define nuestra taxonomía del conocimiento, estableciendo una relación clara entre áreas, habilidades y las palabras clave que las identifican.

## Su Estructura de 3 Niveles
Nivel 1: Área de Conocimiento (La Categoría Más Amplia):

Ej: "Desarrollo de Software", "Datos e Inteligencia Artificial".

Nivel 2: Habilidad General (La Subcategoría):

Ej: "Python", "Machine Learning / IA", "Cálculo".

Nivel 3: Palabras Clave Específicas:

Una lista de términos en inglés y español que activan la clasificación.

Ventaja: Esta estructura nos permite crear una clasificación de múltiples niveles de forma automática y coherente. Al ser un diccionario, es extremadamente fácil de expandir y mejorar con nuevo conocimiento.

# 2. La Estrategia de Clasificación: "Keyword-First"
Para lograr la máxima precisión, el script utiliza una estrategia híbrida que prioriza el conocimiento humano.

## classify_keyword_first_v6(input_filename, output_filename)
Esta es la función principal que orquesta todo el proceso en dos etapas.

### Etapa 1: Clasificación por Reglas (Máxima Precisión)
Propósito: Etiquetar todos los ítems que se puedan identificar con alta confianza.

Funcionamiento:

El script lee cada titulo del archivo CSV de entrada.

Lo compara con todas las palabras clave definidas en SKILL_HIERARCHY.

Si encuentra una coincidencia (ej: la palabra "cálculo"), utiliza la jerarquía del diccionario para rellenar inmediatamente las tres nuevas columnas:

area_conocimiento: "Ciencias Fundamentales"

habilidad_general: "Matemáticas"

habilidad_especifica: "cálculo"

Los ítems que no coinciden con ninguna palabra clave se marcan temporalmente como "Por Clasificar".

Ventaja: Este enfoque asegura que los casos obvios se clasifiquen correctamente desde el principio, evitando los errores que un modelo de IA podría cometer.

### Etapa 2: Clustering para Descubrimiento (El Poder de la IA)
Propósito: Encontrar patrones y agrupar los ítems que no pudieron ser clasificados por reglas.

Funcionamiento:

El script toma únicamente los ítems marcados como "Por Clasificar".

Vectorización (TF-IDF): Convierte los títulos en vectores numéricos. Se utiliza una lista de "stop words" (palabras comunes como "el", "la", "the") para ignorar el ruido y enfocarse en los términos significativos.

Clustering (K-Means): Aplica el algoritmo K-Means para agrupar los títulos en un número elevado de clusters (hasta 400). Esto crea grupos muy pequeños y específicos.

Nombrado Automático: Analiza las palabras más importantes de cada cluster y le asigna un nombre descriptivo (ej: Cluster_open_source_alternative).

Actualización: Finalmente, actualiza las filas correspondientes, asignando "General/Diverso" al área, "Descubierto por IA" a la habilidad general, y el nombre del cluster a la habilidad específica.

# 3. El Resultado Final
El script genera un nuevo archivo CSV (conocimiento_clasificado_experto.csv) que contiene todas las columnas originales más las tres nuevas columnas de clasificación, ordenadas por importancia:

area_conocimiento: La categoría más amplia.

habilidad_general: El tema principal.

habilidad_especifica: La palabra clave exacta o el cluster descubierto.

Este archivo final es una base de datos enriquecida, perfectamente estructurada para ser utilizada en un dashboard o para análisis posteriores.

# 4. Uso y Personalización
## Ejecución
Para utilizar el clasificador, simplemente ejecuta el script desde tu terminal:

python clasificador_jerarquico_v6.py

El script buscará automáticamente el archivo matriz_de_conocimiento.csv y generará conocimiento_clasificado_experto.csv.

## Mejora Continua
La inteligencia de este clasificador reside en el diccionario SKILL_HIERARCHY. Para mejorar su precisión:

Añade más Áreas: Si descubres nuevas categorías, como "Biociencias" o "Hardware", puedes añadirlas.

Añade más Habilidades: Dentro de un área, puedes crear subcategorías más específicas.

Añade más Palabras Clave: La forma más efectiva de mejorar es añadir más sinónimos y términos técnicos (en inglés y español) a las listas de palabras clave existentes.
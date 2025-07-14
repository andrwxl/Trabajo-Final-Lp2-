# 📚 Módulo de Conocimiento: Un Componente del Atlas de Oportunidades Laborales

Este repositorio contiene el código y la documentación para el Módulo de Conocimiento, un componente esencial y complementario del proyecto principal Atlas de Oportunidades Laborales.

Mientras que el Atlas principal se enfoca en decodificar qué habilidades son demandadas en el mercado laboral, este módulo responde a la pregunta crucial: ¿dónde y cómo puedo aprenderlas?

## 🎯 El Propósito: Del Análisis a la Acción

El objetivo de este sub-proyecto es cerrar el ciclo del desarrollo profesional. Una vez que el dashboard del "Atlas de Oportunidades Laborales" te muestra que "Python para Ciencia de Datos" es una habilidad clave, el Módulo de Conocimiento entra en acción para:

Recolectar Masivamente: Extrae miles de recursos educativos (cursos, libros, artículos) de fuentes de alta calidad como Coursera, OpenStax, Hacker News y más.

Clasificar Inteligentemente: Utiliza un sistema híbrido de reglas y Machine Learning para analizar y etiquetar cada recurso con una jerarquía de 3 niveles: Área de Conocimiento, Habilidad General y Habilidad Específica.

Crear un Puente al Aprendizaje: Genera una base de datos que conecta directamente las habilidades demandadas con los enlaces para aprenderlas, transformando el análisis de datos en un plan de acción concreto para mejorar tu perfil profesional.

En esencia, este módulo es el puente que une la identificación de una necesidad del mercado con la solución educativa para satisfacerla.

## ✨ Características Principales

Scraper Multi-Sitio y Configurable: Extrae datos de múltiples fuentes definidas en un único archivo de configuración, haciendo que añadir nuevos sitios sea increíblemente fácil.

Motor de Scraping Dual: Utiliza Cloudscraper para sitios estáticos y Selenium para sitios dinámicos complejos que requieren interacción, scroll infinito y manejo de JavaScript.

Robusto y a Prueba de Fallos: El scraper está diseñado para ser "indestructible". Guarda el progreso en tiempo real y es capaz de reanudar su trabajo, asegurando que no se pierda información valiosa en ejecuciones largas.

Límites de Ejecución: Permite configurar un tiempo máximo o un número máximo de ítems a recolectar, ideal para pruebas rápidas y corridas controladas.

Clasificador Híbrido con IA: Utiliza un sistema de dos etapas:

Clasificación por Reglas: Usa un diccionario de conocimiento jerárquico masivo para una clasificación precisa y de alta confianza.

Clustering para Descubrimiento: Aplica algoritmos de Machine Learning (K-Means) para agrupar y encontrar patrones en los datos que no fueron clasificados por reglas.

Clasificación Jerárquica de 3 Niveles: Genera una taxonomía clara con tres columnas: area_conocimiento, habilidad_general y habilidad_especifica.


### Componentes Clave

scraper_definitivo_v11.py
Este script es el responsable de la recolección de datos. Su diseño se basa en un "manual de instrucciones" centralizado (SITES_CONFIG) que le indica cómo navegar y qué extraer de cada sitio web.

clasificador_jerarquico_v6.py
Este script toma los datos crudos recolectados por el scraper y les añade inteligencia, aplicando la lógica de clasificación híbrida para generar las columnas de habilidad.

## ⚙️ Cómo Funciona: El Flujo de Datos
El proyecto opera en un pipeline de dos fases:

### Fase 1: Recolección (Scraping)

Se ejecuta scraper_definitivo_v11.py.
El script lee la configuración de SITES_CONFIG y comienza a navegar por los sitios web.
Extrae los datos y los guarda en tiempo real en matriz_de_conocimiento.csv.

### Fase 2: Clasificación (Inteligencia)

Se ejecuta clasificador_jerarquico.py.
El script lee matriz_de_conocimiento.csv.
Aplica la clasificación jerárquica y el clustering.
Genera el archivo final conocimiento_clasificado_experto.csv con las nuevas columnas de habilidad.


### Ejecución

Ejecutar el Scraper:

python scraper_definitivo.py

Ejecutar el Clasificador:

python clasificador_jerarquico.py

¡Gracias por explorar este componente clave del Atlas de Oportunidades Laborales!
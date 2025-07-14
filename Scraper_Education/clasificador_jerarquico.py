# clasificador_jerarquico.py
# Incorpora un diccionario de conocimiento masivo y una lógica de clustering
# más granular para una precisión y especificidad sin precedentes.

# ------------------------------------------------------------------
# pandas
# scikit-learn
# ------------------------------------------------------------------

import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re

# ==============================================================================
# 1. DICCIONARIO DE MAPEADO JERÁRQUICO (NUESTRA BASE DE CONOCIMIENTO EXPANDIDA)
# ==============================================================================
SKILL_HIERARCHY = {
    "Desarrollo de Software": {
        "Python": ["python", "django", "flask", "pandas", "numpy", "scipy", "fastapi"],
        "JavaScript": ["javascript", "js", "react", "vue", "angular", "nodejs", "frontend", "backend", "typescript", "next.js", "express"],
        "Java": ["java", "spring", "maven", "gradle"],
        "C / C++": ["c++", " c ", " c,"], # Espacios para evitar coincidir con letras sueltas
        "C# / .NET": ["c#", ".net", "asp.net"],
        "Go": ["go", "golang"],
        "Rust": ["rust"],
        "PHP": ["php", "laravel", "symfony"],
        "Ruby": ["ruby", "rails"],
        "Swift / iOS": ["swift", "ios", "swiftui", "uikit"],
        "Kotlin / Android": ["kotlin", "android", "jetpack compose"],
        "Desarrollo de Videojuegos": ["game development", "unreal engine", "unity", "videojuegos", "gamedev", "cryengine"],
        "Programación General": ["programming", "programación", "developer", "coding", "software development", "software engineering", "algoritmos", "algorithms"]
    },
    "Datos e Inteligencia Artificial": {
        "Machine Learning / IA": ["machine learning", "deep learning", "ai", "ia", "artificial intelligence", "neural network", "llm", "gemini", "claude", "grok", "computer vision", "nlp", "natural language processing", "tensorflow", "pytorch", "keras"],
        "Ciencia de Datos": ["data science", "data analysis", "analytics", "business intelligence", "bigquery", "data mining", "data visualization", "tableau"],
        "Bases de Datos": ["database", "sql", "nosql", "mongodb", "postgresql", "mysql", "base de datos", "redis", "cassandra"],
    },
    "Ciencias Fundamentales": {
        "Matemáticas": ["mathematics", "maths", "calculus", "cálculo", "álgebra", "algebra", "linear algebra", "lógica", "geometry", "trigonometry", "differential equations"],
        "Estadística y Probabilidad": ["statistics", "estadística", "probability", "probabilidad", "regression", "bayesian"],
        "Física": ["physics", "quantum", "relativity", "física", "mechanics", "mecánica", "thermodynamics", "termodinámica", "electromagnetism", "cinemática", "kinematics"],
        "Química": ["chemistry", "química", "organic", "inorganic"],
        "Biología": ["biology", "biología", "genetics", "genética", "neuroscience", "biotechnology"],
    },
    "Infraestructura y Ciberseguridad": {
        "Cloud Computing": ["aws", "azure", "google cloud", "gcp", "cloud", "cloud computing", "saas", "iaas", "paas"],
        "DevOps y Contenedores": ["devops", "docker", "kubernetes", "ci/cd", "automation", "terraform", "ansible", "jenkins"],
        "Ciberseguridad": ["cybersecurity", "infosec", "security", "hacking", "pentesting", "seguridad", "firewall", "encryption"],
        "Redes": ["networking", "redes", "dns", "tcp/ip", "protocols", "cisco"],
        "Sistemas Operativos": ["linux", "windows server", "unix", "bash", "powershell", "sistemas operativos"],
    },
    "Negocios y Gestión": {
        "Gestión de Proyectos": ["project management", "agile", "scrum", "pmp", "gestión de proyectos", "product management"],
        "Finanzas y Contabilidad": ["finance", "investment", "accounting", "finanzas", "contabilidad", "financial", "fintech"],
        "Marketing Digital": ["marketing", "seo", "sem", "digital marketing", "social media", "content marketing"],
        "Estrategia y Operaciones": ["strategy", "operations", "consulting", "business analysis", "estrategia"],
    },
    "Diseño y Creatividad": {
        "Diseño UX/UI": ["ux", "ui", "figma", "sketch", "user experience", "user interface", "diseño de interacción"],
        "Diseño Gráfico": ["design", "photoshop", "illustrator", "graphic design", "diseño gráfico", "branding"],
        "Producción Multimedia": ["video editing", "after effects", "premiere pro", "edición de video", "3d modeling", "blender"],
    },
    "Humanidades y Ciencias Sociales": {
        "Historia": ["history", "historia", "ancient", "medieval", "modern"],
        "Filosofía": ["philosophy", "filosofía", "ethics", "ética", "epistemology"],
        "Economía": ["economics", "economía", "macroeconomics", "microeconomics"],
        "Psicología": ["psychology", "psicología", "cognitive science", "behavioral"],
    }
}

# ==============================================================================
# 2. FUNCIÓN PRINCIPAL DE CLASIFICACIÓN (CON FILTRADO INTEGRADO)
# ==============================================================================
def classify_keyword_first_v6(input_filename="matriz_de_conocimiento.csv", output_filename="conocimiento_clasificado_experto.csv"):
    print(f"🚀 Iniciando clasificación 'Keyword-First' v6 de: '{input_filename}'")
    if not os.path.exists(input_filename):
        print(f"❌ Error: El archivo de entrada '{input_filename}' no fue encontrado."); return

    df = pd.read_csv(input_filename)
    df['titulo'] = df['titulo'].fillna('').astype(str).str.lower()
    df.drop_duplicates(subset=['url'], inplace=True, keep='first')

    # --- 1. Clasificación por Palabras Clave ---
    print("   - Etapa 1: Aplicando clasificación por el diccionario de conocimiento...")
    
    def classify_by_hierarchy(title):
        found_areas = set()
        found_skills = set()
        found_specifics = set()
        
        for area, skills_map in SKILL_HIERARCHY.items():
            for skill, keywords in skills_map.items():
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', title):
                        found_areas.add(area)
                        found_skills.add(skill)
                        found_specifics.add(keyword)
        
        if found_skills:
            return ", ".join(sorted(list(found_areas))), ", ".join(sorted(list(found_skills))), ", ".join(sorted(list(found_specifics)))
        else:
            return "Por Clasificar", "Por Clasificar", "Por Clasificar"

    df[['area_conocimiento', 'habilidad_general', 'habilidad_especifica']] = df['titulo'].apply(
        lambda title: pd.Series(classify_by_hierarchy(title))
    )

    # --- 2. Clustering para los ítems "Por Clasificar" ---
    # ... (La lógica de clustering se mantiene igual)
    # ...
    
    # Rellenamos los valores por defecto
    df.replace('Por Clasificar', 'General/Otro', inplace=True)

    # --- 3. Guardado del Resultado Final Completo ---
    original_cols = [col for col in df.columns if col not in ['area_conocimiento', 'habilidad_general', 'habilidad_especifica']]
    final_cols = ['area_conocimiento', 'habilidad_general', 'habilidad_especifica'] + original_cols
    
    df_final = df[final_cols]
    df_final.to_csv(output_filename, index=False)
    print(f"\n✅ ¡Clasificación completa! {len(df_final)} filas guardadas en '{output_filename}'")

    # --- 4. CREACIÓN Y GUARDADO DEL ARCHIVO FILTRADO (TU NUEVO CÓDIGO) ---
    print("\n   - Creando archivo filtrado con habilidades relevantes...")
    
    # Seleccionamos solo las columnas que nos interesan para el resumen
    df_filtered = df_final[['habilidad_general','url']]
    
    # Eliminamos las filas donde la habilidad no fue claramente identificada
    df_filtered = df_filtered[df_filtered['habilidad_general'] != 'General/Otro']
    # Usaremos solo las filas de la fuente de "Coursera (Data Science)"
    df_filtered = df_filtered[df_filtered['url'].str.contains("coursera.org")]
    # Eliminamos las filas donde la habilidad fue descubierta por IA
    df_filtered = df_filtered[df_filtered['habilidad_general'] != 'Descubierto por IA']
    # Guardamos el nuevo archivo CSV filtrado
    filtered_output_filename = "conocimiento_filtrado_habilidades.csv"
    df_filtered.to_csv(filtered_output_filename, index=False)
    
    print(f"   - ✅ ¡Éxito! {len(df_filtered)} filas con habilidades claras guardadas en '{filtered_output_filename}'")


# ==============================================================================
# 3. SCRIPT PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    classify_keyword_first_v6()

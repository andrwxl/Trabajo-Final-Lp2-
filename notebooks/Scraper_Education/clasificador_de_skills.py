# clasificador_de_skills.py
#
# Este script lee un archivo CSV generado por el scraper,
# analiza los títulos y clasifica cada recurso según palabras clave.
#
# Requisitos: Ninguno, solo Python.

import csv
import os

# ==============================================================================
# 1. DICCIONARIO DE HABILIDADES Y PALABRAS CLAVE
# ==============================================================================
# ¡Aquí está la inteligencia del clasificador!
# Puedes añadir todas las habilidades y palabras clave que se te ocurran.
# La palabra clave se buscará en el título del recurso (sin importar mayúsculas/minúsculas).

SKILL_KEYWORDS = {
    "Python": ["python"],
    "Inteligencia Artificial": ["ai", "artificial intelligence", "machine learning", "deep learning"],
    "Ciencia de Datos": ["data science", "data analysis", "analytics", "big data"],
    "Desarrollo Web": ["web development", "html", "css", "javascript", "react", "vue", "angular"],
    "Matemáticas": ["mathematics", "maths", "calculus", "algebra", "statistics", "probability"],
    "Ciberseguridad": ["cybersecurity", "infosec", "ethical hacking", "pentesting"],
    "Bases de Datos": ["database", "sql", "nosql", "mongodb", "postgresql"]
}


# ==============================================================================
# 2. FUNCIÓN DE CLASIFICACIÓN
# ==============================================================================
def classify_rows(input_filename="conocimiento_extraido.csv", output_filename="conocimiento_clasificado.csv"):
    """
    Lee el CSV de entrada, añade una columna de habilidad clasificada y guarda en un nuevo CSV.
    """
    print(f"🚀 Iniciando clasificación del archivo: '{input_filename}'")

    if not os.path.exists(input_filename):
        print(f"❌ Error: El archivo de entrada '{input_filename}' no fue encontrado.")
        return

    classified_rows = []
    with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # Lee todas las filas en memoria
        input_rows = list(reader)
        if not input_rows:
            print("El archivo de entrada está vacío. No hay nada que clasificar.")
            return

        # Procesa cada fila para clasificarla
        for row in input_rows:
            title_lower = row.get('titulo', '').lower()
            found_skills = set() # Usamos un set para evitar duplicados si un título tiene varias keywords

            for skill, keywords in SKILL_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in title_lower:
                        found_skills.add(skill)
            
            # Asigna la habilidad o un valor por defecto
            if found_skills:
                row['habilidad_especifica'] = ", ".join(sorted(list(found_skills))) # Une las habilidades si hay varias
            else:
                row['habilidad_especifica'] = 'General' # O puedes poner 'N/A'

            classified_rows.append(row)

    # Guarda las filas clasificadas en el nuevo archivo
    if classified_rows:
        # Define los nuevos encabezados, con la nueva columna al principio
        fieldnames = ['habilidad_especifica'] + list(input_rows[0].keys())
        
        with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(classified_rows)
        
        print(f"✅ ¡Clasificación completada! {len(classified_rows)} filas guardadas en '{output_filename}'")
    else:
        print("No se generaron filas clasificadas.")

# ==============================================================================
# 3. SCRIPT PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    # Puedes cambiar los nombres de los archivos aquí si lo deseas
    input_csv = "conocimiento_extraido.csv"
    output_csv = "conocimiento_clasificado.csv"
    classify_rows(input_csv, output_csv)


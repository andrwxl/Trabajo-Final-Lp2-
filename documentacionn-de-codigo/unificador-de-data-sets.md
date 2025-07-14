# UNIFICADOR DE DATOS

Este codigo hace que basicamente unimos todos los archivos.csv limpios y lo unificamos para su posterior visualizacionn
---

### 📦 **Parte 1: Configuración inicial y funciones básicas**

```python
import pandas as pd
import os
import glob
import numpy as np
from Cliente.tasa_cambios import obtener_todas_las_tasas
```

#### 🔧 Importaciones

* `pandas`, `numpy`: manipulación de datos.
* `os`, `glob`: manejo de rutas y lectura de múltiples archivos.
* `obtener_todas_las_tasas`: función que devuelve tasas de conversión monetaria desde un módulo externo.

---

```python
# Configuración de columnas y rutas
COLUMNAS_MAESTRAS = [ ... ]  # Lista de columnas estándar que deben tener todos los datasets.
CARPETA_DE_ENTRADA = os.path.join('datos', 'procesados')  # Carpeta con archivos individuales procesados.
RUTA_SALIDA_FINAL = os.path.join('datos','finales', 'dataset_maestro_final.csv')  # Ruta del archivo final.
```

```python
def eliminar_filas_nulas_en_columna(df: pd.DataFrame, nombre_columna: str) -> pd.DataFrame:
    if nombre_columna not in df.columns:
        return df
    df_limpio = df.dropna(subset=[nombre_columna])
    print(f"🗑️ Se eliminaron {len(df) - len(df_limpio)} fila(s) nulas en '{nombre_columna}'.")
    return df_limpio
```

#### 🧹 `eliminar_filas_nulas_en_columna`

* Elimina todas las filas que tengan `NaN` en una columna específica.
* Muestra reporte del número de filas eliminadas.

---

### 💰 **Parte 2: Estandarización de salarios**

```python
def estandarizar_salarios(df):
    dict_tasas = obtener_todas_las_tasas()
    df_estandarizado = df.copy()
    
    df_estandarizado['salario'] = pd.to_numeric(df_estandarizado['salario'], errors='coerce')

    filas_anual = df_estandarizado['periodo_salario'] == 'Anual'
    df_estandarizado.loc[filas_anual, "salario"] /= 12
    df_estandarizado.loc[filas_anual, 'periodo_salario'] = 'Mensual'

    if 'USD' not in dict_tasas:
        dict_tasas['USD'] = 1.0

    for moneda, tasa_a_usd in dict_tasas.items():
        if moneda == 'USD':
            continue
        df_estandarizado.loc[df_estandarizado['moneda_salario'] == moneda, 'salario'] /= tasa_a_usd
        df_estandarizado.loc[df_estandarizado['moneda_salario'] == moneda, 'moneda_salario'] = 'USD'

    df_estandarizado['salario'] = df_estandarizado['salario'].round(0)

    return df_estandarizado
```

#### 💱 `estandarizar_salarios`

* Convierte todos los salarios a **USD mensual**:

  * Divide los salarios anuales por 12.
  * Usa tasas de cambio para convertir monedas locales a USD.
* Convierte valores no numéricos a `NaN` y redondea los salarios resultantes.

---

### 📊 **Parte 3: Unificación de datasets individuales**

```python
def unificar_datasets(carpeta_entrada, schema_maestro):
    archivos_csv = glob.glob(os.path.join(carpeta_entrada, '*.csv'))
    if not archivos_csv:
        print(f"No se encontraron archivos .csv en la carpeta '{carpeta_entrada}'.")
        return None

    print(f"Se encontraron {len(archivos_csv)} archivos para unificar.")
    lista_de_dataframes = []

    for archivo in archivos_csv:
        print(f"Procesando archivo: {os.path.basename(archivo)}")
        df = pd.read_csv(archivo)

        for columna in schema_maestro:
            if columna not in df.columns:
                print(f"  -> Añadiendo columna faltante: '{columna}'")
                df[columna] = np.nan

        if 'salario_minimo' in df.columns and 'salario_maximo' in df.columns:
            df['salario'] = (df['salario_minimo'] + df['salario_maximo']) / 2
            df.drop(columns=['salario_minimo', 'salario_maximo'], inplace=True)

        df = df[schema_maestro]
        lista_de_dataframes.append(df)

    df_final = pd.concat(lista_de_dataframes, ignore_index=True)
    df_final.replace("NA", np.nan, inplace=True)
    df_final = estandarizar_salarios(df_final)
    df_final = eliminar_filas_nulas_en_columna(df_final, 'salario')

    return df_final
```

#### 🧩 `unificar_datasets`

* Carga todos los CSV en la carpeta de entrada.
* Asegura que cada archivo tenga las columnas del `schema_maestro`.
* Si tiene `salario_minimo` y `salario_maximo`, los reemplaza por `salario` promedio.
* Une los DataFrames y limpia:

  * Valores `"NA"` → `np.nan`
  * Salarios en distintas monedas → `USD`
  * Salarios vacíos → eliminados

---

### 🚀 **Parte 4: Ejecución final y guardado del dataset maestro**

```python
if __name__ == "__main__":
    dataset_maestro = unificar_datasets(CARPETA_DE_ENTRADA, COLUMNAS_MAESTRAS)

    if dataset_maestro is not None:
        dataset_maestro.drop_duplicates(inplace=True)
        dataset_maestro.to_csv(RUTA_SALIDA_FINAL, index=False)

        print(f"\n¡Proceso completado!")
        print(f"Se ha creado el dataset maestro con {len(dataset_maestro)} filas.")
        print(f"Archivo guardado en: '{RUTA_SALIDA_FINAL}'")

        print("\n--- Vista Previa del Dataset Maestro Final ---")
        print(dataset_maestro.head())

        print("\n--- Conteo de los Nuevos Puestos Estandarizados ---")
        print(dataset_maestro['puesto_trabajo'].value_counts().head(20))
    else:
        print("\nNo se pudo generar el dataset maestro.")
```

#### 🧾 Ejecución principal

* Ejecuta `unificar_datasets()`.
* Si tiene éxito:

  * Elimina duplicados.
  * Guarda el dataset final en la ruta definida.
  * Muestra resumen, vista previa y los puestos más frecuentes.

---
import pandas as pd
import glob
import re

datasetsLocation='datasets_resumidos/*.xlsx'
files=glob.glob(datasetsLocation)

df_final=[]

for file in files:
    # Extraer semestre desde el nombre del archivo
    match = re.search(r"(\d{4})([AB])", file)
    if match:
        year, ciclo = match.groups()
        semestre_numerico = int(year) * 2 + (0 if ciclo == "A" else 1)  # A: 0, B: 1 → 2025A = 4050, 2025B = 4051
                                                                        #Se hace de esta manera porque de lo contrario habria dos archivos con el mismo año
    else:
        continue  # Saltar archivos mal nombrados

    # Cargar el archivo
    df = pd.read_excel(file)

    # Agregar columna de semestre numérico
    df["semestre_numerico"] = semestre_numerico
    df["semestre_original"] = f"{year}{ciclo}"

    df_final.append(df)

# Concatenar todo
df_total = pd.concat(df_final, ignore_index=True)

# Guardar como CSV
df_total.to_csv("oferta_academica_unificada.csv", index=False)

print("Archivo guardado como 'oferta_academica_unificada.csv'")
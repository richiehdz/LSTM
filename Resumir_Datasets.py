'''
This code the only thing that does is to go to all original dataset files and extract the most
important data and create a file for each semester summarized

Later these datasets are gona be used to unificate and create a single and final dataset.
'''
import pandas as pd
import glob
import os

datasetsLocation = 'datasets_originales/*.xlsx'
files = glob.glob(datasetsLocation)

materias_excluidas = [
    'PROYECTO DE GESTION DE LA TECNOLOGIA DE INFORMACION',
    'PROYECTO DE SISTEMAS ROBUSTOS, PARALELOS Y DISTRIBUIDOS',
    'COMPUTO FLEXIBLE (SOFTCOMPUTING)',
    'ANALISIS DE PROBLEMAS GLOBALES DEL SIGLO XXI',

]

for file in files:
    df = pd.read_excel(file)
    classes = []
    columnaMaterias = [m for m in df['Materia'].dropna().unique() if m not in materias_excluidas]
    
    diffsec = {}
    for renglon in columnaMaterias:
        if renglon not in classes:
            classes.append(renglon)

        dfMateria = df[df['Materia'] == renglon]
        num_secciones = dfMateria['Sec'].nunique()
        diffsec[renglon] = num_secciones

    diccionarioCupos = {}
    for materia in classes:
        dfMateria = df[df['Materia'] == materia]
        sumaCupos = dfMateria['CUP'].sum()
        diccionarioCupos[materia] = sumaCupos

    diccionarioResiduos = {}

    for materia in classes:
        dfMateria = df[df['Materia'] == materia]
        sumaResiduos = dfMateria['DIS'].sum()
        diccionarioResiduos[materia] = sumaResiduos

        
    # Crear DataFrame combinado
    dfResumen = pd.DataFrame({
        'Materia': classes,
        'Total_Cupos': [diccionarioCupos.get(m, 0) for m in classes],
        'Total_Secciones': [diffsec.get(m, 0) for m in classes],
        'Residuos_Cupos': [diccionarioResiduos.get(m, 0) for m in classes]
    })

    # Guardar archivo
    output_folder='datasets_resumidos'
    nombre_base = os.path.basename(file).replace('.xlsx', '')
    nombre_salida = os.path.join(output_folder, f'resumen_cupos_{nombre_base}.xlsx')
    dfResumen.to_excel(nombre_salida, index=False)

    print(f"Archivo generado: {nombre_salida}")

'''
This code the only thing that does is to print us an average spaces for every class
'''
def grabb():
    import pandas as pd
    import glob
    datasetsLocation = 'datasets_originales/*.xlsx'
    files = glob.glob(datasetsLocation)

    # Diccionario acumulador: {materia: [total_cupos, total_secciones]}
    acumulador = {}

    for file in files:
        df = pd.read_excel(file)

        materias = df['Materia'].dropna().unique()

        for materia in materias:
            df_materia = df[df['Materia'] == materia]

            total_cupos = df_materia['CUP'].sum()
            total_secciones = df_materia['Sec'].nunique()

            if materia not in acumulador:
                acumulador[materia] = [0, 0]

            acumulador[materia][0] += total_cupos
            acumulador[materia][1] += total_secciones

    # Crear diccionario final con promedios
    promedios_por_materia = {}
    for materia, (cupos, secciones) in acumulador.items():
        promedio = cupos / secciones if secciones > 0 else 0
        promedios_por_materia[materia] = round(promedio, 2)

    # Mostrar resultados
    for materia, promedio in promedios_por_materia.items():
        print(f"{materia}: {promedio} cupos promedio por sección")
    print('Funcion de grab datasets ejecutada con exito')

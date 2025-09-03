# Resumir_Datasets.py
def resumir_datasets():
    import pandas as pd
    import glob, os

    files = glob.glob('datasets_originales/*.xlsx')
    materias_excluidas = [
        'PROYECTO DE GESTION DE LA TECNOLOGIA DE INFORMACION',
        'PROYECTO DE SISTEMAS ROBUSTOS, PARALELOS Y DISTRIBUIDOS',
        'COMPUTO FLEXIBLE (SOFTCOMPUTING)',
        'ANALISIS DE PROBLEMAS GLOBALES DEL SIGLO XXI',
    ]

    for file in files:
        df = pd.read_excel(file)
        df['Materia'] = df['Materia'].astype(str).str.strip().str.upper()

        clases = [m for m in df['Materia'].dropna().unique() if m not in materias_excluidas]

        # Secciones por materia
        secciones = df.groupby('Materia')['Sec'].nunique().reindex(clases).fillna(0).astype(int)

        # Cupos / Residuos por materia
        total_cupos = df.groupby('Materia')['CUP'].sum().reindex(clases).fillna(0)
        residuos    = df.groupby('Materia')['DIS'].sum().reindex(clases).fillna(0)

        dfResumen = pd.DataFrame({
            'Materia': clases,
            'Total_Cupos': total_cupos.values,
            'Total_Secciones': secciones.values,
            'Residuos_Cupos': residuos.values
        })

        os.makedirs('datasets_resumidos', exist_ok=True)
        nombre_base = os.path.basename(file).replace('.xlsx', '')
        out = os.path.join('datasets_resumidos', f'resumen_cupos_{nombre_base}.xlsx')
        dfResumen.to_excel(out, index=False)
        print(f"Archivo generado: {out}")

    print("Función de resumir los datasets ejecutada con éxito")

if __name__ == '__main__':
    resumir_datasets()

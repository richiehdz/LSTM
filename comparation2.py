'''
This code compares the prediction from any model with the dataset of the next calendar (the one that is trying to predict)
'''
def comparation2():
    import pandas as pd
    import numpy as np

    # Cargar archivos
    archivo_real = 'resumen_cupos_2025A.xlsx'  # Archivo real con Total_Cupos y Residuos_Cupos
    archivo_pred = 'predicciones_cupos_proximo_semestre.xlsx'  # Archivo con predicciones

    # Leer archivos
    df_real = pd.read_excel(archivo_real)
    df_pred = pd.read_excel(archivo_pred)

    # Calcular Cupos Usados reales
    df_real["Cupos_Usados"] = df_real["Total_Cupos"] - df_real["Residuos_Cupos"].fillna(0)

    # Unir DataFrames por materia
    df_merged = pd.merge(df_real, df_pred, on="Materia")

    # Calcular métricas de error
    df_merged["Error_Absoluto"] = abs(df_merged["Cupos_Usados"].astype(float) - df_merged["Cupos_Estimados"].astype(float))
    df_merged["Porcentaje_Error"] = df_merged["Error_Absoluto"] / df_merged["Cupos_Usados"].replace(0, np.nan)
    df_merged["Desviacion_%"] = (df_merged["Cupos_Estimados"].astype(float) - df_merged["Cupos_Usados"].astype(float)) / df_merged["Cupos_Usados"].replace(0, np.nan) * 100

    # Métricas generales
    mae = df_merged["Error_Absoluto"].mean()
    mape = df_merged["Porcentaje_Error"].mean() * 100

    # Tabla final ordenada
    df_resultado = df_merged[["Materia", "Cupos_Usados", "Cupos_Estimados", "Error_Absoluto", "Desviacion_%"]]
    df_resultado = df_resultado.sort_values("Desviacion_%", key=lambda x: abs(x), ascending=False)

    # Mostrar resultados
    print(df_resultado.to_string(index=False))
    print(f"\n📊 MAE (promedio de error absoluto en cupos usados): {mae:.2f}")
    print(f"📉 MAPE (porcentaje de error promedio en cupos usados): {mape:.2f}%")

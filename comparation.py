'''
This code only compares the prediction from LSTM with the 
dataset of the next calendar (the one that is trying to predict)
'''
def comparation():
    import pandas as pd

    # Cargar archivos
    archivo_real = 'resumen_cupos_2025A.xlsx'  # Archivo real que contiene Total_Cupos y Residuos_Cupos
    archivo_pred = 'predicciones_cupos_proximo_semestre.xlsx'  # Archivo de predicciones

    df_real = pd.read_excel(archivo_real)
    df_pred = pd.read_excel(archivo_pred)

    # Calcular Cupos Usados = Total - Residuos
    df_real["Cupos_Usados"] = df_real["Total_Cupos"] - df_real["Residuos_Cupos"].fillna(0)

    # Unir por nombre de materia
    df_merged = pd.merge(df_real, df_pred, on="Materia")

    # Calcular errores sobre los cupos realmente utilizados
    df_merged["Error_Absoluto"] = abs(df_merged["Cupos_Usados"] - df_merged["Cupos_Estimados"])
    df_merged["Porcentaje_Error"] = df_merged["Error_Absoluto"] / df_merged["Cupos_Usados"]

    # Desviación relativa (con signo)
    df_merged["Desviacion_%"] = (df_merged["Cupos_Estimados"] - df_merged["Cupos_Usados"]) / df_merged["Cupos_Usados"] * 100

    # MAPE y MAE
    mape = df_merged["Porcentaje_Error"].mean() * 100
    mae = df_merged["Error_Absoluto"].mean()

    # Mostrar tabla ordenada
    df_resultado = df_merged[["Materia", "Cupos_Usados", "Cupos_Estimados", "Error_Absoluto", "Desviacion_%"]]
    df_resultado = df_resultado.sort_values("Desviacion_%", key=lambda x: abs(x), ascending=False)

    # Mostrar resultados
    print(df_resultado.to_string(index=False))
    print(f"\n📊 MAE (promedio de error absoluto en cupos usados): {mae:.2f}")
    print(f"📉 MAPE (porcentaje de error promedio en cupos usados): {mape:.2f}%")

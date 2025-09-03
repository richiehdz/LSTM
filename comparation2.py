# comparation2.py
def comparation2(
    archivo_real="resumen_cupos_2025B.xlsx",
    archivo_pred=None,  # ← ahora es opcional
    archivo_salida="evaluacion_pred_vs_real_2025B.xlsx",
    archivo_hist="oferta_academica_unificada.csv",
    sem_train_max=4050  # 2025A por defecto (YYYYA=YYYY*2, YYYYB=YYYY*2+1)
):
    """
    Compara el dataset real (resumen_cupos_2025B.xlsx) contra predicciones del nuevo semestre.
    - Si `archivo_pred` existe: lo usa (debe tener columnas: Materia, Cupos_Estimados).
    - Si no existe: genera predicciones baseline con el último cupos_usados histórico por Materia
      a partir de `archivo_hist` (<= sem_train_max). Si no hay historial, pone 0.
    """

    import os
    import pandas as pd
    import numpy as np

    # --------------------------
    # 1) Cargar y normalizar REAL
    # --------------------------
    df_real = pd.read_excel(archivo_real)
    df_real["Materia"] = df_real["Materia"].astype(str).str.strip().str.upper()

    for c in ["Total_Cupos", "Total_Secciones", "Residuos_Cupos", "Cupos_Usados"]:
        if c in df_real.columns:
            df_real[c] = pd.to_numeric(df_real[c], errors="coerce")

    if "Cupos_Usados" not in df_real.columns:
        df_real["Cupos_Usados"] = (
            df_real["Total_Cupos"].fillna(0) - df_real["Residuos_Cupos"].fillna(0)
        ).clip(lower=0)

    # --------------------------
    # 2) Obtener PREDICCIONES
    # --------------------------
    df_pred = None
    uso_archivo_pred = False
    if archivo_pred and os.path.exists(archivo_pred):
        # Predicciones provistas por el modelo (Excel)
        df_pred = pd.read_excel(archivo_pred)
        # Normalizar
        if "Materia" not in df_pred.columns or "Cupos_Estimados" not in df_pred.columns:
            raise ValueError(
                f"'{archivo_pred}' debe tener columnas ['Materia','Cupos_Estimados']"
            )
        df_pred["Materia"] = df_pred["Materia"].astype(str).str.strip().str.upper()
        df_pred["Cupos_Estimados"] = pd.to_numeric(
            df_pred["Cupos_Estimados"], errors="coerce"
        ).fillna(0)
        uso_archivo_pred = True
    else:
        # Baseline: usar último cupos_usados histórico por Materia
        if not os.path.exists(archivo_hist):
            raise FileNotFoundError(
                f"No existe '{archivo_pred}' ni '{archivo_hist}'. "
                "Proporciona un archivo de predicciones o genera el histórico con unionDatasets.py"
            )

        hist = pd.read_csv(archivo_hist)
        # Normalizar
        hist["Materia"] = hist["Materia"].astype(str).str.strip().str.upper()
        hist["semestre_numerico"] = pd.to_numeric(hist["semestre_numerico"], errors="coerce")
        hist["cupos_usados"] = pd.to_numeric(hist["cupos_usados"], errors="coerce")

        # Último valor por Materia (≤ sem_train_max)
        last_map = (
            hist[hist["semestre_numerico"] <= sem_train_max]
            .sort_values(["Materia", "semestre_numerico"])
            .groupby("Materia")["cupos_usados"]
            .last()
        )

        # Construir df_pred solo para las materias del REAL
        df_pred = pd.DataFrame({
            "Materia": df_real["Materia"].values
        })
        df_pred["Cupos_Estimados"] = df_pred["Materia"].map(last_map).fillna(0)

    # --------------------------
    # 3) Unir y calcular métricas
    # --------------------------
    dfm = pd.merge(df_real, df_pred, on="Materia", how="left")

    # Por si queda algún NaN en Cupos_Estimados (materia sin mapa)
    dfm["Cupos_Estimados"] = pd.to_numeric(dfm["Cupos_Estimados"], errors="coerce").fillna(0)

    dfm["Error_Absoluto"] = (
        dfm["Cupos_Usados"].astype(float) - dfm["Cupos_Estimados"].astype(float)
    ).abs()

    dfm["Desviacion_%"] = np.where(
        dfm["Cupos_Usados"].astype(float) != 0,
        (dfm["Cupos_Estimados"].astype(float) - dfm["Cupos_Usados"].astype(float))
        / dfm["Cupos_Usados"].astype(float) * 100,
        np.nan
    )

    out_cols = ["Materia", "Total_Cupos", "Cupos_Usados", "Cupos_Estimados", "Error_Absoluto", "Desviacion_%"]
    df_out = dfm[out_cols].copy().reset_index(drop=True)
    df_out.to_excel(archivo_salida, index=False)

    # --------------------------
    # 4) Reporte en consola
    # --------------------------
    mae = df_out["Error_Absoluto"].mean()
    mape = (df_out["Error_Absoluto"] / df_out["Cupos_Usados"].replace(0, np.nan)).mean() * 100

    # Diagnóstico breve
    faltan_pred = df_out["Cupos_Estimados"].isna().sum()
    origen = "archivo de predicciones" if uso_archivo_pred else "baseline (último histórico)"
    print(f"✅ Predicciones usadas desde: {origen}")
    if uso_archivo_pred:
        print(f"   Archivo: {archivo_pred}")
    else:
        print(f"   Histórico: {archivo_hist} (≤ {sem_train_max})")

    print(df_out.sort_values("Desviacion_%", key=lambda s: s.abs(), ascending=False).to_string(index=False))
    print(f"\n📊 MAE:  {mae:.2f}")
    print(f"📉 MAPE: {mape:.2f}%")
    print(f"💾 Guardado: {archivo_salida}")

    return df_out


if __name__ == "__main__":
    comparation2()

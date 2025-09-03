# unionDatasets.py
def union_Datasets():
    import os, re, glob
    import pandas as pd

    print("Iniciando la función de unificación")
    files = glob.glob("datasets_resumidos/*.xlsx")
    if not files:
        raise FileNotFoundError("No se encontraron archivos en 'datasets_resumidos/*.xlsx'")

    partes = []
    for file in files:
        m = re.search(r"(\d{4})([AB])", os.path.basename(file))
        if not m:
            print(f"⚠️ Se omite archivo mal nombrado: {file}")
            continue
        year, ciclo = m.groups()
        sem_num = int(year) * 2 + (0 if ciclo.upper() == "A" else 1)
        sem_ori = f"{year}{ciclo.upper()}"

        df = pd.read_excel(file)
        req = {"Materia","Total_Cupos","Total_Secciones","Residuos_Cupos"}
        faltan = req - set(df.columns)
        if faltan:
            raise ValueError(f"{file} sin columnas {faltan}")

        df["Materia"] = df["Materia"].astype(str).str.strip().str.upper()
        for c in ["Total_Cupos","Total_Secciones","Residuos_Cupos"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["semestre_numerico"]  = sem_num
        df["semestre_original"]  = sem_ori
        partes.append(df)

    df_total = pd.concat(partes, ignore_index=True)
    df_total["cupos_usados"] = (df_total["Total_Cupos"].fillna(0) - df_total["Residuos_Cupos"].fillna(0)).clip(lower=0)

    # Merge con ingresos por semestre
    ruta_ingresos = "cant_alumnos_ingreso_por_semestre.xlsx"
    if os.path.exists(ruta_ingresos):
        ing = pd.read_excel(ruta_ingresos)
        # Renombrado flexible
        rename_map = {}
        for c in ing.columns:
            cl = str(c).lower().strip()
            if cl.startswith("semestre"): rename_map[c] = "Semestre"
            elif "ingres" in cl:         rename_map[c] = "Ingresados"
        ing = ing.rename(columns=rename_map)
        if not {"Semestre","Ingresados"} <= set(ing.columns):
            raise ValueError("El archivo de ingresos debe tener 'Semestre' y 'Ingresados'.")

        ing["Semestre"]   = ing["Semestre"].astype(str).str.strip().str.upper()
        ing["Ingresados"] = pd.to_numeric(ing["Ingresados"], errors="coerce").fillna(0).astype(int)
        ing = ing.groupby("Semestre", as_index=False)["Ingresados"].sum()

        df_total["semestre_original"] = df_total["semestre_original"].astype(str).str.strip().str.upper()
        df_total = (df_total
                    .merge(ing, left_on="semestre_original", right_on="Semestre", how="left")
                    .drop(columns=["Semestre"])
                    .rename(columns={"Ingresados":"nuevos_alumnos"}))
        df_total["nuevos_alumnos"] = df_total["nuevos_alumnos"].fillna(0).astype(int)
    else:
        print("⚠️ No se encontró 'cant_alumnos_ingreso_por_semestre.xlsx'. Se creará 'nuevos_alumnos'=0.")
        df_total["nuevos_alumnos"] = 0

    # LAG por materia (sin fuga)
    df_total = df_total.sort_values(["Materia","semestre_numerico"]).reset_index(drop=True)
    df_total["lag1_cupos_usados"] = df_total.groupby("Materia")["cupos_usados"].shift(1).fillna(0)

    keep = ["Materia","Total_Cupos","Total_Secciones","Residuos_Cupos",
            "semestre_numerico","semestre_original","cupos_usados","nuevos_alumnos","lag1_cupos_usados"]
    falt = [c for c in keep if c not in df_total.columns]
    if falt: raise ValueError(f"Faltan columnas al final: {falt}")

    out_path = "oferta_academica_unificada.csv"
    df_total[keep].to_csv(out_path, index=False, encoding="utf-8")
    print(f"Archivo guardado como '{out_path}'")
    print("Filas:", len(df_total), "| Columnas:", len(keep))
    print("Columnas:", keep)
    print("Función de unificación ejecutada con éxito")

if __name__ == "__main__":
    union_Datasets()

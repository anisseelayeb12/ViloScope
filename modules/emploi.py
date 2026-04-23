import pandas as pd
import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


@st.cache_data(show_spinner=False)
def _charger_dossier():
    candidats = [
        "dossier_complet_2023.csv",
        "dossier_complet-2023.csv",
        "dossier_complet_2024.csv",
        "dossier_complet_2025.csv",
    ]
    for nom in candidats:
        path = os.path.join(DATA_DIR, nom)
        if os.path.exists(path):
            for sep in ["\t", ",", ";"]:
                try:
                    df = pd.read_csv(path, sep=sep, dtype={"CODGEO": str}, low_memory=False)
                    if "CODGEO" in df.columns and len(df.columns) > 5:
                        df["CODGEO"] = df["CODGEO"].astype(str).str.zfill(5)
                        return df
                except Exception:
                    continue
    return None


def get_offres(code_insee):
    df = _charger_dossier()
    if df is None:
        return None, "Fichiers dossier_complet introuvables dans data/"

    code = str(code_insee).zfill(5)
    row = df[df["CODGEO"] == code]
    if row.empty:
        return None, f"Commune {code} non trouvee dans les donnees INSEE"

    row = row.iloc[0]

    def val(col, defaut=0):
        try:
            v = row.get(col, defaut)
            return float(v) if pd.notna(v) else defaut
        except Exception:
            return defaut

    emplois   = val("P20_EMPLT")
    chomeurs  = val("P20_CHOM1564")
    actifs    = val("P20_ACT1564")
    taux_chom = round(chomeurs / actifs * 100, 1) if actifs > 0 else 0

    secteurs = {
        "Agriculture":            val("C20_EMPLT_AGRI"),
        "Industrie":              val("C20_EMPLT_INDUS"),
        "Construction":           val("C20_EMPLT_CONST"),
        "Commerce / Services":    val("C20_EMPLT_CTS"),
        "Administration / Sante": val("C20_EMPLT_APESAS"),
    }
    secteurs = {k: int(v) for k, v in secteurs.items() if v > 0}

    evolution = {}
    if val("P09_EMPLT") > 0:
        evolution["2009"] = int(val("P09_EMPLT"))
    if val("P14_EMPLT") > 0:
        evolution["2014"] = int(val("P14_EMPLT"))
    if emplois > 0:
        evolution["2020"] = int(emplois)

    return {
        "emplois":   int(emplois),
        "chomeurs":  int(chomeurs),
        "taux_chom": taux_chom,
        "secteurs":  secteurs,
        "evolution": evolution,
    }, None

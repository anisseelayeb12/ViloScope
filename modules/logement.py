import pandas as pd
import streamlit as st
import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DVF_PATH  = os.path.join(BASE_DIR, "data", "dvf_filtre.csv")


def _supprimer_accents(texte):
    return unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")


@st.cache_data(show_spinner=False)
def _charger_dvf(mtime=None):
    # mtime est passé comme clé : le cache se recharge si le fichier change
    _ = mtime
    if not os.path.exists(DVF_PATH):
        return None
    df = pd.read_csv(DVF_PATH, dtype={"annee": str})
    df["Commune"] = df["Commune"].str.upper().apply(_supprimer_accents)
    return df


def get_logement(nom_commune, annees=("2023", "2024", "2025")):
    mtime = os.path.getmtime(DVF_PATH) if os.path.exists(DVF_PATH) else None
    df = _charger_dvf(mtime=mtime)
    if df is None:
        return None

    # Même normalisation sur le nom recherché
    nom_upper = _supprimer_accents(nom_commune.upper())
    df_ville  = df[df["Commune"].str.contains(nom_upper, na=False)]

    if df_ville.empty:
        return None

    resultats = {}
    for annee in annees:
        df_an = df_ville[df_ville["annee"] == str(annee)]
        if df_an.empty:
            continue

        apparts = df_an[df_an["Type local"] == "Appartement"]["prix_m2"]
        maisons  = df_an[df_an["Type local"] == "Maison"]["prix_m2"]

        resultats[annee] = {
            "nb_transactions": len(df_an),
            "prix_global":     round(df_an["prix_m2"].median(), 0),
            "prix_appart":     round(apparts.median(), 0) if not apparts.empty else None,
            "prix_maison":     round(maisons.median(), 0) if not maisons.empty else None,
            "nb_apparts":      len(apparts),
            "nb_maisons":      len(maisons),
        }

    return resultats if resultats else None

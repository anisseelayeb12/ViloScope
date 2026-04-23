import pandas as pd
import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMUNES_PATH = os.path.join(BASE_DIR, "data", "communes-france-2025.csv")

@st.cache_data
def charger_communes():
    # Lecture brute sans contrainte de type pour éviter les erreurs de parsing
    df = pd.read_csv(COMMUNES_PATH, low_memory=False)

    # Renommer la colonne index si elle existe sans nom
    if df.columns[0] == "Unnamed: 0":
        df = df.drop(columns=df.columns[0])

    # Conversion explicite des colonnes numériques
    for col in ["population", "superficie_km2", "densite", "latitude_centre", "longitude_centre"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # S'assurer que code_insee est une chaîne de caractères
    df["code_insee"] = df["code_insee"].astype(str).str.zfill(5)

    # Filtre : uniquement les villes de plus de 20 000 habitants
    df = df[df["population"] >= 20000].copy()
    df = df.dropna(subset=["nom_standard", "population"])
    df = df.sort_values("nom_standard").reset_index(drop=True)
    return df

def get_infos_ville(df, nom):
    row = df[df["nom_standard"] == nom].iloc[0]
    return {
        "nom":        row["nom_standard"],
        "population": int(row["population"]),
        "superficie": float(row["superficie_km2"]),
        "densite":    float(row["densite"]),
        "departement": row["dep_nom"],
        "region":     row["reg_nom"],
        "code_insee": str(row["code_insee"]),
        "lat":        float(row["latitude_centre"]),
        "lon":        float(row["longitude_centre"]),
    }

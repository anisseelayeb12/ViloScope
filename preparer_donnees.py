"""
preparer_donnees.py
-------------------
Script à lancer UNE SEULE FOIS avant de démarrer l'application.

Il lit les fichiers DVF bruts (plusieurs millions de lignes),
filtre uniquement les villes de plus de 20 000 habitants,
et sauvegarde un fichier allégé utilisé par l'application.

Lancement :
    python preparer_donnees.py
"""

import pandas as pd
import os
import re
import unicodedata
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

COMMUNES_PATH = os.path.join(DATA_DIR, "communes-france-2025.csv")
OUTPUT_PATH   = os.path.join(DATA_DIR, "dvf_filtre.csv")

ANNEES = [2023, 2024, 2025]

# Colonnes à garder dans les fichiers DVF
COLS_DVF = [
    "Commune",
    "Valeur fonciere",
    "Type local",
    "Surface reelle bati",
    "Date mutation",
]


def supprimer_accents(texte):
    return unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode("utf-8")


def normaliser_commune(nom):
    """Regroupe les arrondissements sous le nom de la ville principale."""
    if re.match(r"PARIS\s+\d", nom):
        return "PARIS"
    if re.match(r"LYON\s+\d", nom):
        return "LYON"
    if re.match(r"MARSEILLE\s+\d", nom):
        return "MARSEILLE"
    return supprimer_accents(nom)


def charger_communes_cibles():
    print("Chargement de la liste des communes cibles...")
    df = pd.read_csv(COMMUNES_PATH, dtype={"code_insee": str}, low_memory=False)
    df = df[df["population"] >= 20000].copy()
    # On garde les noms en majuscule SANS accents pour matcher avec DVF
    noms = set(df["nom_standard"].str.upper().apply(supprimer_accents).tolist())
    # Paris, Lyon, Marseille sont découpées par arrondissements dans DVF
    noms.update(["PARIS", "LYON", "MARSEILLE"])
    print(f"  {len(noms)} villes de plus de 20 000 habitants trouvées.")
    return noms


def traiter_dvf(annee, noms_cibles):
    path = os.path.join(DATA_DIR, f"ValeursFoncieres-{annee}.txt")
    if not os.path.exists(path):
        print(f"  Fichier {annee} introuvable, ignoré.")
        return None

    print(f"  Lecture de ValeursFoncieres-{annee}.txt...")
    debut = time.time()

    # Lecture par morceaux pour éviter de saturer la mémoire
    morceaux = []
    taille_morceau = 200_000
    total_lu = 0
    total_garde = 0

    for morceau in pd.read_csv(
        path,
        sep="|",
        usecols=COLS_DVF,
        dtype=str,
        low_memory=False,
        chunksize=taille_morceau,
    ):
        total_lu += len(morceau)

        # Filtre sur les communes cibles
        masque = morceau["Commune"].str.upper().apply(normaliser_commune).isin(noms_cibles)
        morceau_filtre = morceau[masque].copy()

        if not morceau_filtre.empty:
            # Normaliser le nom stocké (ex: "PARIS 1ER" → "PARIS")
            morceau_filtre["Commune"] = morceau_filtre["Commune"].str.upper().apply(normaliser_commune)
            # Nettoyage des valeurs numériques
            morceau_filtre["Valeur fonciere"] = pd.to_numeric(
                morceau_filtre["Valeur fonciere"].str.replace(",", "."), errors="coerce"
            )
            morceau_filtre["Surface reelle bati"] = pd.to_numeric(
                morceau_filtre["Surface reelle bati"].str.replace(",", "."), errors="coerce"
            )

            # Filtre qualité : surface > 9m², prix > 0
            morceau_filtre = morceau_filtre[
                (morceau_filtre["Valeur fonciere"] > 0) &
                (morceau_filtre["Surface reelle bati"] > 9)
            ]

            morceau_filtre["prix_m2"] = (
                morceau_filtre["Valeur fonciere"] / morceau_filtre["Surface reelle bati"]
            ).round(2)

            # Supprimer les prix aberrants (moins de 100 ou plus de 100 000 €/m²)
            morceau_filtre = morceau_filtre[
                (morceau_filtre["prix_m2"] >= 100) &
                (morceau_filtre["prix_m2"] <= 100_000)
            ]

            morceau_filtre["annee"] = str(annee)
            morceaux.append(morceau_filtre)
            total_garde += len(morceau_filtre)

    duree = round(time.time() - debut, 1)
    print(f"    {total_lu:,} lignes lues, {total_garde:,} conservées ({duree}s)".replace(",", " "))

    return pd.concat(morceaux) if morceaux else None


def main():
    print("\n=== Preparation des donnees DVF ===\n")

    if not os.path.exists(DATA_DIR):
        print("Dossier data/ introuvable. Vérifiez la structure du projet.")
        return

    noms_cibles = charger_communes_cibles()

    tous_les_morceaux = []
    for annee in ANNEES:
        df = traiter_dvf(annee, noms_cibles)
        if df is not None:
            tous_les_morceaux.append(df)

    if not tous_les_morceaux:
        print("\nAucun fichier DVF traité. Vérifiez le dossier data/.")
        return

    print("\nAssemblage et sauvegarde...")
    df_final = pd.concat(tous_les_morceaux, ignore_index=True)
    df_final.to_csv(OUTPUT_PATH, index=False)

    taille_mo = os.path.getsize(OUTPUT_PATH) / 1_000_000
    print(f"  Fichier sauvegardé : dvf_filtre.csv")
    print(f"  Lignes totales     : {len(df_final):,}".replace(",", " "))
    print(f"  Taille             : {taille_mo:.1f} Mo")
    print("\nPreparation terminée. Vous pouvez lancer l'application.")
    print("    streamlit run app.py\n")


if __name__ == "__main__":
    main()

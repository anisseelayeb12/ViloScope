# ViloScope — Comparateur de villes françaises

Application web permettant de comparer deux villes françaises de plus de 20 000 habitants
sur cinq thèmes : données générales, emploi, logement, météo et vie locale.

Développée avec Python et Streamlit.

---

## Installation

### 1. Cloner le dépôt
```
git clone https://github.com/TON_PSEUDO/ViloScope.git
cd ViloScope
```

### 2. Installer les dépendances
```
pip install -r requirements.txt
```

### 3. Configurer les clés API
Créer un fichier `.env` à la racine avec :
```
FT_CLIENT_ID=votre_client_id
FT_CLIENT_SECRET=votre_client_secret
```

### 4. Placer les fichiers de données dans data/
```
communes-france-2025.csv
ValeursFoncieres-2023.txt
ValeursFoncieres-2024.txt
ValeursFoncieres-2025.txt
```

### 5. Préparer les données
```
python preparer_donnees.py
```

### 6. Lancer l'application
```
python -m streamlit run app.py
```

---

## Sources de données

- INSEE : données de population et communes
- DVF (data.gouv.fr) : prix immobiliers par commune
- Open-Meteo : météo et climat (API publique)
- France Travail : offres d'emploi (API OAuth2)
- OpenStreetMap / Overpass API : équipements locaux

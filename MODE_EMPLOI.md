# Mode d'emploi — ViloScope

---

## Ce qu'il faut installer avant de commencer

1. Python 3.10 ou plus récent
   Verifier avec : python --version

2. Les librairies Python du projet
   Ouvrir un terminal dans le dossier ViloScope et taper :
   pip install -r requirements.txt

---

## Placer les fichiers de données

Copier ces fichiers dans le dossier data/ :

   communes-france-2025.csv
   dossier_complet-2023.csv
   dossier_complet_2024.csv
   dossier_complet_2025.csv
   ValeursFoncieres-2023.txt
   ValeursFoncieres-2024.txt
   ValeursFoncieres-2025.txt

---

## Etape obligatoire avant le premier lancement : preparer les données

Les fichiers DVF bruts sont trop volumineux pour être lus à chaque fois.
Ce script les traite une seule fois et génère un fichier allégé.

Dans le terminal, taper :
   python preparer_donnees.py

Attendre la fin du traitement (environ 1 à 3 minutes selon la machine).
Un fichier dvf_filtre.csv sera créé automatiquement dans data/.
Cette étape n'est à faire qu'une seule fois.

---

## Lancer l'application

Après la préparation des données, taper :
   streamlit run app.py

L'application s'ouvre dans le navigateur à l'adresse :
   http://localhost:8501

---

## Utiliser l'application

1. Dans la colonne de gauche, choisir une première ville dans la liste deroulante
2. Choisir une deuxième ville différente
3. Naviguer entre les cinq onglets :
   - General      : population, superficie, densité, region
   - Emploi       : offres d'emploi actives par type de contrat
   - Logement     : prix immobilier au m² sur plusieurs années
   - Meteo        : previsions 7 jours et climat annuel
   - Vie locale   : equipements (restaurants, musees, sport, etc.)

Toutes les villes proposées comptent plus de 20 000 habitants.

---

## En cas de problème

- "dvf_filtre.csv introuvable" : relancer python preparer_donnees.py
- "Données non disponibles"    : vérifier que les fichiers sont bien dans data/
- L'appli ne se lance pas      : vérifier que pip install a été fait
- Offres d'emploi absentes     : vérifier les clés dans le fichier .env

---

## Déploiement en ligne (Streamlit Cloud)

1. Mettre le projet sur GitHub (sans le fichier .env, sans les fichiers DVF bruts)
2. Inclure dvf_filtre.csv dans le dépôt
3. Aller sur https://streamlit.io et connecter le dépôt
4. Dans les paramètres, ajouter les deux variables secrètes :
   FT_CLIENT_ID
   FT_CLIENT_SECRET

import requests
import streamlit as st

SERVEURS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass.karte.io/api/interpreter",
]

# Mapping tag → catégorie affichée
TAG_CATEGORIES = {
    ("amenity", "restaurant"):    "Restaurants",
    ("amenity", "cafe"):          "Cafes et bars",
    ("amenity", "bar"):           "Cafes et bars",
    ("tourism",  "museum"):       "Musees",
    ("amenity", "cinema"):        "Cinemas",
    ("leisure",  "sports_centre"):"Salles de sport",
    ("leisure",  "fitness_centre"):"Salles de sport",
    ("leisure",  "swimming_pool"):"Piscines",
    ("leisure",  "park"):         "Parcs",
    ("tourism",  "hotel"):        "Hotels",
    ("amenity", "pharmacy"):      "Pharmacies",
    ("amenity", "hospital"):      "Hopitaux",
    ("amenity", "clinic"):        "Hopitaux",
}

# Catégories dans l'ordre d'affichage
ORDRE = [
    "Restaurants", "Cafes et bars", "Musees", "Cinemas",
    "Salles de sport", "Piscines", "Parcs", "Hotels",
    "Pharmacies", "Hopitaux",
]


def _construire_query(lat, lon, rayon_m):
    """Une seule requête Overpass pour toutes les catégories."""
    filtres = [
        'node["amenity"~"restaurant|cafe|bar|cinema|pharmacy|hospital|clinic"]',
        'way["amenity"~"restaurant|cafe|bar|cinema|pharmacy|hospital|clinic"]',
        'node["tourism"~"museum|hotel"]',
        'way["tourism"~"museum|hotel"]',
        'node["leisure"~"sports_centre|fitness_centre|swimming_pool|park"]',
        'way["leisure"~"sports_centre|fitness_centre|swimming_pool|park"]',
    ]
    union = "\n".join(f'  {f}(around:{rayon_m},{lat},{lon});' for f in filtres)
    return f'[out:json][timeout:60];\n(\n{union}\n);\nout tags;'


def _compter_par_categorie(elements):
    """Compte les éléments par catégorie à partir des tags OSM."""
    compteurs = {cat: 0 for cat in ORDRE}
    for el in elements:
        tags = el.get("tags", {})
        for (cle, val), categorie in TAG_CATEGORIES.items():
            if tags.get(cle) == val:
                compteurs[categorie] += 1
                break  # un élément = une catégorie
    return compteurs


@st.cache_data(ttl=3600, show_spinner=False)
def get_vie_locale(lat, lon, rayon_m=5000):
    query = _construire_query(lat, lon, rayon_m)

    for serveur in SERVEURS:
        try:
            r = requests.post(
                serveur,
                data={"data": query},
                timeout=65,
                headers={"User-Agent": "ViloScope/1.0"},
            )
            if r.status_code == 200:
                data = r.json()
                elements = data.get("elements", [])
                if elements is not None:
                    return _compter_par_categorie(elements)
        except Exception:
            continue

    # Tous les serveurs ont échoué
    return {cat: 0 for cat in ORDRE}

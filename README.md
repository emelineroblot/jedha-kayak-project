# 🏖️ Projet Kayak - Recommandation de Destinations

**Analyse data science pour recommander les meilleures destinations de vacances en région PACA (Provence-Alpes-Côte d'Azur) en combinant données météorologiques et offres d'hébergements.**

---

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Objectifs](#objectifs)
- [Architecture du Projet](#architecture-du-projet)
- [Étapes du Projet](#étapes-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Résultats](#résultats)
- [Technologies Utilisées](#technologies-utilisées)
- [Auteur](#auteur)

---

## 🎯 Vue d'ensemble

Ce projet analyse **35 villes françaises** pour identifier les **Top 5 destinations** selon :
- ☀️ **Conditions météorologiques** (température, précipitations, ensoleillement)
- 🏨 **Disponibilité et qualité des hébergements** (notes, prix, équipements)
- 🎯 **Score combiné** intégrant météo, qualité et prix

Le système génère des **recommandations personnalisées** sous forme de :
- 📊 Tableaux de données structurés
- 🗺️ Cartes interactives géolocalisées
- 📈 Visualisations analytiques
- 📄 Rapport HTML complet

---

## 🎯 Objectifs

### Objectifs Principaux

1. ✅ **Collecter et traiter** les données météorologiques de 35 villes françaises
2. ✅ **Identifier le Top 5** des destinations selon un score météo composite
3. ✅ **Récupérer les offres d'hébergements** via l'API de Booking.com
4. ✅ **Fusionner et analyser** les données météo + hôtels
5. ✅ **Créer des visualisations** interactives et un rapport final
6. ⏳ **Déployer sur AWS** (optionnel)

### KPIs

- **35 villes** analysées avec données météo complètes
- **Top 5 destinations** identifiées
- **~75 hôtels** récupérés (15 par ville)
- **Score final** combinant météo (40%), qualité (40%), prix (20%)
- **Cartes interactives** avec géolocalisation GPS
- **Rapport HTML** professionnel

---

## 🏗️ Architecture du Projet
```
kayak_project/
│
├── data/
│   ├── raw/                          # Données brutes
│   │   ├── cities.csv                # Liste des 35 villes
│   │   ├── weather_raw.csv           # Données météo brutes
│   │   ├── hotels_top5_all.csv       # Tous les hôtels (Top 5)
│   │   └── hotels/                   # CSV par ville
│   │       ├── hotels_marseille.csv
│   │       ├── hotels_cassis.csv
│   │       └── ...
│   │
│   └── processed/                    # Données traitées
│       ├── city_weather_scores.csv   # Scores météo par ville
│       ├── top5_destinations.csv     # Top 5 destinations
│       ├── final_recommendations.csv # Recommandations finales
│       ├── top20_recommendations.csv # Top 20 hôtels
│       ├── carte_tous_hotels.html    # Carte interactive complète
│       ├── carte_top20.html          # Carte Top 20
│       ├── dashboard_complet.png     # Graphiques d'analyse
│       └── rapport_final.html        # Rapport complet
│
├── notebooks/                        # Notebooks Jupyter
│   ├── 01_weather_analysis.ipynb     # Étape 1 : Analyse météo
│   ├── 02_hotels_scraping.ipynb      # Étape 2 : Scraping hôtels
│   ├── 03_fusion_meteo_hotels.ipynb  # Étape 3 : Fusion données
│   └── 04_visualisations_rapport.ipynb # Étape 4 : Rapport final
│
├── src/                              # Scripts Python
│   ├── __init__.py
│   ├── step1_weather_data.py         # Collecte météo
│   ├── step2_fetch_results.py        # Scraping hôtels
│   └── step3_top_destinations.py     # Calcul Top 5
│
├── requirements.txt                  # Dépendances Python
├── .env.example                      # Template variables d'environnement
├── .gitignore                        # Fichiers ignorés par Git
└── README.md                         # Ce fichier
```

---

## 🚀 Étapes du Projet

### ✅ **Étape 1 : Analyse Météorologique**

**Objectif** : Collecter et analyser les données météo de 35 villes françaises.

**Actions** :
1. Collecte via API météo (OpenWeatherMap ou équivalent)
2. Calcul d'un score composite pondéré :
   - 🌡️ **Température** (30%) : optimal entre 20-28°C
   - ☔ **Précipitations** (30%) : plus c'est faible, mieux c'est
   - ☀️ **Ensoleillement** (25%) : maximum d'heures de soleil
   - 💨 **Vent** (15%) : faible vitesse préférée

**Livrables** :
- `data/raw/weather_raw.csv` : Données brutes
- `data/processed/city_weather_scores.csv` : Scores calculés
- Visualisations : distribution des scores, corrélations
- **Notebook** : `notebooks/01_weather_analysis.ipynb`

**Résultat** : Top 5 destinations identifiées

---

### ✅ **Étape 2 : Scraping des Hébergements**

**Objectif** : Récupérer les offres d'hébergements pour le Top 5.

**Actions** :
1. Scraping via API Booking.com (ApifyClient)
2. Récupération de ~15 hôtels par ville
3. Extraction des données :
   - Nom, URL, note, prix
   - Coordonnées GPS (latitude, longitude)
   - Équipements, images
   - Nombre d'avis

**Livrables** :
- `data/raw/hotels_top5_all.csv` : Tous les hôtels
- `data/raw/hotels/*.csv` : CSV par ville
- **Script** : `src/step2_fetch_results.py`
- **Notebook** : `notebooks/02_hotels_scraping.ipynb`

**KPI** : ~75 hôtels récupérés avec 100% de données GPS

---

### ✅ **Étape 3 : Fusion et Recommandations**

**Objectif** : Créer un système de recommandation combiné.

#### 3.1 Fusion des Données

**Actions** :
1. Merge des datasets météo + hôtels
2. Normalisation des scores sur échelle 0-10
3. Calcul du **score final** :
```
   Score Final = 0.40 × Score Météo 
                + 0.40 × Score Hôtel 
                + 0.20 × Score Prix (inversé)
```

**Livrables** :
- `data/processed/final_recommendations.csv`
- **Notebook** : `notebooks/03_fusion_meteo_hotels.ipynb`

#### 3.2 Visualisations et Rapport

**Actions** :
1. **Cartes interactives** (Folium) :
   - Tous les hôtels géolocalisés
   - Top 20 avec marqueurs numérotés
   - Popups détaillés (score, prix, météo)
   - Légende par code couleur

2. **Dashboard analytique** (8 graphiques) :
   - Distribution des scores par ville
   - Top 10 hôtels
   - Corrélation qualité/prix
   - Impact météo sur le score
   - Répartition par type de propriété

3. **Rapport HTML interactif** :
   - Design moderne et responsive
   - Statistiques clés
   - Top 5 détaillé
   - Cartes intégrées
   - Graphiques d'analyse

**Livrables** :
- `data/processed/carte_tous_hotels.html`
- `data/processed/carte_top20.html`
- `data/processed/dashboard_complet.png`
- `data/processed/rapport_final.html`
- **Notebook** : `notebooks/04_visualisations_rapport.ipynb`

---

### ⏳ **Étape 4 : Déploiement AWS (Optionnel)**

**Objectif** : Déployer les données et visualisations sur le cloud.

**Actions prévues** :
1. **S3** : Stockage des CSV, cartes HTML, rapport
2. **RDS** : Base de données PostgreSQL
3. **Lambda** : Actualisation automatique des données
4. **CloudFront** : CDN pour le rapport HTML

---

## 💻 Installation

### Prérequis

- Python 3.8+
- pip
- Jupyter Notebook
- Compte Apify (pour scraping Booking.com)

### Étapes
```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/kayak_project.git
cd kayak_project

# 2. Créer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter votre clé API Apify
```

### Dépendances Principales
```txt
pandas==2.1.3
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
requests==2.31.0
apify-client==1.7.1
folium==0.15.1
jupyter==1.0.0
python-dotenv==1.0.0
```

---

## 🎮 Utilisation

### Option 1 : Scripts Python (CLI)
```bash
# Étape 1 : Analyse météo
python src/step1_weather_data.py

# Étape 2 : Scraping hôtels
python src/step2_fetch_results.py

# Résultat : Top 5 destinations
python src/step3_top_destinations.py
```

### Option 2 : Notebooks Jupyter (Recommandé)
```bash
# Lancer Jupyter
jupyter notebook

# Exécuter dans l'ordre :
# 1. notebooks/01_weather_analysis.ipynb
# 2. notebooks/02_hotels_scraping.ipynb
# 3. notebooks/03_fusion_meteo_hotels.ipynb
# 4. notebooks/04_visualisations_rapport.ipynb
```

### Voir le Rapport Final
```bash
# Ouvrir le rapport dans votre navigateur
# Windows
start data/processed/rapport_final.html

# macOS
open data/processed/rapport_final.html

# Linux
xdg-open data/processed/rapport_final.html
```

---

## 🛠️ Technologies Utilisées

### Langages et Frameworks

- **Python 3.8+** : Langage principal
- **Pandas** : Manipulation de données
- **NumPy** : Calculs numériques
- **Matplotlib / Seaborn** : Visualisations
- **Folium** : Cartes interactives

### APIs et Services

- **OpenWeatherMap API** : Données météorologiques
- **Apify + Booking.com** : Scraping hôtels
- **Jupyter Notebook** : Analyse interactive

### Outils

- **Git / GitHub** : Versioning
- **VS Code** : Éditeur
- **AWS** (prévu) : Déploiement cloud

---

## 📁 Fichiers Clés

| Fichier | Description | Taille |
|---------|-------------|--------|
| `data/processed/final_recommendations.csv` | Toutes les recommandations | ~75 lignes |
| `data/processed/top20_recommendations.csv` | Top 20 hôtels | 20 lignes |
| `data/processed/carte_tous_hotels.html` | Carte interactive complète | ~500 KB |
| `data/processed/rapport_final.html` | Rapport complet | ~200 KB |
| `notebooks/04_visualisations_rapport.ipynb` | Notebook final | ~2 MB |

---

## 👤 Auteur

**Emeline ROBLOT**
- GitHub : [@emelineroblot](https://github.com/emelineroblot)
- LinkedIn : [Emeline ROBLOT](https://linkedin.com/in/emeline-roblot)
- Email : emeline.roblot@emdigital.fr

---

## 🎯 Quick Start
```bash
# Installation rapide
git clone https://github.com/votre-username/kayak_project.git
cd kayak_project
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt

# Lancer le projet
jupyter notebook notebooks/01_weather_analysis.ipynb

# Voir le rapport final
open data/processed/rapport_final.html
```

---

**Dernière mise à jour** : Novembre 2024

**Status** : ✅ Étapes 1-3 complètes | ⏳ Étape 4 (AWS) en cours

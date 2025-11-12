# 🏖️ Projet Kayak - Recommandation de Destinations

---

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Objectifs](#objectifs)
- [Architecture du Projet](#architecture-du-projet)
- [Étapes du Projet](#étapes-du-projet)
- [Installation](#installation)
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
- ☁️ **Déploiement cloud sur AWS**

---

## 🎯 Objectifs

### Objectifs Principaux

1. ✅ **Collecter et traiter** les données météorologiques de 35 villes françaises
2. ✅ **Identifier le Top 5** des destinations selon un score météo composite
3. ✅ **Récupérer les offres d'hébergements** via l'API de Booking.com
4. ✅ **Fusionner et analyser** les données météo + hôtels
5. ✅ **Créer des visualisations** interactives et un rapport final
6. ✅ **Déployer sur AWS** (S3 + RDS PostgreSQL)

### KPIs

- **35 villes** analysées avec données météo complètes
- **Top 5 destinations** identifiées
- **75 hôtels** récupérés (15 par ville)
- **Score final** combinant météo (40%), qualité (40%), prix (20%)
- **Cartes interactives** avec géolocalisation GPS
- **Rapport HTML** professionnel
- **Base de données PostgreSQL** hébergée sur AWS RDS
- **Fichiers accessibles publiquement** via AWS S3

---

## 🏗️ Architecture du Projet
```
kayak_project/
│
├── data/
│   ├── raw/                                # Données brutes
│   │   ├── cities.csv                      # Liste des 35 villes
│   │   ├── weather_raw.csv                 # Données météo brutes
│   │   ├── hotels_top5_all.csv             # Tous les hôtels (Top 5)
│   │   └── hotels/                         # CSV par ville
│   │       ├── hotels_marseille.csv
│   │       ├── hotels_cassis.csv
│   │       └── ...
│   │
│   └── processed/                          # Données traitées
│       ├── city_weather_scores.csv         # Scores météo par ville
│       ├── top5_destinations.csv           # Top 5 destinations
│       ├── final_recommendations.csv       # Recommandations finales
│       ├── top20_recommendations.csv       # Top 20 hôtels
│       ├── carte_tous_hotels.html          # Carte interactive complète
│       ├── carte_top20.html                # Carte Top 20
│       ├── dashboard_complet.png           # Graphiques d'analyse
│       ├── rapport_final.html              # Rapport complet
│       ├── aws_s3_urls.txt                 # URLs S3 publiques
│       └── rds_import_report.txt           # Rapport import base de données
│
├── notebooks/                              # Notebooks Jupyter
│   ├── 01_data_collection.ipynb            # Étape 1 : Récupération des coordonnées gps des 35 villes
│   ├── 02_data_weather.ipynb               # Étape 2 : Récupération données météo
│   ├── 03_scoring_weather_cities.ipynb     # Étape 3 : Scoring du temps par ville en fonction critères météo 
│   ├── 04_hotels_scraping.ipynb            # Étape 4 : Scraping hôtels 
│   ├── 05_hotels_cleaning.ipynb            # Étape 5 : Enrichissement données hôtels
│   ├── 06_fusion_meteo_hotels.ipynb        # Étape 6 : Fusion data hôtels et météo
│   ├── 07_visualisations_rapport.ipynb     # Étape 7 : Création visualisations et rapport final
│   ├── 08_aws_setup.ipynb                  # Étape 8 : Configuration AWS
│   ├── 09_deploy_s3.ipynb                  # Étape 9 : Déploiement S3
│   ├── 10_setup_rds.ipynb                  # Étape 10 : Configuration RDS
│   └── 11_import_data_rds.ipynb            # Étape 11 : Import données RDS
│
├── src/                                    # Scripts Python
│   ├── fetch_results.py                    # Etape 2 scraping hôtels
│   └── trigger_scrapping.py                # Etape 1 scraping hôtels
│
├── requirements.txt                        # Dépendances Python
├── .env.example                            # Template variables d'environnement
├── .gitignore                              # Fichiers ignorés par Git
└── README.md                               # Ce fichier
```

---

## 🚀 Étapes du Projet

### ✅ **Étape 1 : Analyse Météorologique**

**Objectif** : Collecter et analyser les données météo de 35 villes françaises.

**Actions** :
1. Collecte via API météo (OpenWeatherMap)
2. Calcul d'un score composite pondéré :
   - 🌡️ **Température** (30%) : optimal entre 20-28°C
   - ☔ **Précipitations** (30%) : plus c'est faible, mieux c'est
   - ☀️ **Ensoleillement** (25%) : maximum d'heures de soleil
   - 💨 **Vent** (15%) : faible vitesse préférée

**Résultat** : Top 5 destinations identifiées

---

### ✅ **Étape 2 : Scraping des Hébergements**

**Objectif** : Récupérer les offres d'hébergements pour le Top 5.

**Actions** :
1. Scraping via API Booking.com (BrightData)
2. Récupération de ~15 hôtels par ville
3. Extraction des données :
   - Nom, URL, note, prix
   - Coordonnées GPS (latitude, longitude)
   - Équipements, images
   - Nombre d'avis

**Résultat** : 75 hôtels récupérés avec 100% de données GPS

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

---

### ✅ **Étape 4 : Déploiement AWS**

**Objectif** : Déployer les données et visualisations sur le cloud AWS.

#### 4.1 Configuration AWS

**Actions** :
1. Configuration des credentials AWS (Access Key, Secret Key)
2. Vérification de la connexion S3 et RDS
3. Test des permissions IAM

---

#### 4.2 Déploiement S3

**Actions** :
1. Upload des fichiers vers S3 :
   - Rapport HTML final
   - Cartes interactives
   - Graphiques et dashboards
   - Données CSV
2. Configuration de l'accès public via Bucket Policy
3. Génération des URLs publiques

**Résultat** : 
```
📄 Rapport Final : https://251107-140505-jedha-kayak-project.s3.eu-west-3.amazonaws.com/rapport_final.html
🗺️ Carte Complète : https://251107-140505-jedha-kayak-project.s3.eu-west-3.amazonaws.com/cartes/carte_tous_hotels.html
🏆 Carte Top 20 : https://251107-140505-jedha-kayak-project.s3.eu-west-3.amazonaws.com/cartes/carte_top20.html
```

---

#### 4.3 Configuration RDS PostgreSQL

**Actions** :
1. Connexion à l'instance RDS existante
2. Création du schéma de base de données :
   - Table `cities` : Informations des villes
   - Table `hotels` : Catalogue des hôtels
   - Table `recommendations` : Recommandations finales
   - Table `weather_history` : Historique météo
3. Création de vues SQL pour requêtes rapides :
   - `top_recommendations` : Classement complet
   - `city_statistics` : Statistiques par ville
   - `best_hotels_by_city` : Meilleurs hôtels par ville

---

#### 4.4 Import des Données

**Actions** :
1. Import des villes (5 destinations)
2. Import des hôtels (75 hôtels)
3. Import des recommandations (74 entrées)
4. Import de l'historique météo (5 enregistrements)
5. Vérification de l'intégrité des données

**Statistiques finales** :
```
✅ 5 villes importées
✅ 75 hôtels importés
✅ 74 recommandations importées
✅ 5 enregistrements météo
💾 Taille de la base : ~8 MB
```

---

## 💻 Installation

### Prérequis

- Python 3.8+
- pip
- Jupyter Notebook
- Compte BrightData (pour scraping Booking.com)
- Compte AWS (pour déploiement cloud)

### Étapes
```bash
# 1. Cloner le dépôt
git clone https://github.com/emelineroblot/kayak_project.git
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
# Éditer .env et ajouter :
# - Clé API BrightData
# - Credentials AWS (Access Key, Secret Key)
# - Configuration RDS (Host, Database, User, Password)
```

---

## 👤 Auteur

**Emeline ROBLOT**
- 🌐 GitHub : [@emelineroblot](https://github.com/emelineroblot)
- 💼 LinkedIn : [Emeline ROBLOT](https://linkedin.com/in/emeline-roblot)
- 📧 Email : emeline.roblot@emdigital.fr

---

**Dernière mise à jour** : Novembre 2025

**Status** : ✅ **PROJET COMPLET** - Toutes les étapes terminées (Étapes 1-4)


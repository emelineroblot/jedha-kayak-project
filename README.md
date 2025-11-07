# 🏖️ Kayak Travel Recommendation Project

Projet de recommandation de destinations et hôtels en France basé sur les données météo et Booking.com.

## 📋 Table des Matières

- [Description du Projet](#description-du-projet)
- [Objectifs](#objectifs)
- [Technologies Utilisées](#technologies-utilisées)
- [Architecture du Projet](#architecture-du-projet)
- [Installation](#installation)
- [Étapes du Projet](#étapes-du-projet)
- [Utilisation](#utilisation)
- [Livrables](#livrables)
- [Auteur](#auteur)

---

## 📖 Description du Projet

Kayak est un moteur de recherche de voyages qui aide les utilisateurs à planifier leurs prochaines vacances au meilleur prix.

**Contexte :** 
- 70% des utilisateurs souhaitent plus d'informations sur leurs destinations
- Les utilisateurs sont méfiants envers les contenus de marques inconnues

**Solution :** Créer une application de recommandation basée sur :
- Données météorologiques réelles
- Informations sur les hôtels disponibles

---

## 🎯 Objectifs

Le projet vise à :

1. **Scraper des données** sur 35 destinations françaises
2. **Récupérer les données météo** pour chaque destination (prévisions sur 6 jours)
3. **Scraper les informations hôtels** depuis Booking.com
4. **Stocker les données** dans un Data Lake (AWS S3)
5. **Créer un Data Warehouse** (AWS RDS) avec des données nettoyées
6. **Visualiser les résultats** : Top 5 destinations et Top 20 hôtels

---

## 🛠️ Technologies Utilisées

### Langages & Frameworks
- **Python 3.10+**
- **Pandas** - Manipulation de données
- **NumPy** - Calculs numériques
- **Requests** - Appels API

### APIs
- **Nominatim** (OpenStreetMap) - Géocodage des villes (gratuit)
- **OpenWeatherMap API** - Données météorologiques (plan gratuit)

### Web Scraping
- **BeautifulSoup4** - Parsing HTML
- **Selenium** - Scraping dynamique

### Cloud & Storage
- **AWS S3** - Data Lake
- **AWS RDS (PostgreSQL)** - Data Warehouse
- **boto3** - SDK AWS pour Python

### Database
- **SQLAlchemy** - ORM Python
- **psycopg2** - Driver PostgreSQL

### Visualisation
- **Plotly** - Cartes interactives
- **Matplotlib** - Graphiques
- **Seaborn** - Visualisations statistiques

### Environnement
- **Jupyter Notebook** - Développement interactif
- **python-dotenv** - Gestion des variables d'environnement

---

## 🏗️ Architecture du Projet
```
kayak_project/
│
├── config/
│   └── .env                          # Variables d'environnement (clés API)
│
├── data/
│   ├── raw/                          # Données brutes
│   │   ├── cities_coordinates.csv    # ✅ Coordonnées GPS des 35 villes
│   │   └── weather_forecast_6days.csv # ✅ Données météo (6 jours)
│   │
│   └── processed/                    # Données nettoyées
│       ├── city_weather_scores.csv   # ✅ Scores météo de toutes les villes
│       ├── top5_destinations.csv     # ✅ Top 5 des meilleures destinations
│       └── weather_analysis_report.txt # ✅ Rapport d'analyse complet
│
├── notebooks/
│   └── 01_data_collection.ipynb      # ✅ Collecte des données
│
├── src/
│   └── (scripts Python à venir)
│
├── visualizations/
│   ├── weather_distributions.png     # ✅ Distributions des variables météo
│   ├── top10_weather_scores.png      # ✅ Graphique Top 10 destinations
│   ├── top5_destinations_map.html    # ✅ Carte interactive Top 5
│   ├── weather_scores_heatmap.png    # ✅ Évolution des scores sur 6 jours
│   └── top5_radar_comparison.html    # ✅ Comparaison radar du Top 5
│
├── .gitignore                        # Fichiers à ignorer
├── README.md                         # Ce fichier
└── requirements.txt                  # Dépendances Python
```

---

## 📦 Installation

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/kayak-project.git
cd kayak-project
```

### 2. Créer l'Environnement Virtuel

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux :**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les Variables d'Environnement

Créez un fichier `config/.env` avec vos clés API :
```env
# API Keys
OPENWEATHER_API_KEY=votre_cle_api_openweathermap

# AWS Credentials
AWS_ACCESS_KEY_ID=votre_access_key_id
AWS_SECRET_ACCESS_KEY=votre_secret_access_key
AWS_REGION=eu-west-3
AWS_S3_BUCKET=kayak-project-data-2024

# Database (RDS)
DB_HOST=votre-endpoint-rds.eu-west-3.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=admin
DB_PASSWORD=votre_mot_de_passe
```

### 5. Obtenir les Clés API

#### OpenWeatherMap (Gratuit)
1. Créez un compte sur [OpenWeatherMap](https://openweathermap.org/)
2. Allez dans **API keys**
3. Copiez votre clé API
4. ⏰ Attendez 1-2 heures pour l'activation

#### AWS (12 mois gratuits)
1. Créez un compte [AWS Free Tier](https://aws.amazon.com/free/)
2. Créez un utilisateur IAM avec les permissions :
   - `AmazonS3FullAccess`
   - `AmazonRDSFullAccess`
3. Téléchargez les credentials (Access Key + Secret Key)

---

## 🚀 Étapes du Projet

### ✅ Phase 1 : Préparation & Configuration (TERMINÉ)

#### Étape 1.1 : Setup de l'Environnement
- [x] Création de la structure de dossiers
- [x] Environnement virtuel Python créé
- [x] Installation des librairies
- [x] Configuration Git
- [x] Fichier .gitignore créé

#### Étape 1.2 : Obtention des Accès
- [x] Compte OpenWeatherMap créé
- [x] Clé API OpenWeatherMap obtenue
- [x] Compte AWS créé (Free Tier)
- [x] Utilisateur IAM configuré
- [x] Bucket S3 créé
- [x] Instance RDS PostgreSQL créée
- [x] Fichier .env configuré

---

### ✅ Phase 2 : Collecte des Données Météo (TERMINÉ)

#### Étape 2.1 : Géocodage des Villes
- [x] Liste des 35 villes françaises définie
- [x] Fonction de géocodage avec Nominatim créée
- [x] Coordonnées GPS récupérées pour toutes les villes
- [x] DataFrame `df_cities` créé avec city_id
- [x] Fichier `cities_coordinates.csv` sauvegardé

**Résultat :**
- 📁 `data/raw/cities_coordinates.csv`
- 📊 35 villes géocodées
- 🗂️ Colonnes : city_id, city, latitude, longitude, display_name

---

#### Étape 2.2 : Récupération des Données Météo
- [x] Fonction `get_weather_6days()` créée
- [x] Météo actuelle (jour 0) récupérée pour chaque ville
- [x] Prévisions 5 jours récupérées via API gratuite
- [x] DataFrame `df_weather` créé avec toutes les données
- [x] Fusion avec city_id effectuée
- [x] Fichier `weather_forecast_6days.csv` sauvegardé

**Résultat :**
- 📁 `data/raw/weather_forecast_6days.csv`
- 📊 210 enregistrements (35 villes × 6 jours)
- 🗂️ Données : températures, humidité, pluie, vent, nuages

**Données météo collectées :**
| Colonne | Description |
|---------|-------------|
| city_id | Identifiant unique de la ville |
| city | Nom de la ville |
| day | Numéro du jour (0-5) |
| date | Date de la prévision |
| temp_min | Température minimale (°C) |
| temp_max | Température maximale (°C) |
| temp_avg | Température moyenne (°C) |
| humidity | Humidité (%) |
| pop | Probabilité de précipitations (%) |
| rain | Volume de pluie (mm) |
| wind_speed | Vitesse du vent (m/s) |
| clouds | Couverture nuageuse (%) |
| weather_description | Description météo (français) |

---

#### Étape 2.3 : Scoring Météo et Identification du Top 5
- [x] Critères de "beau temps" définis
- [x] Fonction de scoring créée (score sur 100)
- [x] Scores calculés pour chaque jour de chaque ville
- [x] Score moyen calculé par ville (sur 6 jours)
- [x] Top 5 des meilleures destinations identifié
- [x] Visualisations créées (graphiques + cartes)
- [x] Rapport d'analyse généré

**Critères de scoring (total 100 points) :**
- 🌡️ Température idéale (18-28°C) : **25 points**
- 🌧️ Faible probabilité de pluie : **25 points**
- 💧 Peu de volume de pluie : **20 points**
- 💧 Humidité modérée (40-70%) : **10 points**
- 💨 Vent faible (< 5 m/s) : **10 points**
- ☁️ Ciel dégagé (< 50% nuages) : **10 points**

**Résultat :**
- 📁 `data/processed/city_weather_scores.csv` (35 villes classées)
- 📁 `data/processed/top5_destinations.csv` (Top 5)
- 📁 `data/processed/weather_analysis_report.txt` (Rapport)
- 📊 5 visualisations créées

**Visualisations générées :**
1. 📊 Distributions des variables météo
2. 📊 Graphique Top 10 destinations (barres)
3. 🗺️ Carte interactive du Top 5 (Plotly)
4. 📊 Heatmap évolution des scores sur 6 jours
5. 📊 Radar chart comparaison détaillée du Top 5

---

### 🔄 Phase 3 : Scraping des Données Hôtels (EN COURS)

#### Étape 3.1 : Scoring Météo (PROCHAINE ÉTAPE)
- [ ] Définir les critères de "beau temps"
- [ ] Calculer un score météo pour chaque ville
- [ ] Identifier le Top 5 des meilleures destinations

#### Étape 3.2 : Scraping Booking.com
- [ ] Analyser la structure de Booking.com
- [ ] Créer le scraper avec BeautifulSoup/Selenium
- [ ] Scraper les hôtels du Top 5 des villes
- [ ] Récupérer : nom, URL, coordonnées, score, description

---

### 📋 Phase 4 : Data Lake (À VENIR)

- [ ] Fusionner les données météo et hôtels
- [ ] Upload du CSV final vers S3
- [ ] Vérification de l'intégrité des données

---

### 🗄️ Phase 5 : Data Warehouse (À VENIR)

- [ ] Design du schéma SQL (tables cities et hotels)
- [ ] Extraction des données depuis S3
- [ ] Transformation et nettoyage
- [ ] Chargement dans RDS PostgreSQL

---

### 📊 Phase 6 : Visualisations (À VENIR)

- [ ] Carte interactive Top 5 destinations (Plotly)
- [ ] Carte interactive Top 20 hôtels (Plotly)
- [ ] Dashboard avec métriques clés

---

## 💻 Utilisation

### Lancer Jupyter Notebook
```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Lancer Jupyter
jupyter notebook
```

### Exécuter le Notebook de Collecte

1. Ouvrez `notebooks/01_data_collection.ipynb`
2. Changez le kernel vers **"Python (Kayak Project)"**
3. Exécutez les cellules dans l'ordre

---

## 📦 Livrables

### ✅ Livrables Actuels

1. **Fichier CSV - Coordonnées des Villes**
   - 📁 `data/raw/cities_coordinates.csv`
   - 35 villes avec latitude/longitude

2. **Fichier CSV - Données Météo**
   - 📁 `data/raw/weather_forecast_6days.csv`
   - 210 prévisions météo (35 villes × 6 jours)

3. **Fichier CSV - Scores Météo**
   - 📁 `data/processed/city_weather_scores.csv`
   - Classement des 35 villes avec scores

4. **Fichier CSV - Top 5 Destinations**
   - 📁 `data/processed/top5_destinations.csv`
   - Les 5 meilleures destinations identifiées

5. **Rapport d'Analyse Météo**
   - 📁 `data/processed/weather_analysis_report.txt`
   - Synthèse complète avec statistiques

6. **Visualisations**
   - 📊 5 graphiques et cartes interactives
   - Formats : PNG et HTML interactif

### 🔜 Livrables à Venir

3. **Fichier CSV - Données Complètes**
   - Données météo + hôtels enrichies
   - Stockage sur AWS S3

4. **Base de Données SQL**
   - AWS RDS PostgreSQL
   - Tables cities et hotels

5. **Visualisations**
   - Carte Top 5 destinations
   - Carte Top 20 hôtels

---

## 📊 Scope du Projet

Le projet se concentre sur les **35 meilleures villes françaises** selon OneWeekIn.com :
```python
cities = [
    "Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen",
    "Paris", "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg",
    "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy",
    "Grenoble", "Lyon", "Gorges du Verdon", "Bormes les Mimosas", "Cassis",
    "Marseille", "Aix en Provence", "Avignon", "Uzes", "Nimes",
    "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", 
    "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "La Rochelle"
]
```

---

## 🚨 Limitations & Notes

### APIs Gratuites
- **OpenWeatherMap** : 1000 appels/jour (plan gratuit)
  - API utilisée : "5 Day / 3 Hour Forecast" (gratuite)
  - Limitation : 5-6 jours de prévisions au lieu de 7
  
- **Nominatim** : 1 requête/seconde maximum

### Coûts AWS (Free Tier)
- **S3** : 5 GB gratuits (largement suffisant)
- **RDS** : 750h/mois gratuits pendant 12 mois
- ⚠️ Surveillez votre usage pour rester dans les limites gratuites

### Scraping
- Booking.com peut bloquer le scraping intensif
- Utilisez des délais entre les requêtes (rate limiting)
- Respectez le fichier robots.txt

---

## 🔒 Sécurité

**⚠️ IMPORTANT :**
- Ne JAMAIS commiter le fichier `.env` sur Git
- Ne JAMAIS partager vos clés API publiquement
- Vérifiez que `.env` est bien dans `.gitignore`
- Utilisez des credentials IAM avec permissions limitées

---

## 📝 Journal des Modifications

### Version 0.2 - 2025-11-07
- ✅ Collecte des données météo terminée (6 jours de prévisions)
- ✅ 210 enregistrements météo sauvegardés
- ✅ Documentation mise à jour

### Version 0.1 - 2025-11-07
- ✅ Configuration initiale du projet
- ✅ Géocodage de 35 villes françaises
- ✅ Structure du projet créée
- ✅ Accès API et AWS configurés

---

## 🐛 Problèmes Connus & Solutions

### 1. Erreur 401 - OpenWeatherMap API
**Problème :** L'API One Call (7 jours) n'est plus gratuite

**Solution :** Utilisation de l'API "5 Day Forecast" (gratuite) → 6 jours de prévisions

### 2. Erreur "module not found" dans Jupyter
**Problème :** Jupyter utilise un kernel différent de l'environnement virtuel

**Solution :**
```bash
pip install ipykernel
python -m ipykernel install --user --name=kayak_env --display-name "Python (Kayak Project)"
```
Puis changer le kernel dans Jupyter

### 3. RDS Connection Timeout
**Problème :** RDS pas accessible publiquement

**Solution :** 
1. Modifier RDS : "Publicly accessible" = Yes
2. Configurer Security Group : autoriser port 5432 depuis votre IP

---

## 🤝 Contribution

Ce projet est réalisé dans le cadre d'une formation en Data Science.

---

## 📚 Ressources Utiles

### Documentation APIs
- [OpenWeatherMap API Docs](https://openweathermap.org/api)
- [Nominatim API Docs](https://nominatim.org/release-docs/develop/api/Overview/)

### Documentation AWS
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

### Tutoriels
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 📧 Contact

**Emeline ROBLOT**
- GitHub: [@emelineroblot](https://github.com/emelineroblot)
- Email: emeline.roblot@emdigital.fr

---

## 📄 Licence

Ce projet est réalisé à des fins éducatives dans le cadre d'une formation en Data Science.

---

## 🎯 Prochaines Étapes

1. **Étape 2.3** : Calculer un score météo et identifier le Top 5 destinations
2. **Étape 3** : Scraper les données hôtels depuis Booking.com
3. **Étape 4** : Upload des données vers AWS S3
4. **Étape 5** : Création du Data Warehouse sur RDS
5. **Étape 6** : Visualisations interactives avec Plotly

---

**Dernière mise à jour :** 8 novembre 2025

**Statut du projet :** 🟢 En cours - Phase 2 terminée (Scoring météo)

**Progression :** ████████████░░░░░░░░ 60%
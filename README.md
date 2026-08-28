# 🏖️ Projet Kayak - Recommandation de Destinations

---

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Résultats](#-résultats)
- [Objectifs](#-objectifs)
- [Architecture du Projet](#-architecture-du-projet)
- [Étapes du Projet](#-étapes-du-projet)
- [Livrables en ligne](#-livrables-en-ligne)
- [Installation](#-installation)
- [Limites assumées](#-limites-assumées)
- [Stack technique](#-stack-technique)
- [Auteur](#-auteur)

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

## 📈 Résultats

Collecte du **11/11/2025** : prévisions OpenWeather sur 6 jours pour les 35 villes, puis
tarifs Booking pour un séjour de **2 nuits à J+30, 2 adultes**.

### Top 5 des destinations retenues

| # | Ville | Score météo /100 | Temp. moy. | Pluie (vol.) | Nuages |
|---|---|---|---|---|---|
| 1 | **Aix en Provence** | **76,33** | 13,0 °C | 0,0 mm | 59 % |
| 2 | **Marseille** | **76,17** | 15,1 °C | 0,15 mm | 61 % |
| 3 | **Bormes les Mimosas** | **76,00** | 13,0 °C | 0,0 mm | 50 % |
| 4 | **Cassis** | **73,67** | 14,3 °C | 0,34 mm | 57 % |
| 5 | **Avignon** | **71,83** | 12,9 °C | 0,0 mm | 52 % |

Les 5 villes retenues sont toutes en Provence, et les scores se tiennent en **4,5 points**
(71,83 → 76,33). C'est précisément pour cela que le score final utilise une échelle absolue
et non une normalisation min-max — voir [Étape 3](#31-fusion-des-données).

### Top 10 des hébergements recommandés

`Score final = 0,40 × météo + 0,40 × note Booking + 0,20 × prix (inversé)`

| # | Hébergement | Ville | Note | €/pers/nuit | Score final |
|---|---|---|---|---|---|
| 1 | La Villa Rustica | Aix en Provence | 9,8 | 25,27 € | **8,87** |
| 2 | La Favière proche de la plage | Bormes les Mimosas | 9,5 | 26,13 € | 8,72 |
| 3 | Romantic getaway in Bormes | Bormes les Mimosas | 9,5 | 32,18 € | 8,60 |
| 4 | Apartment-NO elevator-Free private parking | Avignon | 9,6 | 27,00 € | 8,57 |
| 5 | L'Oriflamme | Avignon | 9,5 | 29,37 € | 8,49 |
| 6 | Le Mas de la Palmeraie - Studio | Bormes les Mimosas | 9,7 | 42,76 € | 8,46 |
| 7 | Centre Palais des Papes B2 Clim | Avignon | 9,1 | 24,34 € | 8,43 |
| 8 | Le Bosquet | Cassis | 9,3 | 34,89 € | 8,37 |
| 9 | La Cigale du Port | Cassis | 9,0 | 29,91 € | 8,35 |
| 10 | Le petit cassis | Cassis | 8,7 | 25,63 € | 8,31 |

**Aucun hôtel marseillais dans le Top 10** alors que Marseille est 2ᵉ au score météo — son
meilleur établissement n'arrive qu'au 12ᵉ rang. La météo ne départage presque rien (0,16 point
d'écart avec Aix), et c'est la **qualité** qui tranche : Marseille affiche la note médiane la
plus basse des cinq villes (**8,30** contre 8,50 à 8,70 ailleurs), malgré le prix médian le
plus bas (**35,31 €** par personne et par nuit). Les 40 % de poids « qualité » pèsent plus que
les 20 % de « prix ».

### Le pipeline en chiffres

| Indicateur | Valeur |
|---|---|
| Villes analysées | **35** (dont 5 retenues) |
| Hôtels collectés | 75 → **74** après dédoublonnage sur `listing_id` |
| Hôtels classés | **72** (2 sans aucun avis, non classables) |
| Livrable `kayak_enriched.csv` | **104 lignes × 26 colonnes** (74 lignes hôtel + 30 villes sans hôtel) |
| Prix par personne et par nuit | 18,14 € (min) · **40,60 € (médiane)** · 431,53 € (max) |
| Base RDS PostgreSQL | 4 tables, 3 vues, **8,4 Mo** |
| Objets publiés sur S3 | **19** |

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
- **75 hôtels** collectés (15 par ville), **74** après déduplication, **72** classés
- **Score final** combinant météo (40%), qualité (40%), prix (20%)
- **Cartes interactives** avec géolocalisation GPS
- **Rapport HTML** professionnel
- **Base de données PostgreSQL** hébergée sur AWS RDS
- **Fichiers accessibles publiquement** via AWS S3

---

## 🏗️ Architecture du Projet
```
jedha-kayak-project/
│
├── data/
│   ├── raw/                                # Données brutes
│   │   ├── cities_coordinates.csv          # Coordonnées GPS des 35 villes
│   │   ├── hotels_top5_all.csv             # Tous les hôtels du Top 5, consolidés
│   │   ├── hotels/                         # CSV par ville
│   │   │   ├── hotels_marseille.csv
│   │   │   ├── hotels_cassis.csv
│   │   │   └── ...
│   │   └── hotels_json/                    # Réponses BrightData brutes, par ville
│   │       ├── marseille_raw.json
│   │       └── ...
│   │
│   └── processed/                          # Données traitées
│       ├── kayak_enriched.csv              # ⭐ LIVRABLE : météo + hôtels, 35 villes
│       ├── city_weather_scores.csv         # Scores météo des 35 villes
│       ├── top5_destinations.csv           # Top 5 destinations
│       ├── hotels_cleaned.csv              # Hôtels après parsing et dédoublonnage
│       ├── final_recommendations.csv       # Recommandations finales (72 classées)
│       ├── top20_recommendations.csv       # Top 20 hôtels
│       ├── carte_destinations.html         # Carte du Top 5 des destinations
│       ├── carte_tous_hotels.html          # Carte interactive complète
│       ├── carte_top20.html                # Carte Top 20
│       ├── analysis_fusion.png             # Planche d'analyse de la fusion
│       ├── charts/                         # Les 7 graphiques du dashboard
│       │   ├── scores_par_ville.png
│       │   ├── top10.png
│       │   ├── qualite_prix.png
│       │   └── ...
│       ├── rapport_final.html              # Rapport complet
│       ├── aws_s3_urls.txt                 # URLs S3 publiques (lisible)
│       └── aws_s3_urls.json                # URLs S3 publiques (exploitable)
│
├── notebooks/                              # Notebooks Jupyter
│   ├── 01_data_collection.ipynb            # Étape 1 : Coordonnées GPS des 35 villes
│   ├── 02_data_weather.ipynb               # Étape 2 : Récupération données météo
│   ├── 03_scoring_weather_cities.ipynb     # Étape 3 : Scoring météo par ville
│   ├── 04_hotels_scraping.ipynb            # Étape 4 : Scraping hôtels
│   ├── 05_hotels_cleaning.ipynb            # Étape 5 : Parsing et nettoyage hôtels
│   ├── 06_fusion_meteo_hotels.ipynb        # Étape 6 : Fusion météo + hôtels
│   ├── 07_visualisations_rapport.ipynb     # Étape 7 : Visualisations et rapport
│   ├── 08_aws_setup.ipynb                  # Étape 8 : Configuration AWS
│   ├── 09_deploy_s3.ipynb                  # Étape 9 : Déploiement S3
│   ├── 10_setup_rds.ipynb                  # Étape 10 : Configuration RDS
│   └── 11_import_data_rds.ipynb            # Étape 11 : Import S3 → RDS
│
├── visualizations/                         # Sorties de l'analyse météo (étape 3)
│   ├── top5_destinations_map.html          # Carte Plotly des 35 villes scorées
│   ├── top5_radar_comparison.html          # Radar comparatif du Top 5
│   ├── weather_scores_heatmap.png
│   └── ...
│
├── src/                                    # Scripts Python
│   ├── config.py                           # Constantes partagées (séjour, taux de change)
│   ├── trigger_scraping.py                 # Scraping hôtels : déclenchement BrightData
│   ├── fetch_results.py                    # Scraping hôtels : récupération et parsing
│   ├── reparse_hotels.py                   # Reparse des JSON bruts sans rappeler l'API
│   └── recover_city_weather.py             # Reconstruction des scores météo des 35 villes
│
├── config/
│   └── .env.example                        # Template des variables d'environnement
│
├── requirements.txt                        # Dépendances Python
├── .gitignore                              # Fichiers ignorés par Git
└── README.md                               # Ce fichier
```

> **Ce qui est versionné, et pourquoi.** Les livrables de `data/processed/` sont dans le dépôt :
> un jury qui clone doit pouvoir relire les résultats sans rejouer le pipeline ni disposer de
> clés d'API. En revanche `data/raw/cities_coordinates.csv` est régénéré par le notebook 01, et
> le fichier `config/.env` (secrets) n'est évidemment pas versionné.

---

## 🚀 Étapes du Projet

### ✅ **Étape 1 : Analyse Météorologique**

**Objectif** : Collecter et analyser les données météo de 35 villes françaises.

**Actions** :
1. Collecte via API météo (OpenWeatherMap)
2. Calcul d'un score composite pondéré (total 100 points) :
   - 🌡️ **Température** (25 pts) : optimal entre 20-25°C
   - ☔ **Probabilité de pluie** (25 pts) : plus c'est faible, mieux c'est
   - 💧 **Volume de pluie** (20 pts) : équivalent 24 h, 0 mm = maximum
   - 💦 **Humidité** (10 pts) : optimal entre 40 et 60%
   - 💨 **Vent** (10 pts) : faible vitesse préférée
   - ☁️ **Couverture nuageuse** (10 pts) : ciel dégagé préféré

   > Les journées de prévision trop tronquées (moins de 3 créneaux de 3 h) sont
   > écartées, et le volume de pluie est ramené à un équivalent 24 h : sans cela,
   > une journée partielle affiche mécaniquement moins de pluie qu'une journée
   > complète.

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

**Résultat** : 75 hôtels collectés, 74 après suppression du doublon détecté sur
`listing_id`, 100% de données GPS. Deux établissements sans aucun avis sont conservés
dans les données mais exclus du classement (une note absente n'est pas un 0/10).

> ⚠️ BrightData ignore le paramètre `currency: EUR` et renvoie des montants **en USD**,
> pour la **durée totale du séjour** (2 nuits). Les prix sont donc reconstruits au
> parsing : offre la moins chère de l'établissement, ramenée à la nuit et à la personne,
> puis convertie au taux BCE du jour de la collecte (1 USD = 0,86393 EUR au 11/11/2025).
> Ces constantes sont centralisées dans `src/config.py` pour que le déclenchement du
> scraping et le parsing ne puissent pas diverger.

---

### ✅ **Étape 3 : Fusion et Recommandations**

**Objectif** : Créer un système de recommandation combiné.

#### 3.1 Fusion des Données

**Actions** :
1. Merge des datasets météo + hôtels
2. Passage de chaque dimension sur une échelle **absolue** 0-10 :
   - météo : score sur 100 ÷ 10
   - qualité : note Booking, déjà sur 10
   - prix : échelle linéaire inversée et bornée sur le prix par personne et par nuit
     (20 € → 10/10, 120 € et au-delà → 0/10)
3. Calcul du **score final** :
```
   Score Final = 0.40 × Score Météo
                + 0.40 × Score Hôtel
                + 0.20 × Score Prix (inversé)
```

> Une normalisation **min-max** avait initialement été utilisée. Comme le score météo
> ne prend que 5 valeurs comprises entre 71,83 et 76,33, elle étirait 4,5 points d'écart
> réel sur toute la plage 0-10 : la ville la moins bien classée perdait mécaniquement
> 4 points de score final, et le classement départageait des villes plutôt que des
> hôtels. L'échelle absolue conserve la proportion réelle des écarts.
>
> Quand le prix est absent, son poids de 20 % est redistribué sur les deux autres
> dimensions plutôt que compté comme un zéro.

#### 3.2 Visualisations et Rapport

**Actions** :
1. **Cartes interactives** (Folium) :
   - Carte du Top 5 des destinations
   - Tous les hôtels géolocalisés
   - Top 20 avec marqueurs numérotés
   - Popups détaillés (score, prix, météo)
   - Légende par code couleur

2. **Dashboard analytique** — 8 graphiques :
   - `analysis_fusion.png` : planche de synthèse de la fusion météo × hôtels
   - `charts/` : les 7 graphiques unitaires (scores par ville, Top 10, corrélation
     qualité/prix, notes et avis, prix par ville, types d'hébergement, corrélations)

   > L'ancienne planche unique `dashboard_complet.png` n'est plus générée : ses graphiques
   > ont été éclatés en fichiers unitaires, lisibles individuellement dans le rapport.

3. **Rapport HTML interactif** (`rapport_final.html`) :
   - Design responsive
   - Statistiques clés
   - Top 5 détaillé
   - Les 3 cartes intégrées en `<iframe>`
   - Graphiques embarqués en base64 — le rapport reste lisible même téléchargé seul

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
1. Upload des 19 objets vers S3 : rapport, cartes, graphiques et données CSV
2. Configuration de l'accès public via Bucket Policy
3. Génération des URLs publiques (`data/processed/aws_s3_urls.txt` et `.json`)

> Le rapport HTML référence ses **trois cartes** par des chemins **relatifs plats**
> (`carte_destinations.html`, `carte_top20.html`, `carte_tous_hotels.html`). Ces fichiers
> doivent donc être déposés dans le **même préfixe** que le rapport, à la racine du bucket —
> sinon les trois iframes renvoient un 404 une fois en ligne. Les graphiques, eux, sont
> encodés en base64 dans le rapport et ne dépendent d'aucun chemin.

---

#### 4.3 Configuration RDS PostgreSQL

**Actions** :
1. Connexion à l'instance RDS existante

> **L'extraction se fait depuis S3, pas depuis le disque local.** L'énoncé demande
> d'« extract your data from S3 and store it in your newly created DB » : le notebook 11
> lit les CSV via `boto3.get_object` sur le bucket, ce qui fait réellement de S3 la source
> du data warehouse et non un dépôt de fichiers en parallèle.
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
1. Import des **35 villes** du périmètre (dont 5 destinations retenues, marquées `is_top5`)
2. Import des hôtels (74 hôtels)
3. Import des recommandations (72 entrées classées)
4. Import de l'historique météo (5 enregistrements)
5. Vérification de l'intégrité des données

**Statistiques finales** :
```
✅ 35 villes importées (dont 5 destinations retenues)
✅ 74 hôtels importés
✅ 72 recommandations importées
✅ 5 relevés météo détaillés
💾 Taille de la base : 8,4 MB
```

Charger les 35 villes — et pas seulement le Top 5 — permet de **rejouer la sélection des
destinations en SQL** depuis la base, ce qui était impossible auparavant :

```sql
SELECT city_name, avg_weather_score, is_top5
FROM cities
ORDER BY avg_weather_score DESC;
```

> ⚠️ **Limite de reconstruction.** Le CSV météo des 35 villes n'était pas versionné et les
> prévisions OpenWeather ne sont pas rejouables (l'API ne sert que du J+5, jamais
> d'historique). Les valeurs du run du 11/11/2025 ont été récupérées depuis la carte Plotly
> versionnée, qui embarque nom, coordonnées et score des 35 villes — mais pas le détail
> (température, pluie, vent, humidité, nuages), disponible uniquement pour le Top 5.
> La colonne `weather_detail` trace cette différence (`complet` / `score_seul`), et
> `weather_history` ne contient donc que les 5 relevés détaillés.
> Script de reconstruction : `src/recover_city_weather.py`.

Instance : `kayak-db.cta2iqgqyibu.eu-north-1.rds.amazonaws.com:5432`, PostgreSQL 18.3,
`db.t4g.micro`, base `kayak`.

Contrôles d'intégrité après import : aucun hôtel orphelin (tous rattachés à une ville),
devise unique en base (`EUR`), prix de 45 à 863 €/nuit. Les 2 hôtels sans avis sont
présents dans `hotels` mais absents de `recommendations` — une note absente n'est pas
une note de 0/10, ils ne peuvent donc pas être classés.

---

## ☁️ Livrables en ligne

Bucket `260824-181205-jedha-kayak-project` (région `eu-north-1`), accès public en lecture.
Liens vérifiés le 28/08/2026.

| Livrable | URL |
|---|---|
| 📄 **Rapport final** | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/rapport_final.html |
| 🌍 Carte du Top 5 | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/carte_destinations.html |
| 🗺️ Carte complète | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/carte_tous_hotels.html |
| 🏆 Carte Top 20 | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/carte_top20.html |
| 📈 Planche d'analyse | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/analysis_fusion.png |
| 🧩 **CSV enrichi** (livrable) | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/data/kayak_enriched.csv |
| 📁 Recommandations finales | https://260824-181205-jedha-kayak-project.s3.eu-north-1.amazonaws.com/data/final_recommendations.csv |

La liste complète des 19 objets publiés est dans `data/processed/aws_s3_urls.txt`.

---

## 💻 Installation

### Prérequis

- Python 3.10+
- pip
- Jupyter Notebook
- Compte BrightData (pour le scraping Booking.com)
- Compte OpenWeatherMap (pour la météo)
- Compte AWS (pour le déploiement cloud)

### Étapes
```bash
# 1. Cloner le dépôt
git clone https://github.com/emelineroblot/jedha-kayak-project.git
cd jedha-kayak-project

# 2. Créer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp config/.env.example config/.env
# Puis éditer config/.env (voir la liste des variables dans le template)
```

> Les notebooks chargent les secrets via `load_dotenv('../config/.env')` : le fichier doit
> bien se trouver dans `config/`, pas à la racine du dépôt.

### Relire les résultats sans rejouer le pipeline

Les livrables sont versionnés. Sans aucune clé d'API :

```bash
# Le rapport complet, hors ligne
python -m http.server 8000 --directory data/processed
# puis ouvrir http://localhost:8000/rapport_final.html
```

---

## ⚠️ Limites assumées

1. **Les deux fenêtres temporelles ne coïncident pas.** Les villes sont sélectionnées sur une
   prévision météo à 6 jours, les hôtels interrogés pour un séjour à **J+30**. On recommande
   donc un hébergement pour une date dont on ne connaît pas la météo. C'est un choix : à J+30
   les tarifs sont disponibles et stables, alors que l'API météo gratuite ne dépasse pas J+5.

2. **Le run n'est pas rejouable à l'identique.** OpenWeather ne sert pas d'historique et les
   tarifs Booking changent en continu. Rejouer les notebooks produira d'autres chiffres — les
   CSV versionnés sont la trace du run du 11/11/2025.

3. **Détail météo disponible pour 5 villes sur 35.** Voir la note de reconstruction en 4.4 :
   la colonne `weather_detail` distingue `complet` de `score_seul`.

4. **Échantillon d'hôtels petit et non exhaustif.** ~15 établissements par ville sur une seule
   requête Booking, pour 2 adultes et 2 nuits. Le classement décrit cette collecte, pas le
   marché de l'hébergement de ces villes.

5. **Un doublon corrigé, mais la déduplication reste faible.** Elle porte sur `listing_id` :
   deux annonces distinctes du même établissement ne seraient pas détectées.

6. **La pondération 40/40/20 est un choix produit, pas un optimum mesuré.** Aucune donnée de
   réservation ne permet de la valider ; elle est explicite et modifiable en un point du code.

7. **Prix convertis à un taux figé.** 1 USD = 0,86393 EUR (BCE, 11/11/2025). Les montants sont
   comparables entre eux, mais ne reflètent plus les prix actuels.

8. **Pas de suite de tests automatisés.** La cohérence est assurée par la centralisation des
   constantes dans `src/config.py` et par les contrôles d'intégrité exécutés après l'import RDS,
   pas par des tests unitaires.

---

## 🛠️ Stack technique

```
pandas, numpy                   manipulation des données
requests, aiohttp               appels API (OpenWeather, BrightData)
folium                          cartes interactives (Top 5, tous hôtels, Top 20)
plotly                          cartes et radars de l'analyse météo
matplotlib, seaborn             dashboard analytique
boto3                           S3 (upload, lecture des CSV pour l'import RDS)
psycopg2                        PostgreSQL sur AWS RDS
python-dotenv                   chargement des secrets depuis config/.env
jupyter                         11 notebooks, exécutés dans l'ordre
```

Versions figées dans `requirements.txt`.

**Services externes** : OpenWeatherMap (météo), BrightData (Booking.com),
AWS S3 (diffusion des livrables), AWS RDS PostgreSQL 18.3 (`db.t4g.micro`).

---

## 👤 Auteur

**Emeline ROBLOT**
- 🌐 GitHub : [@emelineroblot](https://github.com/emelineroblot)
- 💼 LinkedIn : [Emeline ROBLOT](https://linkedin.com/in/emeline-roblot)
- 📧 Email : emeline.roblot@emdigital.fr

---

**Données collectées** : 11 novembre 2025
**Dernière mise à jour du dépôt** : 28 août 2026

**Status** : ✅ **PROJET COMPLET** — Étapes 1 à 4 terminées, livrables publiés sur S3 et RDS

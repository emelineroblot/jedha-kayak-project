"""
Constantes partagées entre le déclenchement du scraping et le parsing des résultats.

Regroupées ici pour éviter que deux fichiers divergent sur une hypothèse commune
(nombre d'adultes de la recherche, taux de change appliqué aux prix).
"""

# ═══════════════════════════════════════════════════════════════════════
# PARAMÈTRES DE RECHERCHE BOOKING
# ═══════════════════════════════════════════════════════════════════════

# Nombre d'adultes envoyé à Booking via BrightData. Sert aussi de plancher de
# capacité au moment du calcul du prix par personne : une offre retournée par une
# recherche « 2 adultes » loge nécessairement 2 personnes, même quand le champ
# max_number_of_guests des données brutes vaut 0 ou 1 (bruit observé sur ~14 %
# des types de chambres).
SEARCH_ADULTS = 2

# Durée du séjour interrogé, en nuits. BrightData renvoie `final_price` pour la
# durée totale du séjour et non par nuit : c'est la source du bug de prix ×2.
SEARCH_NIGHTS = 2

# Nombre de jours entre la date d'exécution et la date d'arrivée interrogée.
# Choix assumé : à J+30 les tarifs sont disponibles et stables, alors que la
# fenêtre météo utilisée pour sélectionner les villes ne couvre que 6 jours.
# Les deux fenêtres ne coïncident donc pas — c'est documenté dans le rapport.
SEARCH_LEAD_DAYS = 30


# ═══════════════════════════════════════════════════════════════════════
# CONVERSION DE DEVISE
# ═══════════════════════════════════════════════════════════════════════

# BrightData ignore le paramètre `currency: EUR` de la requête et renvoie
# systématiquement des montants en USD. Les prix sont donc convertis au taux de
# référence BCE du jour de la collecte.
#
# Source : https://api.frankfurter.dev/v1/2025-11-11?from=USD&to=EUR
#          (taux de référence BCE, 1 USD = 0.86393 EUR)
FX_RATE_DATE = '2025-11-11'
FX_RATES = {
    'USD': 0.86393,
    'EUR': 1.0,
}

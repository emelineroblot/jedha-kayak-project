"""
Reconstruit data/processed/city_weather_scores.csv pour les 35 villes.

Contexte
--------
Le CSV d'origine n'est pas versionné (`.gitignore` excluait `data/processed/*.csv`)
et les prévisions OpenWeather ne sont pas rejouables : l'API ne renvoie que des
prévisions à J+5, jamais un historique. Les valeurs du run du 11/11/2025 sont donc
récupérées depuis les artefacts qui, eux, ont été versionnés.

Sources
-------
1. `visualizations/top5_destinations_map.html` — la carte Plotly embarque la trace
   de fond « Autres villes » avec, pour les 35 villes : `text` (nom), `lat`, `lon`
   et `customdata` (score météo moyen). Les tableaux numériques sont encodés en
   base64 (format typed-array de Plotly 6).
2. `data/processed/top5_destinations.csv` — détail météo complet, mais pour les
   5 destinations retenues uniquement.

Limite assumée
--------------
`temp_avg`, `pop`, `rain`, `humidity`, `wind_speed` et `clouds` ne sont
disponibles que pour le Top 5. Ils restent vides pour les 30 autres villes.
La colonne `weather_detail` trace cette différence.

Usage :
    python src/recover_city_weather.py
"""

import base64
import io
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MAP_HTML = ROOT / 'visualizations' / 'top5_destinations_map.html'
TOP5_CSV = ROOT / 'data' / 'processed' / 'top5_destinations.csv'
OUT_CSV = ROOT / 'data' / 'processed' / 'city_weather_scores.csv'

DETAIL_COLS = ['temp_avg', 'pop', 'rain', 'humidity', 'wind_speed', 'clouds']


def _decode(value):
    """Plotly 6 encode les tableaux numeriques en base64 ({dtype, bdata})."""
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and 'bdata' in value:
        buf = base64.b64decode(value['bdata'])
        return np.frombuffer(buf, dtype=value.get('dtype', 'f8')).tolist()
    raise TypeError(f'format de tableau Plotly non reconnu : {type(value)}')


def load_background_trace():
    """Extrait la trace des 35 villes de la carte Plotly versionnee."""
    html = io.open(MAP_HTML, encoding='utf-8').read()
    match = re.search(r'Plotly\.newPlot\(\s*"[^"]+",\s*(\[.*?\]),\s*\{', html, re.S)
    if not match:
        raise RuntimeError(f'aucune figure Plotly trouvee dans {MAP_HTML}')

    traces = json.loads(match.group(1))
    background = next((t for t in traces if t.get('name') == 'Autres villes'), None)
    if background is None:
        raise RuntimeError('trace de fond « Autres villes » introuvable')

    return pd.DataFrame({
        'city': background['text'],
        'latitude': _decode(background['lat']),
        'longitude': _decode(background['lon']),
        'avg_weather_score': _decode(background['customdata']),
    })


def main():
    cities = load_background_trace()
    print(f'{len(cities)} villes recuperees depuis {MAP_HTML.name}')

    top5 = pd.read_csv(TOP5_CSV)
    print(f'{len(top5)} villes avec detail meteo depuis {TOP5_CSV.name}')

    # Le detail meteo vient du Top 5 ; les coordonnees et le score viennent de la
    # carte, qui fait autorite pour les 35.
    merged = cities.merge(top5[['city'] + DETAIL_COLS], on='city', how='left')

    merged['weather_detail'] = np.where(
        merged[DETAIL_COLS].notna().any(axis=1), 'complet', 'score_seul'
    )
    merged['is_top5'] = merged['city'].isin(top5['city'])

    merged = merged.sort_values('avg_weather_score', ascending=False).reset_index(drop=True)
    merged.insert(0, 'city_id', range(1, len(merged) + 1))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_CSV, index=False, encoding='utf-8')

    print()
    print(f'-> {OUT_CSV.relative_to(ROOT)} ({len(merged)} villes)')
    print(f'   detail meteo complet : {(merged["weather_detail"] == "complet").sum()}')
    print(f'   score seul           : {(merged["weather_detail"] == "score_seul").sum()}')
    print()
    print(merged.head(8)[['city_id', 'city', 'avg_weather_score', 'temp_avg',
                          'weather_detail', 'is_top5']].to_string(index=False))


if __name__ == '__main__':
    main()

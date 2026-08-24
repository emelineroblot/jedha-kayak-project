"""
Re-parse des hôtels à partir des réponses JSON brutes déjà collectées.

Permet de rejouer l'étape de parsing sans relancer un scraping BrightData (les
snapshots ont une durée de vie limitée et chaque run est facturé). Utilise
exactement la même fonction `parse_hotels_data` que le pipeline temps réel :
corriger le parseur corrige donc aussi les fichiers régénérés ici.

Usage :
    python src/reparse_hotels.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / 'src'))

from config import FX_RATE_DATE, FX_RATES  # noqa: E402
from fetch_results import parse_hotels_data  # noqa: E402

JSON_DIR = ROOT / 'data' / 'raw' / 'hotels_json'
HOTELS_DIR = ROOT / 'data' / 'raw' / 'hotels'
COMBINED_CSV = ROOT / 'data' / 'raw' / 'hotels_top5_all.csv'

# Le registre conserve l'orthographe exacte des villes telle qu'envoyée à
# BrightData ; les noms de fichiers, eux, sont slugifiés.
REGISTRY_CANDIDATES = (
    ROOT / 'data' / 'raw' / 'snapshots' / 'snapshots_registry.json',
    ROOT / 'notebooks' / 'data' / 'raw' / 'snapshots' / 'snapshots_registry.json',
)


def load_city_names():
    """slug -> nom de ville d'origine, depuis le registre de snapshots."""
    for path in REGISTRY_CANDIDATES:
        if path.exists():
            registry = json.loads(path.read_text(encoding='utf-8'))
            return {
                city.replace(' ', '_').lower(): city
                for city in registry.get('snapshots', {})
            }
    return {}


def main():
    city_names = load_city_names()
    HOTELS_DIR.mkdir(parents=True, exist_ok=True)

    print('=' * 78)
    print('RE-PARSING DES HOTELS DEPUIS LES JSON BRUTS')
    print(f'Conversion USD -> EUR : {FX_RATES["USD"]} (taux BCE du {FX_RATE_DATE})')
    print('=' * 78)

    frames = []
    for json_path in sorted(JSON_DIR.glob('*_raw.json')):
        slug = json_path.stem.replace('_raw', '')
        city = city_names.get(slug, slug.replace('_', ' ').title())

        hotels_data = json.loads(json_path.read_text(encoding='utf-8'))
        df = parse_hotels_data(hotels_data, city)

        if df.empty:
            print(f'   [vide]  {city}')
            continue

        out = HOTELS_DIR / f'hotels_{slug}.csv'
        df.to_csv(out, index=False, encoding='utf-8')
        frames.append(df)

    if not frames:
        print('Aucune donnee parsee.')
        return

    all_hotels = pd.concat(frames, ignore_index=True)
    all_hotels.to_csv(COMBINED_CSV, index=False, encoding='utf-8')

    print('-' * 78)
    print(f'{len(all_hotels)} hotels -> {COMBINED_CSV.relative_to(ROOT)}')
    print(f'  notes disponibles      : {all_hotels["score"].notna().sum()}/{len(all_hotels)}')
    print(f'  prix disponibles       : {all_hotels["price_per_night"].notna().sum()}/{len(all_hotels)}')
    print(f'  coordonnees GPS        : {all_hotels["latitude"].notna().sum()}/{len(all_hotels)}')
    print(f'  identifiants uniques   : {all_hotels["hotel_id"].nunique()}')
    print()
    print(all_hotels.groupby('city').agg(
        hotels=('hotel_id', 'count'),
        note_moy=('score', 'mean'),
        prix_nuit_eur=('price_per_night', 'mean'),
        prix_pers_nuit_eur=('price_per_person_night', 'mean'),
    ).round(2).to_string())


if __name__ == '__main__':
    main()

"""
STEP 2 : Récupération des résultats depuis BrightData
Polling GET sur les snapshot_id pour récupérer les données
"""

import aiohttp
import asyncio
import json
import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from config import FX_RATES, FX_RATE_DATE, SEARCH_ADULTS  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

SNAPSHOTS_REGISTRY = 'data/raw/snapshots/snapshots_registry.json'


def load_config():
    """Charge la configuration API."""
    if 'notebooks' in str(Path.cwd()):
        env_path = Path.cwd().parent / 'config' / '.env'
    else:
        env_path = Path('config/.env')
    
    if not env_path.exists():
        raise FileNotFoundError(f"❌ Fichier .env introuvable : {env_path}")
    
    load_dotenv(env_path)
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    
    if not api_key:
        raise ValueError(f"❌ BRIGHTDATA_API_KEY non trouvée dans {env_path}")
    
    print(f"✅ API Key chargée : {api_key[:20]}...")
    return api_key


def load_snapshot_registry():
    """Charge le registre des snapshots."""
    if not os.path.exists(SNAPSHOTS_REGISTRY):
        raise FileNotFoundError(f"❌ Fichier non trouvé : {SNAPSHOTS_REGISTRY}")
    
    with open(SNAPSHOTS_REGISTRY, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_snapshot_status(city, status, num_hotels=0):
    """Met à jour le statut d'un snapshot dans le registre."""
    registry = load_snapshot_registry()
    
    if city in registry["snapshots"]:
        registry["snapshots"][city]["status"] = status
        registry["snapshots"][city]["num_hotels"] = num_hotels
        
        if status in ["ready", "error"]:
            registry["snapshots"][city]["timestamp_complete"] = datetime.now().isoformat()
        
        with open(SNAPSHOTS_REGISTRY, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════
# SAUVEGARDE JSON
# ═══════════════════════════════════════════════════════════════════════

def save_json_response(city, hotels_data):
    """Sauvegarde la réponse JSON brute de l'API."""
    os.makedirs('data/raw/hotels_json', exist_ok=True)
    
    filename = f"data/raw/hotels_json/{city.replace(' ', '_').lower()}_raw.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(hotels_data, f, indent=2, ensure_ascii=False)
    
    print(f"   💾 JSON brut : {filename}")


# ═══════════════════════════════════════════════════════════════════════
# FONCTION ASYNCHRONE : GET /snapshot
# ═══════════════════════════════════════════════════════════════════════

async def fetch_snapshot_results(session, city, snapshot_id, api_key, max_wait=600, check_interval=30):
    """Récupère les résultats d'un snapshot (GET avec polling)."""
    url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"format": "json"}
    
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < max_wait:
        attempts += 1
        elapsed = int(time.time() - start_time)
        
        try:
            async with session.get(url, headers=headers, params=params) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError:
                        print(f"❌ {city:20s} → Erreur JSON")
                        return None
                    
                    # CAS 1 : Liste directe (données prêtes)
                    if isinstance(result, list):
                        num_hotels = len(result)
                        print(f"✅ {city:20s} → {num_hotels} hôtels ({elapsed}s)")
                        update_snapshot_status(city, "ready", num_hotels)
                        
                        # SAUVEGARDER LE JSON BRUT
                        save_json_response(city, result)
                        
                        return result
                    
                    # CAS 2 : Objet avec statut
                    elif isinstance(result, dict):
                        status = result.get('status')
                        
                        if status == 'ready':
                            snapshot_url = result.get('snapshot_url')
                            if snapshot_url:
                                async with session.get(snapshot_url) as data_response:
                                    if data_response.status == 200:
                                        hotels_data = await data_response.json()
                                        num_hotels = len(hotels_data) if isinstance(hotels_data, list) else 0
                                        print(f"✅ {city:20s} → {num_hotels} hôtels ({elapsed}s)")
                                        update_snapshot_status(city, "ready", num_hotels)
                                        
                                        # SAUVEGARDER LE JSON BRUT
                                        save_json_response(city, hotels_data)
                                        
                                        return hotels_data
                            
                            print(f"❌ {city:20s} → Données non accessibles")
                            update_snapshot_status(city, "error", 0)
                            return None
                        
                        elif status == 'running':
                            print(f"⏳ {city:20s} → running (t.{attempts:2d}, {elapsed:3d}s)")
                            update_snapshot_status(city, "running", 0)
                            await asyncio.sleep(check_interval)
                        
                        elif status == 'error':
                            print(f"❌ {city:20s} → Erreur API")
                            update_snapshot_status(city, "error", 0)
                            return None
                        
                        else:
                            print(f"⏳ {city:20s} → statut: {status} (t.{attempts:2d}, {elapsed:3d}s)")
                            await asyncio.sleep(check_interval)
                    
                    else:
                        print(f"❌ {city:20s} → Format inattendu: {type(result)}")
                        return None
                
                elif response.status == 202:
                    print(f"⏳ {city:20s} → En attente (t.{attempts:2d}, {elapsed:3d}s)")
                    await asyncio.sleep(check_interval)
                
                else:
                    print(f"❌ {city:20s} → HTTP {response.status}")
                    update_snapshot_status(city, "error", 0)
                    return None
        
        except Exception as e:
            print(f"⚠️  {city:20s} → Erreur: {str(e)[:80]}")
            await asyncio.sleep(check_interval)
    
    print(f"⚠️  {city:20s} → Timeout {max_wait}s")
    update_snapshot_status(city, "error", 0)
    return None


# ═══════════════════════════════════════════════════════════════════════
# PARSING DES RÉSULTATS (CORRIGÉ)
# ═══════════════════════════════════════════════════════════════════════

def _first_not_none(mapping, keys):
    """Retourne la premiere valeur non-None parmi `keys` (0.0 est une valeur valide)."""
    for key in keys:
        value = mapping.get(key)
        if value is not None:
            return value
    return None


def _parse_coordinates(hotel):
    """Extrait (latitude, longitude). L'API BrightData renvoie 'lan' au lieu de 'lat'."""
    coordinates = hotel.get('coordinates')
    if not isinstance(coordinates, dict):
        return None, None

    lat = _first_not_none(coordinates, ('lat', 'lan', 'latitude'))
    lon = _first_not_none(coordinates, ('lon', 'lng', 'longitude'))

    if lat is None or lon is None:
        return None, None
    return float(lat), float(lon)


def _parse_best_offer(hotel):
    """
    Selectionne l'offre la moins chere par personne et par nuit.

    Corrige trois defauts de la version initiale :
      - le prix retenu etait celui de la 1re chambre listee, pas la moins chere ;
      - `final_price` couvre la duree du sejour (`nights`), pas une nuit ;
      - les biens n'ont pas la meme capacite, donc les totaux ne sont pas comparables.

    La capacite vient de `availability` (jointure sur `room_type`). Elle est plafonnee
    par le bas a SEARCH_ADULTS : la recherche a ete faite pour 2 adultes, donc toute
    offre retournee loge au moins 2 personnes (des capacites a 0 ou 1 existent dans
    les donnees brutes et relevent du bruit).
    """
    capacity_by_room = {
        room.get('room_type'): room.get('max_number_of_guests')
        for room in (hotel.get('availability') or [])
    }

    best = None
    for room in (hotel.get('pricing') or []):
        guests = capacity_by_room.get(room.get('room_type'))
        guests = max(int(guests), SEARCH_ADULTS) if guests else SEARCH_ADULTS

        for offer in (room.get('offers') or []):
            price = offer.get('price') or {}
            total = price.get('final_price')
            if total is None:
                continue

            nights = price.get('nights') or 1
            per_night = float(total) / nights
            per_person_night = per_night / guests

            if best is None or per_person_night < best['price_per_person_night']:
                best = {
                    'room_type': room.get('room_type'),
                    'guests': guests,
                    'nights': nights,
                    'price_total': float(total),
                    'price_per_night': round(per_night, 2),
                    'price_per_person_night': round(per_person_night, 2),
                    'currency': price.get('currency'),
                    'taxes_fees_included': price.get('taxes_fees_included'),
                }
    return best


def parse_hotels_data(hotels_data, city):
    """Parse les donnees JSON en DataFrame."""
    if not hotels_data or not isinstance(hotels_data, list):
        return pd.DataFrame()

    parsed = []
    skipped = []

    for idx, hotel in enumerate(hotels_data, 1):
        try:
            # `listing_id` est l'identifiant stable de l'annonce Booking. L'ancien
            # identifiant positionnel (f"{city}_{idx}") changeait a chaque execution
            # et ne permettait pas de detecter les doublons : les URLs different par
            # un parametre anti-bot `chal_t` horodate.
            listing_id = hotel.get('listing_id')

            score = hotel.get('review_score')
            reviews = hotel.get('number_of_reviews')

            info = {
                'hotel_id': listing_id if listing_id is not None else '{}_{}'.format(city, idx),
                'city': city,
                'hotel_name': hotel.get('title'),
                'url': hotel.get('url'),
                # Un etablissement sans avis est renvoye avec review_score = 0.
                # Ce n'est pas une note de 0/10, c'est une note absente.
                'score': float(score) if score else None,
                'number_of_reviews': reviews,
                'description': (hotel.get('description', '') or '')[:500],
                'property_type': hotel.get('property_type'),
            }

            latitude, longitude = _parse_coordinates(hotel)
            info['latitude'] = latitude
            info['longitude'] = longitude

            # PRIX
            offer = _parse_best_offer(hotel)
            if offer:
                rate = FX_RATES.get(offer['currency'], 1.0)
                info['room_type'] = offer['room_type']
                info['max_guests'] = offer['guests']
                info['nights'] = offer['nights']
                info['currency_source'] = offer['currency']
                info['price_total_source'] = offer['price_total']
                info['taxes_included'] = offer['taxes_fees_included']
                info['price_per_night'] = round(offer['price_per_night'] * rate, 2)
                info['price_per_person_night'] = round(offer['price_per_person_night'] * rate, 2)
                info['currency'] = 'EUR'
            else:
                for column in ('room_type', 'max_guests', 'nights', 'currency_source',
                               'price_total_source', 'taxes_included',
                               'price_per_night', 'price_per_person_night', 'currency'):
                    info[column] = None

            facilities = hotel.get('most_popular_facilities', [])
            info['facilities'] = ', '.join(facilities[:5]) if facilities else None

            images = hotel.get('images', [])
            info['image_url'] = images[0] if images else None

            if info['hotel_name'] and info['url']:
                parsed.append(info)
            else:
                skipped.append((info['hotel_id'], 'nom ou URL manquant'))

        except Exception as exc:
            # Ne jamais avaler silencieusement une erreur de parsing : une ligne
            # perdue sans trace est indetectable en aval.
            skipped.append((hotel.get('listing_id', idx), '{}: {}'.format(type(exc).__name__, exc)))
            continue

    df = pd.DataFrame(parsed)

    # Deduplication sur l'identifiant d'annonce : Booking renvoie parfois deux fois
    # le meme etablissement dans une meme recherche.
    if not df.empty:
        duplicates = int(df['hotel_id'].duplicated().sum())
        if duplicates:
            df = df.drop_duplicates(subset='hotel_id', keep='first').reset_index(drop=True)
            print("   [dedup] {:25s} -> {} doublon(s) supprime(s)".format(city, duplicates))

    for hotel_id, reason in skipped:
        print("   [skip]  {:25s} -> hotel {} ignore ({})".format(city, hotel_id, reason))

    if not df.empty:
        coords_found = int(df["latitude"].notna().sum())
        print("   [ok]    {:25s} -> {} hotels | {} GPS ({:.0f}%)".format(
            city, len(df), coords_found, coords_found / len(df) * 100))

    return df



# ═══════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════

async def fetch_all_results():
    """Récupère les résultats pour tous les snapshots."""
    print(f"\n{'='*80}")
    print(f"📥 STEP 2 : RÉCUPÉRATION DES RÉSULTATS (GET)")
    print(f"{'='*80}")
    print(f"⏱️  Démarrage : {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Charger le registre
    registry = load_snapshot_registry()
    snapshots = registry.get("snapshots", {})
    
    if not snapshots:
        print("❌ Aucun snapshot trouvé")
        return {}
    
    print(f"📊 {len(snapshots)} snapshot(s) à récupérer :")
    for city, info in snapshots.items():
        print(f"   • {city:25s} → {info['snapshot_id']}")
    print()
    
    # Charger la config
    api_key = load_config()
    
    all_results = {}
    timeout = aiohttp.ClientTimeout(total=None, connect=60, sock_read=60)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Créer les tâches
        tasks = []
        for city, info in snapshots.items():
            snapshot_id = info['snapshot_id']
            task = fetch_snapshot_results(session, city, snapshot_id, api_key, 600, 30)
            tasks.append((city, task))
        
        # Exécuter en parallèle
        print(f"⏳ Récupération en cours...\n")
        results = await asyncio.gather(*[task for _, task in tasks])
        
        # Parser et sauvegarder
        print(f"\n{'─'*80}")
        print("📊 Parsing et sauvegarde...")
        print(f"{'─'*80}\n")
        
        os.makedirs('data/raw/hotels', exist_ok=True)
        
        for (city, _), hotels_data in zip(tasks, results):
            if hotels_data:
                df = parse_hotels_data(hotels_data, city)
                
                if not df.empty:
                    filename = f"data/raw/hotels/hotels_{city.replace(' ', '_').lower()}.csv"
                    df.to_csv(filename, index=False, encoding='utf-8')
                    print(f"   💾 CSV : {filename}")
                    all_results[city] = df
    
    # Combiner
    if all_results:
        all_hotels = pd.concat(list(all_results.values()), ignore_index=True)
        all_hotels.to_csv('data/raw/hotels_top5_all.csv', index=False)
        
        # Stats GPS
        total_hotels = len(all_hotels)
        with_gps = all_hotels['latitude'].notna().sum()
        
        print(f"\n{'='*80}")
        print(f"✅ hotels_top5_all.csv ({total_hotels} hôtels)")
        print(f"📍 Coordonnées GPS : {with_gps}/{total_hotels} ({with_gps/total_hotels*100:.1f}%)")
    
    print(f"\n{'='*80}")
    print(f"✅ STEP 2 TERMINÉ")
    print(f"{'='*80}")
    print(f"📊 Villes : {len(all_results)}/{len(snapshots)}\n")
    
    return all_results


# ═══════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée pour exécution standalone."""
    asyncio.run(fetch_all_results())


if __name__ == "__main__":
    main()
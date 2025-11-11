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

def parse_hotels_data(hotels_data, city):
    """Parse les données JSON en DataFrame."""
    if not hotels_data or not isinstance(hotels_data, list):
        return pd.DataFrame()
    
    parsed = []
    coords_found = 0
    
    for idx, hotel in enumerate(hotels_data, 1):
        try:
            info = {
                'hotel_id': f"{city}_{idx}",
                'city': city,
                'hotel_name': hotel.get('title'),
                'url': hotel.get('url'),
                'score': hotel.get('review_score'),
                'number_of_reviews': hotel.get('number_of_reviews'),
                'description': (hotel.get('description', '') or '')[:500],
                'property_type': hotel.get('property_type'),
            }
            
            # ═══════════════════════════════════════════════════════════════
            # PARSING GPS CORRIGÉ - GÈRE "lan" et "lat"
            # ═══════════════════════════════════════════════════════════════
            
            coordinates = hotel.get('coordinates')
            
            if coordinates and isinstance(coordinates, dict):
                # Essayer "lat" puis "lan" (bug de l'API)
                lat = coordinates.get('lat') or coordinates.get('lan') or coordinates.get('latitude')
                lon = coordinates.get('lon') or coordinates.get('lng') or coordinates.get('longitude')
                
                if lat is not None and lon is not None:
                    info['latitude'] = float(lat)
                    info['longitude'] = float(lon)
                    coords_found += 1
                else:
                    info['latitude'] = None
                    info['longitude'] = None
            else:
                info['latitude'] = None
                info['longitude'] = None
            
            # ═══════════════════════════════════════════════════════════════
            # PRIX
            # ═══════════════════════════════════════════════════════════════
            
            pricing = hotel.get('pricing', [])
            if pricing and len(pricing) > 0:
                offers = pricing[0].get('offers', [])
                if offers:
                    price_info = offers[0].get('price', {})
                    info['price'] = price_info.get('final_price')
                    info['currency'] = price_info.get('currency', 'EUR')
                else:
                    info['price'] = None
                    info['currency'] = None
            else:
                info['price'] = None
                info['currency'] = None
            
            # ═══════════════════════════════════════════════════════════════
            # ÉQUIPEMENTS
            # ═══════════════════════════════════════════════════════════════
            
            facilities = hotel.get('most_popular_facilities', [])
            info['facilities'] = ', '.join(facilities[:5]) if facilities else None
            
            # ═══════════════════════════════════════════════════════════════
            # IMAGES
            # ═══════════════════════════════════════════════════════════════
            
            images = hotel.get('images', [])
            info['image_url'] = images[0] if images else None
            
            if info['hotel_name'] and info['url']:
                parsed.append(info)
        
        except Exception as e:
            continue
    
    df = pd.DataFrame(parsed)
    
    if not df.empty:
        print(f"   ✅ {city:25s} → {len(df)} hôtels | {coords_found} GPS ({coords_found/len(df)*100:.0f}%)")
    
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
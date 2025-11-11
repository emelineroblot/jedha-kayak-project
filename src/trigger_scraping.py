"""
STEP 1 : Déclenchement du scraping Booking.com via BrightData API
Lancement des requêtes POST en parallèle pour obtenir les snapshot_id
"""

import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

SNAPSHOTS_REGISTRY = 'data/raw/snapshots/snapshots_registry.json'


def load_config():
    """Charge la configuration API."""
    from pathlib import Path
    
    # Trouver le fichier .env de manière robuste
    # 1. Essayer depuis le dossier courant (si lancé depuis notebook)
    env_path = Path('config/.env')
    
    # 2. Si pas trouvé, essayer depuis le parent (si lancé depuis notebooks/)
    if not env_path.exists():
        env_path = Path('../config/.env')
    
    # 3. Si toujours pas trouvé, essayer chemin absolu
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / 'config' / '.env'
    
    print(f"🔍 Chargement depuis : {env_path.absolute()}")
    
    if not env_path.exists():
        raise FileNotFoundError(f"❌ Fichier .env introuvable : {env_path.absolute()}")
    
    load_dotenv(env_path)
    
    api_key = os.getenv('BRIGHTDATA_API_KEY')
    dataset_id = "gd_mdy9ld3p1e0oqlj9g4"
    
    if not api_key:
        raise ValueError(f"❌ BRIGHTDATA_API_KEY non trouvée dans {env_path}")
    
    print(f"✅ API Key chargée : {api_key[:20]}...")
    return api_key, dataset_id


def save_snapshot_registry(registry):
    """Sauvegarde le registre des snapshots."""
    os.makedirs('data/raw/snapshots', exist_ok=True)
    with open(SNAPSHOTS_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"💾 Registre sauvegardé : {SNAPSHOTS_REGISTRY}")


def load_snapshot_registry():
    """Charge le registre des snapshots."""
    if os.path.exists(SNAPSHOTS_REGISTRY):
        with open(SNAPSHOTS_REGISTRY, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"timestamp": datetime.now().isoformat(), "snapshots": {}}


# ═══════════════════════════════════════════════════════════════════════
# FONCTION ASYNCHRONE : POST /trigger
# ═══════════════════════════════════════════════════════════════════════

async def trigger_city_scraping(session, city_name, max_hotels, api_key, dataset_id):
    """
    Déclenche le scraping pour une ville (POST).
    
    Args:
        session: Session aiohttp
        city_name (str): Nom de la ville
        max_hotels (int): Nombre max d'hôtels
        api_key (str): Clé API BrightData
        dataset_id (str): ID du dataset
        
    Returns:
        dict: Informations du snapshot
    """
    checkin = datetime.now() + timedelta(days=30)
    checkout = checkin + timedelta(days=2)
    
    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    params = {
        "dataset_id": dataset_id,
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "search_input",
        "limit_per_input": str(max_hotels),
    }
    
    data = [{
        "url": "https://www.booking.com",
        "location": f"{city_name}, France",
        "check_in": checkin.strftime("%Y-%m-%dT00:00:00.000Z"),
        "check_out": checkout.strftime("%Y-%m-%dT00:00:00.000Z"),
        "adults": 2,
        "rooms": 1,
        "currency": "EUR",
        "country": "FR"
    }]
    
    try:
        async with session.post(url, headers=headers, params=params, json=data) as response:
            response_text = await response.text()
            
            if response.status == 200:
                result = json.loads(response_text)
                snapshot_id = result.get('snapshot_id')
                
                if snapshot_id:
                    print(f"✅ {city_name:20s} → Snapshot: {snapshot_id}")
                    return {
                        "city": city_name,
                        "snapshot_id": snapshot_id,
                        "status": "triggered",
                        "timestamp": datetime.now().isoformat(),
                        "max_hotels": max_hotels
                    }
                else:
                    print(f"❌ {city_name:20s} → Pas de snapshot_id")
                    return None
            else:
                print(f"❌ {city_name:20s} → HTTP {response.status}")
                return None
    
    except Exception as e:
        print(f"❌ {city_name:20s} → Erreur: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════

async def trigger_all_cities(cities_list, max_hotels_per_city=15):
    """
    Déclenche le scraping pour toutes les villes en parallèle.
    
    Args:
        cities_list (list): Liste des villes
        max_hotels_per_city (int): Nombre d'hôtels par ville
        
    Returns:
        dict: Registre mis à jour
    """
    print(f"\n{'='*80}")
    print(f"📤 STEP 1 : DÉCLENCHEMENT DES SCRAPINGS (POST)")
    print(f"{'='*80}")
    print(f"🏙️  Villes : {len(cities_list)}")
    print(f"🏨 Hôtels par ville : {max_hotels_per_city}")
    print(f"⏱️  Démarrage : {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Charger la config
    api_key, dataset_id = load_config()
    
    # Charger le registre existant
    registry = load_snapshot_registry()
    
    timeout = aiohttp.ClientTimeout(total=60)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        # Créer les tâches pour toutes les villes
        tasks = [
            trigger_city_scraping(session, city, max_hotels_per_city, api_key, dataset_id)
            for city in cities_list
        ]
        
        # Exécuter en parallèle
        results = await asyncio.gather(*tasks)
        
        # Mettre à jour le registre
        registry["timestamp"] = datetime.now().isoformat()
        
        success_count = 0
        for result in results:
            if result:
                registry["snapshots"][result["city"]] = result
                success_count += 1
        
        # Sauvegarder
        save_snapshot_registry(registry)
    
    print(f"\n{'='*80}")
    print(f"✅ STEP 1 TERMINÉ")
    print(f"{'='*80}")
    print(f"📊 Snapshots créés : {success_count}/{len(cities_list)}")
    print(f"📁 Registre : {SNAPSHOTS_REGISTRY}\n")
    
    return registry


# ═══════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE (si exécuté comme script)
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée pour exécution standalone."""
    import pandas as pd
    
    # Charger le Top 5
    top5 = pd.read_csv('data/processed/top5_destinations.csv')
    cities = top5['city'].tolist()
    
    print("🏆 Top 5 des destinations :")
    for i, city in enumerate(cities, 1):
        print(f"   {i}. {city}")
    
    # Lancer
    asyncio.run(trigger_all_cities(cities, max_hotels_per_city=15))


if __name__ == "__main__":
    main()
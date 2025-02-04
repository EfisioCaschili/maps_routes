#import geopy
import geopy.distance
import requests
from pathlib import Path
import os
try:
    from dotenv import dotenv_values, load_dotenv
except:
    from dotenv import main 

path=str(Path.cwd()) + '/'
try:
    env=dotenv_values(path+'env.env')
    GOOGLE_PLACES_API=env.get('Google_Places_API')
    BASE_URL=env.get('Base_Url')
    GOOGLE_DIRECTIONS_API=env.get('Google_Directions_API')
    BASE_DIRECTIONS_URL=env.get('BASE_DIRECTIONS_URL')
    GEOCODING_URL = env.get('GEOCODING_URL')
    GOOGLE_GEOCODING_API = env.get('GOOGLE_GEOCODING_API')
except: 
    env=main.load_dotenv(path+'env.env')
    GOOGLE_PLACES_API=os.getenv('Google_Places_API')
    BASE_URL=os.getenv('Base_Url')
    GOOGLE_DIRECTIONS_API=os.getenv('Google_Directions_API')
    BASE_DIRECTIONS_URL=os.getenv('BASE_DIRECTIONS_URL')
    GEOCODING_URL = os.getenv('GEOCODING_URL')
    GOOGLE_GEOCODING_API = os.getenv('GOOGLE_GEOCODING_API')

def fetch_places(lat, lon, radius=50000, keyword="scenic view"):
    params = {
        "key": GOOGLE_PLACES_API,
        "location": f"{lat},{lon}",
        "radius": radius,
        "keyword": keyword
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        places = response.json().get("results", [])
    else:
        print(f"Errore: {response.status_code}")
        return []
    sorted_places = sorted(places, key=lambda place: geopy.distance.distance(
            (lat, lon), (place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"])
        ).km)
    return sorted_places

def fetch_restaurants(lat, lon, radius=2000, keyword="restaurant|pub|caffè"):
    """Trova ristoranti o pub vicino a una posizione specifica."""
    params = {
        "key": GOOGLE_PLACES_API,
        "location": f"{lat},{lon}",
        "radius": radius,
        "keyword": keyword
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Errore Google Places API: {response.status_code}")
        return []

def generate_itinerary_old(lat, lon, places):
    """Genera un itinerario ottimizzato usando Google Directions API"""
    if not places:
        return {"error": "Nessun luogo trovato per creare un itinerario."}
    
    waypoints = "|".join([
        f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}" 
        for place in places[:5]  # Prendiamo i primi 5 luoghi più vicini
    ])

    params = {
        "key": GOOGLE_DIRECTIONS_API,
        "origin": f"{lat},{lon}",
        "destination": waypoints.split("|")[-1],  # Ultimo punto come destinazione finale
        "waypoints": waypoints,
        "optimize": "true"  # Ottimizza il percorso
    }
    
    response = requests.get(BASE_DIRECTIONS_URL, params=params)
    
    if response.status_code == 200:
        directions = response.json()
        return directions
    else:
        print(f"Error Directions API: {response.status_code}")
        return {}
    
def generate_itinerary(lat, lon, places):
    """Genera un itinerario ottimizzato con punti ristoro e output formattato."""
    if not places:
        return "❌ Nessun luogo trovato per creare un itinerario."

    waypoints = []
    itinerary = f"📍 **Itinerario da ({lat}, {lon})**\n\n"

    for i, place in enumerate(places[:5], start=1):
        place_name = place["name"]
        place_address = place.get("vicinity", "Indirizzo non disponibile")
        place_type = ", ".join(place["types"]) if "types" in place else "N/A"
        place_lat = place['geometry']['location']['lat']
        place_lon = place['geometry']['location']['lng']

        itinerary += f"🔹 {i}. {place_name} ({place_type})\n   📍 {place_address}\n"
        waypoints.append(f"{place_lat},{place_lon}")

        # Cerca un punto ristoro vicino
        restaurants = fetch_restaurants(place_lat, place_lon)
        if restaurants:
            best_restaurant = restaurants[0]
            rest_name = best_restaurant["name"]
            rest_address = best_restaurant.get("vicinity", "Indirizzo non disponibile")
            rest_lat = best_restaurant['geometry']['location']['lat']
            rest_lon = best_restaurant['geometry']['location']['lng']
            
            itinerary += f"   🍽️ **Ristoro consigliato:** {rest_name}\n   📍 {rest_address}\n"
            waypoints.append(f"{rest_lat},{rest_lon}")

        itinerary += "\n"

    waypoints = waypoints[:23]  # Limitiamo a 23 waypoint

    # Generiamo il percorso con Google Directions API
    params = {
        "key": GOOGLE_DIRECTIONS_API,
        "origin": f"{lat},{lon}",
        "destination": waypoints[-1],
        "waypoints": "|".join(waypoints),
        "optimize": "true"
    }

    response = requests.get(BASE_DIRECTIONS_URL, params=params)
    
    if response.status_code == 200:
        directions = response.json()
        total_distance = directions["routes"][0]["legs"][0]["distance"]["text"]
        total_duration = directions["routes"][0]["legs"][0]["duration"]["text"]
        itinerary += f"🛤️ **Distanza totale:** {total_distance}\n⏳ **Durata stimata:** {total_duration}\n"
    else:
        itinerary += "⚠️ Errore nel calcolo del percorso.\n"

    return itinerary



def get_coordinates(place_name):
    """Ottiene le coordinate (lat, lon) di un luogo dato il suo nome"""
    params = {
        "key": GOOGLE_GEOCODING_API,
        "address": place_name
    }
    
    response = requests.get(GEOCODING_URL, params=params)
    
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            location = results[0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None, None
    else:
        print(f"Errore Geocoding API: {response.status_code}")
        return None, None
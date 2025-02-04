from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="scenic_routes")

def generate_routes(center_lat, center_lon, radius_km=50):
    routes = []
    for lat_offset in range(-radius_km, radius_km, 10):
        for lon_offset in range(-radius_km, radius_km, 10):
            lat, lon = center_lat + lat_offset * 0.01, center_lon + lon_offset * 0.01
            location = geolocator.reverse((lat, lon), exactly_one=True)
            if location:
                routes.append({
                    "name": f"Path near to {location.address}",
                    "latitude": lat,
                    "longitude": lon,
                    "description": f"Scenic route near {location.address}",
                    "category": "panoramic"
                })
    return routes

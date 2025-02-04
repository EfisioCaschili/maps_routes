import json

def add_custom_route(name, latitude, longitude, description, category="panoramic"):
    new_route = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "description": description,
        "category": category
    }
    try:
        with open("/routes.json", "r") as file:
            routes = json.load(file)
    except FileNotFoundError:
        routes = []

    routes.append(new_route)

    with open("/routes.json", "w") as file:
        json.dump(routes, file, indent=4)
    print(f"Percorso aggiunto: {name}")

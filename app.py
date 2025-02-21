from flask import Flask, request, jsonify
from fetch_places import *
from route_generator import *
from crowdsourcing import *

app = Flask(__name__)

@app.route('/routes/fetch_place', methods=['GET'])
def fetch_place_call(): 
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')  
    radius = data.get('radius')
    if radius is None:
        radius=50000
    places= fetch_places(latitude,longitude,radius)
    #print(places)
    output=""
    for place in places:
        output+=(f"Name: {place['name']}, Address: {place.get('vicinity', 'N/A')}, Attraction type: {place['types']}\n")
    return output

@app.route('/routes/get_coordinates', methods=['GET'])
def get_coordinates_call():
    data = request.get_json()
    place = data.get('place')
    return jsonify(get_coordinates(place))


@app.route('/routes/generate_itinerary', methods=['GET'])
def generate_itinerary_call(): 
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')  
    radius = data.get('radius')
    place= data.get('place')
    if place is not None:
        latitude,longitude=get_coordinates(place)
    if radius is None:
        radius=50000
    places= fetch_places(latitude,longitude,radius)
    return jsonify(generate_itinerary(latitude,longitude,places))

@app.route("/routes/category/<category>", methods=["GET"])
def get_routes_by_category(category):
    """filtered_routes = [route for route in routes if route["category"].lower() == category.lower()]
    if not filtered_routes:
        return jsonify({"error": "No path found for this category."}), 404
    return jsonify(filtered_routes)"""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')  
    radius = data.get('radius')
    if radius is None:
        radius=50000
    places= fetch_places(latitude,longitude,radius)
    tmp=[]
    #places=[place for place in places if place["type"].lower() ==category.lower()]
    for place in places:
        try:
            if category.lower() in place["types"]:
                tmp.append(place)
        except Exception as comparisonErr:
            print(comparisonErr)
    return jsonify(tmp)





if __name__ == "__main__":
    app.run(host="0.0.0.0",port="5000",debug=True)

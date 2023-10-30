#!/usr/bin/python3
"""Defines routes and methods for the place resource"""
from flask import abort, make_response, request, jsonify
from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place
from models.user import User
from models.state import State
from models.amenity import Amenity

def create_response(data, status_code=200):
    response = make_response(jsonify(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

@app_views.route("/cities/<id>/places", methods=["GET"])
def get_places(id):
    city = storage.get(City, id)
    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return create_response(places)

@app_views.route("/places/<id>", methods=["GET"])
def get_place(id):
    place = storage.get(Place, id)
    if not place:
        abort(404)
    return create_response(place.to_dict())

@app_views.route("/places/<id>", methods=["DELETE"])
def delete_place(id):
    place = storage.get(Place, id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return create_response({})

@app_views.route("/cities/<id>/places", methods=["POST"])
def post_place(id):
    city = storage.get(City, id)
    if not city:
        abort(404)

    data = request.get_json()
    if not data:
        return create_response({"error": "Not a JSON"}, 400)

    user_id = data.get("user_id")
    if not user_id:
        return create_response({"error": "Missing user_id"}, 400)

    user = storage.get(User, user_id)
    if not user:
        abort(404)

    name = data.get("name")
    if not name:
        return create_response({"error": "Missing name"}, 400)

    data["city_id"] = id
    place = Place(**data)
    place.save()
    return create_response(place.to_dict(), 201)

@app_views.route("/places/<place_id>", methods=["PUT"])
def put_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    data = request.get_json()
    if not data:
        return create_response({"error": "Not a JSON"}, 400)

    ignore = ["id", "user_id", "city_id", "created_at", "updated_at"]
    for key, value in data.items():
        if key not in ignore:
            setattr(place, key, value)

    storage.save()
    return create_response(place.to_dict())

@app_views.route('/places_search', methods=['POST'])
def places_search_enhanced():
    data = request.get_json()
    if not data:
        return create_response({"error": "Not a JSON"}, 400)

    states = data.get("states", [])
    cities = data.get("cities", [])
    amenities = data.get("amenities", [])

    placesList = []

    for state_id in states:
        state = storage.get(State, state_id)
        if state:
            for city in state.cities:
                placesList.extend(place for place in city.places)

    for city_id in cities:
        city = storage.get(City, city_id)
        if city:
            for place in city.places:
                if place not in placesList:
                    placesList.append(place)

    if not placesList:
        placesList = storage.all(Place).values()

    for amenity_id in amenities:
        amenity = storage.get(Amenity, amenity_id)
        placesList = [place for place in placesList if amenity in place.amenities]

    places = [place.to_dict() for place in placesList]
    for place in places:
        place.pop("amenities", None)

    return create_response(places)

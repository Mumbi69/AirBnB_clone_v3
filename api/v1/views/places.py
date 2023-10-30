#!/usr/bin/python3
"""Defines routes and methods for the place resource"""
from flask import Flask, request, abort, jsonify
from api.v1.views import app_views
from models import storage
from models.state import State
from models.city import City
from models.place import Place
from models.user import User
from models.user import User
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'])
def places(city_id):
    city = storage.get(City, city_id)

    if city is None:
        abort(404)

    if request.method == 'GET':
        places_list = [place.to_dict() for place in city.places]
        return jsonify(places_list)

    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Not a JSON"}), 400
        user_id = data.get("user_id")
        if user_id is None:
            return jsonify({"error": "Missing user_id"}), 400
        user = storage.get(User, user_id)
        if user is None:
            abort(404)
        name = data.get("name")
        if name is None:
            return jsonify({"error": "Missing name"}), 400
        place = Place(**data)
        place.city_id = city.id
        place.save()
        return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['GET', 'PUT', 'DELETE'])
def place(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    if request.method == 'GET':
        return jsonify(place.to_dict())

    if request.method == 'PUT':
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Not a JSON"}), 400
        for key, value in data.items():
            if key not in \
                    ["id", "user_id", "city_id", "created_at", "updated_at"]:
                setattr(place, key, value)
        place.save()
        return jsonify(place.to_dict())

    if request.method == 'DELETE':
        storage.delete(place)
        storage.save()
        return jsonify({}), 200


def create_response(data, status_code=200):
    response = make_response(jsonify(data), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


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

    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    if not (states or cities or amenities):
        places = storage.all(Place).values()
        placesList = [place.to_dict() for place in places]
        return create_response(placesList)

    placesList = []
    for state_id in states:
        state = storage.get(City, state_id)
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
        place.pop('amenities', None)

    return create_response(places)

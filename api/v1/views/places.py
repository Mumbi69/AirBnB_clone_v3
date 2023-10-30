#!/usr/bin/python3
"""Defines routes and methods for the place resource"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.place import Place
from models.city import City
from models.user import User


@app_views.route('/cities/<cities_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    """Get places by city Id"""
    city = storage.get(City, city_id)

    if city is None:
        abort(404)

    places = city.places
    places_list = [place.to_dict() for place in places]
    return jsonify(places_list)


@app_views.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    """get a place by it's ID"""
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)

    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    """Delete a place base on it's id"""
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a new place"""
    city = storage.get(City, city_id)

    if city is None:
        abort(404)

    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")

    if 'user_id' not in request_data:
        abort(400, "Missing user_id")

    user = storage.get(User, request_data['user_id'])

    if user is None:
        abort(404)

    if 'name' not in request_data:
        abort(400, "Missing name")

    new_place = Place(**request_data)
    new_place = city_id = city_id
    storage.new(new_place)
    storage.save()

    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'])
def update_place(place_id):
    place = storage.get(Place, place_id)

    if place is None:
        abort(404)

    request_data = request.get_json()

    if request is None:
        abort(400, "Not a JSON")

    for key, value in request_data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()

    return jsonify(place.to_dict()), 200

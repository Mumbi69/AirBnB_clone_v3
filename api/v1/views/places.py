#!/usr/bin/python3
"""Defines routes and methods for the place resource"""
from flask import Flask, request, abort, jsonify
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User


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

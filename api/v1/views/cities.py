#!/usr/bin/python3
"""Defines routes and methods for the city resource"""
from api.v1.views import app_views
from flask import jsonify, abort
from models import storage
from models.state import State
from models.state import City
import json


def make_json_response(data, status_code):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

@app_views.route("/states/<id_state>/cities", methods=["GET"])
def get_cities(id_state):
    """Retrieves all cities by state id"""
    state = storage.get(State, id_state)
    if not state:
        abort(404)

    citiesList = [city.to_dict() for city in state.cities]
    return make_json_response(citiesList, 200)

@app_views.route("/cities/<id>", methods=["GET"])
def get_city(id):
    """Retrieves city object by id"""
    city = storage.get(City, id)
    if not city:
        abort(404)
    return make_json_response(city.to_dict(), 200)

@app_views.route("/cities/<id>", methods=["DELETE"])
def delete_city(id):
    """Deletes city by id"""
    city = storage.get(City, id)
    if not city:
        abort(404)

    storage.delete(city)
    storage.save()
    return make_json_response({}, 200)

@app_views.route("/states/<id_state>/cities", methods=["POST"])
def create_city(id_state):
    """Inserts a city if it's valid JSON with the correct keys and state id"""
    state = storage.get(State, id_state)
    if not state:
        abort(404)

    data = request.get_json()
    if not data or "name" not in data:
        return make_json_response({"error": "Missing name"}, 400)

    data["state_id"] = id_state
    instObj = City(**data)
    instObj.save()
    return make_json_response(instObj.to_dict(), 201)

@app_views.route("/cities/<id>", methods=["PUT"])
def put_city(id):
    """Updates a city by id"""
    city = storage.get(City, id)
    if not city:
        abort(404)

    data = request.get_json()
    if not data:
        return make_json_response({"error": "Not a JSON"}, 400)

    ignore_keys = ["id", "state_id", "created_at", "updated_at"]
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(city, key, value)

    storage.save()
    return make_json_response(city.to_dict(), 200)

#!/usr/bin/python3
"""Defines routes and methods for the state resource"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.state import State


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_states():
    """Returns all the states objects"""

    states = storage.all(State).values()
    state_list = [state.to_dict() for state in states]
    return jsonify(state_list)


@app_views.route('/states/<state_id>', methods=['GET'])
def get_state_by_id(state_id):
    """Returns a state based on the specified id"""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route('/states/<state_id>', methods=['DELETE'])
def delete_state(state_id):
    """Deletes a states based on it's ID"""
    state = storage.get(State, state_id)

    if state is None:
        abort(404)

    storage.delete(state)
    storage.save()
    return jsonify({}), 200


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")
    if 'name' not in request_data:
        abort(400, "Missing name")

    new_state = State(**request_data)
    storage.new(new_state)
    storage.save()

    return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['PUT'])
def update_state(state_id):
    """Updates a state based on it's ID"""
    state = storage.get(State, state_id)

    if state is None:
        abort(400)

    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")

    for key, value in request_data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(state, key, value)

    storage.save()

    return jsonify(state.to_dict()), 200

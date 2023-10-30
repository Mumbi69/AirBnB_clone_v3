#!/usr/bin/python3
"""Defines routes and methods for the user resource"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.user import User


@app_views.route('/users', methods=['GET'], strict_slashes=False)
def get_users():
    """Returns all the users objects"""

    users = storage.all(User).values()
    user_list = [user.to_dict() for user in users]
    return jsonify(user_list)


@app_views.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Returns a user based on the specified id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_dict())


@app_views.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletes a users based on it's ID"""
    user = storage.get(User, user_id)

    if user is None:
        abort(404)

    storage.delete(user)
    storage.save()
    return jsonify({}), 200


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user():
    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")
    if 'email' not in request_data:
        abort(400, "Missing email")
    elif 'password' not in request_data:
        abort(400, "Missing password")

    new_user = User(**request_data)
    storage.new(new_user)
    storage.save()

    return jsonify(new_user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Updates a user based on it's ID"""
    user = storage.get(User, user_id)

    if user is None:
        abort(404)

    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")

    for key, value in request_data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(user, key, value)

    storage.save()

    return jsonify(user.to_dict()), 200

#!/usr/bin/python3
"""Defines routes and methods for the amenity resource"""
from api.v1.views import app_views
from flask import jsonify, request, abort
from models import storage
from models.amenity import Amenity


@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
def get_amenities():
    """Returns all the amenities objects"""

    amenities = storage.all(Amenity).values()
    amenity_list = [amenity.to_dict() for amenity in amenities]
    return jsonify(amenity_list)


@app_views.route('/amenities/<amenity_id>', methods=['GET'])
def get_amenity_by_id(amenity_id):
    """Returns a amenity based on the specified id"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    return jsonify(amenity.to_dict())


@app_views.route('/amenities/<amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    """Deletes a amenities based on it's ID"""
    amenity = storage.get(Amenity, amenity_id)

    if amenity is None:
        abort(404)

    storage.delete(amenity)
    storage.save()
    return jsonify({}), 200


@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
def create_amenity():
    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")
    if 'name' not in request_data:
        abort(400, "Missing name")

    new_amenity = Amenity(**request_data)
    storage.new(new_amenity)
    storage.save()

    return jsonify(new_amenity.to_dict()), 201


@app_views.route('/amenities/<amenity_id>', methods=['PUT'])
def update_amenity(amenity_id):
    """Updates a amenity based on it's ID"""
    amenity = storage.get(Amenity, amenity_id)

    if amenity is None:
        abort(404)

    request_data = request.get_json()

    if request_data is None:
        abort(400, "Not a JSON")

    for key, value in request_data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(amenity, key, value)

    storage.save()

    return jsonify(amenity.to_dict()), 200

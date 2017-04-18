# -*- coding: utf-8 -*-
"""
    api.resources.rest
    ~~~~~~~~~~~~~~~~
    REST API resources
"""
from datetime import datetime
from toolz import dissoc, keyfilter, valmap
from flask import request
from jsonschema import validate, ValidationError
from unidecode import unidecode
from flask_restful import Resource, abort
from flask_jwt import jwt_required
from werkzeug import exceptions as e
from aidex.models import User, Org, Location
from api.helpers import (
    uuid, try_committing, get_entity, check_existence)
from aidex.core import db


class Validatable(object):
    schema = None

    def validate_form(self, data):
        try:
            validate(data, self.schema)
        except ValidationError as ve:
            raise e.BadRequest('{}: {}'.format(self.uri, ve.message))


class UsersEndpoint(Validatable, Resource):
    uri = "/users"
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "user",
        "type": "object",
        "properties": {
            "email": {"type": "string"},
            "name": {"type": "string"},
            "phone": {"type": "string"},
            "password": {"type": "string"}},
        "required": ["email", "name", "phone", "password"]
    }

    def post(self):
        self.validate_form(request.json)

        if check_existence(User, User.email == request.json['email']):
            abort(400, 'User {} already exists'
                  .format(request.json['email']))

        new_user = User(
            id=uuid(),
            email=request.json['email'],
            name=unidecode(request.json['name']),
            phone=request.json['phone'],
            timestamp=datetime.now(),
            password=request.json['password'])

        db.session.add(new_user)
        try_committing(db.session)

        return {"success": True, "user_id": new_user.id}, 201


class OrgsEndpoint(Validatable, Resource):
    uri = "/orgs"
    method_decorators = [jwt_required()]
    schema = {
        "type": "object",
        "title": "org",
        "properties": {
            "user_id": {"type": "string"},
            "org_id": {"type" "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "fiveoone": {"type": "string"},
            "phone": {"type": "string"},
            "mission": {"type": "string"},
            "services": {
                "type": "array",
                "items": {
                    "type": "string"
                }},
            "established": {"type": "string"},
            "location": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                }
            }
        },
        "required": ["user_id", "name", "location", "services"]
    }

    def get(self):
        orgs = [
            org.as_dict()
            for org in Org.query.all()]
        return {"count": len(orgs),
                "orgs": orgs}

    def _create_location(self, location):
        return Location(
            city=location['city'],
            address=location['address'],
            country=location['country'])

    def _create_org(self, data, new_location):
        return Org(
            id=uuid(),
            location=new_location,
            location_id=new_location.id,
            timestamp=datetime.now(),
            **data
        )

    def _clean_data(self, data):
        relevant_data = keyfilter(
            lambda key: key in self.schema["properties"], data)
        cleaned_data = valmap(
            unidecode, dissoc(relevant_data, "services", "location"))

        if "services" in data:
            cleaned_data["services"] = [unidecode(v) for v in data["services"]]
        if "location" in data:
            relevant_loc_data = keyfilter(
                lambda key: key in self.schema["properties"]["location"]["properties"],
                data["location"])
            cleaned_data["location"] = valmap(
                unidecode,
                relevant_loc_data)
        return cleaned_data

    def put(self):
        user_id = request.json["user_id"]
        user = get_entity(User, user_id)

        org_id = request.json["org_id"]
        org = get_entity(Org, org_id, True)
        if user not in org.organizers:
            abort(403, "{} is not an organizer of {}, can't update".format(
                user_id, org_id))

        cleaned_data = self._clean_data(request.json)
        for key, value in dissoc(cleaned_data, "location").items():
            setattr(org, key, value)
        if "location" in cleaned_data:
            new_location = self._create_location(cleaned_data["location"])
            db.session.add(new_location)
            org.location = new_location
            org.location_id = new_location.id

        try_committing(db.session)
        return {"org_id": org.id, "user_id": user_id}, 200

    def post(self):
        self.validate_form(request.json)

        user_id = request.json["user_id"]
        user = get_entity(User, user_id, True)

        name = request.json["name"]
        if Org.query.filter_by(name=name).first():
            abort(409, "Org {} already exists".format(name))

        cleaned_data = self._clean_data(request.json)
        new_location = self._create_location(request.json["location"])
        new_org = self._create_org(cleaned_data, new_location)
        new_org.organizers = [user]

        db.session.add(new_location)
        db.session.add(new_org)
        try_committing(db.session)

        return {"org_id": new_org.id,
                "user_id": user_id}, 201


class FollowEndpoint(Validatable, Resource):
    uri = "/follow"
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "org_id": {"type": "string"}},
        "required": ["user_id"]
    }

    def _get_entites(self, data):
        if "org_id" not in data:
            abort(400, "Need an org_id to (un)follow")
        user = get_entity(User, data['user_id'], True)
        org = get_entity(Org, data['org_id'], True)

        return user, org

    def post(self):
        self.validate_form(request.json)
        user, org = self._get_entites(request.json)
        if org in user.following:
            abort(409, "User {} is already following {}".format(user.email, org.name))
        user.following.append(org)
        try_committing(db.session)
        return 204

    def get(self):
        self.validate_form(request.json)
        user = get_entity(User, request.json["user_id"])
        followed_orgs = [org.as_dict() for org in user.following]
        return {"count": len(followed_orgs),
                "followed_orgs": followed_orgs}


class UnfollowEndpoint(FollowEndpoint, Validatable, Resource):
    uri = "/unfollow"
    method_decorators = [jwt_required()]

    def post(self):
        self.validate_form(request.json)
        user, org = self._get_entites(request.json)
        if org not in user.following:
            abort(400, "User {} is not following {}".format(user.email, org.name))
        user.following.remove(org)
        try_committing(db.session)
        return 200


endpoints = [UsersEndpoint, OrgsEndpoint, FollowEndpoint]

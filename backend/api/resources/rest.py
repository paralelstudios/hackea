# -*- coding: utf-8 -*-
"""
    api.resources.rest
    ~~~~~~~~~~~~~~~~
    REST API resources
"""
from toolz import dissoc, keyfilter, valmap
from flask import request
from jsonschema import validate, ValidationError
from unidecode import unidecode
from flask_restful import Resource
from flask_jwt import jwt_required
from werkzeug import exceptions as e
from aidex.models import User, Org, Location
from api.helpers import uuid, try_committing
from aidex.core import db


class Validatable(object):
    schema = None

    def validate_form(self, data):
        try:
            validate(data, self.schema)
        except ValidationError as ve:
            raise e.BadRequest('POST {}: {}'.format(self.uri, ve.message))


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

        if User.query.filter_by(email=request.json['email']).first():
            return {
                'message': 'User {} already exists'
                .format(request.json['email'])}, 400

        new_user = User(
            id=uuid(),
            email=request.json['email'],
            name=unidecode(request.json['name']),
            phone=request.json['phone'],
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
        user = User.query.get(user_id)
        if not user:
            return {"message": "User {} doesn't exist".format(user_id)}, 400

        org_id = request.json["org_id"]
        org = Org.query.with_for_update().get(org_id)
        if not org:
            return {"message": "Org {} doesn't exist".format(org_id)}, 400

        cleaned_data = self._clean_data(request.json)
        for key, value in dissoc(cleaned_data, "location").items():
            setattr(org, key, value)
        if "location" in cleaned_data:
            new_location = self._create_location(cleaned_data["location"])
            db.session.add(new_location)
            org.location = new_location
            org.location_id = new_location.id

        try_committing()

    def post(self):
        self.validate_form(request.json)

        user_id = request.json["user_id"]
        user = User.query.get(user_id)
        if not user:
            return {"message": "User {} doesn't exist".format(user_id)}, 400

        name = request.json["name"]
        if Org.query.filter_by(name=name).first():
            return {"message": "Org {} already exists".format(name)}, 400

        cleaned_data = self._clean_data(request.json)
        new_location = self._create_location(request.json["location"])
        new_org = self._create_org(cleaned_data, new_location)
        new_org.organizers = [user]

        db.session.add(new_location)
        db.session.add(new_org)
        try_committing(db.session)

        return {"success": True,
                "org_id": new_org.id,
                "user_id": user_id}, 201


endpoints = [UsersEndpoint, OrgsEndpoint]

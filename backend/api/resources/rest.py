# -*- coding: utf-8 -*-
"""
    api.resources.rest
    ~~~~~~~~~~~~~~~~
    REST API resources
"""
from flask import request
import json
from jsonschema import validate, ValidationError
from unidecode import unidecode
from flask_restful import Resource
from flask_jwt import jwt_required
from werkzeug import exceptions as e
from aidex.models import User, Org
from api.helpers import (
    DateTimeEncoder,
    uuid, try_committing)
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
            "name": {"type": "string"}},
        "required": ["user_id", "name"]
    }

    def get(self):
        orgs = [
            org.as_dict()
            for org in Org.query.all()]
        return {"count": len(orgs),
                "orgs": json.dumps(orgs, cls=DateTimeEncoder)}

    def post(self):
        self.validate_form(request.json)
        name = request.json["name"]
        user_id = request.json["user_id"]
        user = User.query.get(user_id)

        if not user:
            return {"message": "User {} doesn't exist".format(user_id)}, 400

        if Org.query.filter_by(name=name).first():
            return {"message": "Org {} already exists".format(name)}, 400

        new_org = Org(
            id=uuid(),
            name=unidecode(name))

        new_org.organizers.append(user)

        db.session.add(new_org)
        try_committing(db.session)

        return {"success": True,
                "org_id": new_org.id,
                "user_id": user_id}, 201


endpoints = [UsersEndpoint, OrgsEndpoint]

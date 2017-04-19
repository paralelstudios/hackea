# -*- coding: utf-8 -*-
"""
    api.resources.base
    ~~~~~~~~~~~~~~~~
    Base API stuff
"""

from werkzeug import exceptions as e
from jsonschema import validate, ValidationError
from flask_restful import Resource
from flask_jwt import jwt_required


class Validatable(object):
    schema = None

    def validate_form(self, data):
        try:
            validate(data, self.schema)
        except ValidationError as ve:
            raise e.BadRequest('{}: {}'.format(self.uri, ve.message))


class Endpoint(Validatable, Resource):
    pass


class JWTEndpoint(Endpoint):
    method_decorators = [jwt_required()]

# -*- coding: utf-8 -*-
"""
    api.resources.users
    ~~~~~~~~~~~~~~~~
    Users API resources
"""
from unidecode import unidecode
from toolz import keyfilter
from flask import request
from flask_restful import abort
from aidex.core import db
from aidex.models import User
from aidex.helpers import check_existence, try_committing, create_user
from .base import Endpoint


class UsersEndpoint(Endpoint):
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

    def _clean_data(self, data):
        relevant_data = keyfilter(
            lambda key: key in self.schema["properties"], data)
        relevant_data["name"] = unidecode(relevant_data["name"])
        return relevant_data

    def post(self):
        print("recieved {}".format(request.json))
        self.validate_form(request.json)
        cleaned_data = self._clean_data(request.json)
        print("cleaned and validated")
        if check_existence(User, User.email == cleaned_data['email']):
            abort(409, description='User {} already exists'
                  .format(cleaned_data['email']))
        print("creating")
        new_user = create_user(cleaned_data)

        db.session.add(new_user)
        try_committing(db.session)
        print("created and committed")
        return {"user_id": new_user.id}, 201


ENDPOINTS = [UsersEndpoint]

# -*- coding: utf-8 -*-
"""
    api.resources.orgs
    ~~~~~~~~~~~~~~~~
    Organization API resources
"""
from flask import request, jsonify
from flask_restful import abort
from toolz import dissoc, keyfilter, valmap
from aidex.models import Org, User
from aidex.core import db
from aidex.helpers import (
    try_committing, create_location, create_org)
from ..helpers import get_entity, check_if_org_owner, clean_input
from .base import JWTEndpoint


class OrgsEndpoint(JWTEndpoint):
    uri = "/orgs"
    schema = {
        "type": "object",
        "title": "org",
        "properties": {
            "user_id": {"type": "string"},
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
        if "org_id" not in request.json:
            abort(400, description="org_id needed to get an org")
        org = get_entity(Org, request.json["org_id"])
        return jsonify(org.as_dict())

    def _clean_data(self, data):
        relevant_data = keyfilter(
            lambda key: key in self.schema["properties"], data)
        cleaned_data = valmap(
            clean_input, dissoc(relevant_data, "services", "location", "user_id"))

        if "services" in data:
            cleaned_data["services"] = [clean_input(v) for v in data["services"]]
        if "location" in data:
            relevant_loc_data = keyfilter(
                lambda key: key in self.schema["properties"]["location"]["properties"],
                data["location"])
            cleaned_data["location"] = valmap(
                clean_input,
                relevant_loc_data)
        return cleaned_data

    def put(self):
        if not ("user_id" in request.json and "org_id" in request.json):
            abort(400, description="org_id and user_id needed to update an org")
        user_id = request.json["user_id"]
        user = get_entity(User, user_id)

        org_id = request.json["org_id"]
        org = get_entity(Org, org_id, True)
        check_if_org_owner(user, org)

        cleaned_data = self._clean_data(request.json)
        for key, value in dissoc(cleaned_data, "location").items():
            setattr(org, key, value)
        if "location" in cleaned_data:
            new_location = create_location(cleaned_data["location"])
            db.session.add(new_location)
            org.location = new_location
            org.location_id = new_location.id

        try_committing(db.session)
        return {"org_id": org.id, "user_id": user_id}, 200

    def post(self):
        self.validate_form(request.json)

        user_id = request.json["user_id"]
        user = get_entity(User, user_id, True)
        cleaned_data = self._clean_data(request.json)
        name = cleaned_data["name"]
        if Org.query.filter_by(name=name).first():
            abort(409, description="Org {} already exists".format(name))

        new_location = create_location(cleaned_data["location"])
        new_org = create_org(cleaned_data, new_location)
        new_org.organizers = [user]

        db.session.add(new_location)
        db.session.add(new_org)
        try_committing(db.session)

        return {"org_id": new_org.id,
                "user_id": user_id}, 201


ENDPOINTS = [OrgsEndpoint]

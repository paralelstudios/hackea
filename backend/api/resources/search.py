# -*- coding: utf-8 -*-
"""
    api.resources.search
    ~~~~~~~~~~~~~~~~
    Search API resources
"""
from flask import request, jsonify
from sqlalchemy import func
from .base import JWTEndpoint
from aidex.models import Org, Event
from ..helpers import to_regex_or


class SearchEndpoint(JWTEndpoint):
    uri = "/search"
    _default_limit = 10

    schema = {
        "type": "object",
        "properties": {
            "event": {"type": "boolean"},
            "keywords": {
                "type": "array",
                "items": {
                    "type": "string"
                }},
            "categories": {
                "type": "array",
                "items": {
                    "type": "string",
                }},
            "location": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "country": {"type": "string"}}},
            "limit": {"type": "integer"},
            "offset": {"type": "integer"},
            "page": {"type": "integer"}},
        "required": ["keywords"]
    }

    def _form_conditions(self, parameters):
        keyword_regex = to_regex_or(parameters["keywords"])
        conditions = [Org.name.op('*~')(keyword_regex),
                      func.array_to_string(Org.services, " ").op('*~')(keyword_regex),
                      Org.mission.op('*~')(keyword_regex)]
        if "location" in parameters:
            if "city" in parameters["location"]:
                conditions.append(
                    Org.location.city.ilike(parameters["location"]["city"]))
            if "country" in parameters["location"]:
                conditions.append(
                    Org.location.country.ilike(parameters["location"]["country"]))
            if "categories" in parameters:
                categories_regex = to_regex_or(parameters["categories"])
                conditions.append(
                    func.array_to_string(Org.categories, " ").op("*~")(categories_regex))

    def _process_limit_and_offset(self, parameters):
        page = 1 if "page" not in parameters else parameters["page"]
        limit = self._default_limit if "limit" not in parameters else parameters["limit"]
        offset = 0 if "offset" not in parameters else parameters["offset"] + limit * page
        return limit, offset

    def get(self):
        self.validate_form(request.json)
        conditions = self._form_conditions(request.json)
        limit, offset = self._process_limit_and_offset(request.json)
        if "event" not in request.json or not request.json["event"]:
            model = Org
        else:
            model = Event

        matches = list(model.query.filter(*conditions).limit(limit).offset(offset))
        return jsonify({
            "count": len(matches),
            "matches": [m.as_dict() for m in matches]})


ENDPOINTS = [SearchEndpoint]

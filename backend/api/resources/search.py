# -*- coding: utf-8 -*-
"""
    api.resources.search
    ~~~~~~~~~~~~~~~~
    Search API resources
"""
from flask import request, jsonify
from unidecode import unidecode
from sqlalchemy import func, or_
from aidex.core import db
from aidex.models import Org, Location
from .base import JWTEndpoint
from ..helpers import to_regex_or, get_page_offset


class SearchEndpoint(JWTEndpoint):
    uri = "/search"
    _default_limit = 10

    schema = {
        "type": "object",
        "properties": {
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
            "cities": {
                "type": "array",
                "items": {
                    "type": "string"
                }},
            "country": {"type": "string"},
            "limit": {"type": "integer"},
            "page": {"type": "integer"}},
    }

    def _join_locations(self, parameters, query):
        loc_filters = []
        if "cities" in parameters:
            cities_regex = unidecode(to_regex_or(*parameters["cities"]))
            loc_filters.append(Location.city.op('~*')(cities_regex))
        if "country" in parameters:
            loc_filters.append(Location.country
                               .ilike(unidecode(parameters["location"]["country"])))
        if loc_filters:
            return query.join(Location).filter(*loc_filters)
        return query

    def _form_query(self, parameters):
        query = db.session.query(Org)
        if "keywords" in parameters:
            keyword_regex = unidecode(to_regex_or(*parameters["keywords"]))
            query = query.filter(
                or_(Org.name.op('~*')(keyword_regex),
                    func.array_to_string(Org.services, " ").op('~*')(keyword_regex),
                    Org.mission.op('~*')(keyword_regex)))
        if "categories" in parameters:
            categories_regex = unidecode(to_regex_or(*parameters["categories"]))
            query = query.filter(
                func.array_to_string(Org.categories, " ").op("~*")(categories_regex))

        return self._join_locations(parameters, query)

    def _process_limit_and_offset(self, parameters):
        page = 1 if "page" not in parameters else parameters["page"]
        limit = self._default_limit if "limit" not in parameters else parameters["limit"]
        offset = get_page_offset(page, limit)
        return limit, offset

    def get(self):
        self.validate_form(request.json)
        query = self._form_query(request.json)
        limit, offset = self._process_limit_and_offset(request.json)
        matches = query.limit(limit).offset(offset).all()
        return jsonify({
            "count": len(matches),
            "matches": matches})


ENDPOINTS = [SearchEndpoint]

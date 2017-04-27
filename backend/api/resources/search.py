# -*- coding: utf-8 -*-
"""
    api.resources.search
    ~~~~~~~~~~~~~~~~
    Search API resources
"""
from flask import request, jsonify
from aidex.queries import filter_orgs
from aidex.core import db
from aidex.models import Org
from .base import JWTEndpoint
from ..helpers import get_page_offset


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

    def _process_limit_and_offset(self, parameters):
        page = 1 if "page" not in parameters else parameters["page"]
        limit = self._default_limit if "limit" not in parameters else parameters["limit"]
        offset = get_page_offset(page, limit)
        return limit, offset

    def get(self):
        self.validate_form(request.json)
        query = filter_orgs(db.session.query(Org), **request.json)
        limit, offset = self._process_limit_and_offset(request.json)
        matches = query.limit(limit).offset(offset).all()
        return jsonify({
            "count": len(matches),
            "matches": matches})


ENDPOINTS = [SearchEndpoint]

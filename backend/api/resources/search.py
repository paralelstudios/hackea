# -*- coding: utf-8 -*-
"""
    api.resources.search
    ~~~~~~~~~~~~~~~~
    Search API resources
"""
from flask import request, jsonify, abort
from aidex.queries import filter_orgs
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
            "limit": {"type": "string"},
            "page": {"type": "string"}},
    }

    def _process_limit_and_offset(self, parameters):
        try:
            page = int(parameters.get("page", 1))
            limit = int(parameters.get("limit", self._default_limit))
        except ValueError:
            abort(400, description="page and/or limit have to be valid integers")
        offset = get_page_offset(page, limit)
        return page, limit, offset

    def get(self):
        if not (request.args.keys() & self.schema["properties"].keys()):
            abort(400, description="Need some search criteria")
        query = filter_orgs(Org.query,
                            keywords=request.args.getlist("keywords"),
                            categories=request.args.getlist("categories"),
                            cities=request.args.getlist("cities"),
                            country=request.args.get("country"))
        page, limit, offset = self._process_limit_and_offset(request.args)
        matches = query.limit(limit).offset(offset).all()
        return jsonify({
            "count": len(matches),
            "matches": matches,
            "page": page})


ENDPOINTS = [SearchEndpoint]

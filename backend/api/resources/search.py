# -*- coding: utf-8 -*-
"""
    api.resources.rest
    ~~~~~~~~~~~~~~~~
    REST API resources
"""

from .base import JWTEndpoint


class SearchEndpoint(JWTEndpoint):
    uri = "/search"
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
                }}},
        "required": ["keywords"]
    }

    def get(self):
        self.validate_form


ENDPOINTS = [SearchEndpoint]

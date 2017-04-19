# -*- coding: utf-8 -*-
"""
    api.resources.rest
    ~~~~~~~~~~~~~~~~
    REST API resources
"""

from .base import JWTEndpoint


class SearchEndpoint(JWTEndpoint):
    uri = "/search"

    def post(self):
        pass

    def put(self):
        pass

    def get(self):
        pass


ENDPOINTS = [SearchEndpoint]

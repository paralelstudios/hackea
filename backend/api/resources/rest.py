# -*- coding: utf-8 -*-
"""
    api.resources.rest
    ~~~~~~~~~~~~~~~~
    REST API resources
"""

from . import events, search, users, orgs, following

ENDPOINTS = events.ENDPOINTS + \
            search.ENDPOINTS + \
            users.ENDPOINTS + \
            following.ENDPOINTS + \
            orgs.ENDPOINTS

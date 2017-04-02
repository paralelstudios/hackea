# -*- coding: utf-8 -*-
"""
    api.factory
    ~~~~~~~~~~~~~~~~
    App factory for hackea API
"""

from hackea.core import factory, db
from hackea.models import User
import flask_restful as restful
from .helpers import request_accepts_json, handle_http_error
from .core import HackeaAPI, RestfulAPI
from .exceptions import default_exceptions

import resources



def create_app(package_name, **kwargs):
    app = factory.create_app(__name__, **kwargs)
    app.url_map.strict_slashes = False

    for code in default_exceptions:
        app.errorhandler(code)(handle_http_error)
    app.errorhandler(AssertionError)(handle_http_error)

    api = HackeaAPI(app)
    api._restful_api.representations['application/xml'] = resources.output_xml
    api.register_resources(*resources.__all__)
    return app

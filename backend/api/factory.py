# -*- coding: utf-8 -*-
"""
    api.factory
    ~~~~~~~~~~~~~~~~
    App factory for hackea API
"""

from hackea.core import factory
from .helpers import output_xml, authenticate, identity
from .core import HackeaAPI
from .resources import sms, rest
from flask_jwt import JWT


def create_app(package_name, **kwargs):
    app = factory.create_app(__name__, **kwargs)
    app.url_map.strict_slashes = False

    api = HackeaAPI(app)
    jwt = JWT(app, authenticate, identity)  # noqa
    api._restful_api.representations['application/xml'] = output_xml
    api.register_resources(*(sms.endpoints + rest.endpoints))
    return app

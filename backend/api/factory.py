# -*- coding: utf-8 -*-
"""
    api.factory
    ~~~~~~~~~~~~~~~~
    App factory for hackea API
"""

from hackea.core import factory, db
from hackea.models import User
import flask_restful as restful
from .helpers import output_xml
from .core import HackeaAPI
from .resources import endpoints, output_xml



def create_app(package_name, **kwargs):
    app = factory.create_app(__name__, **kwargs)
    app.url_map.strict_slashes = False

    api = HackeaAPI(app)
    api._restful_api.representations['application/xml'] = output_xml
    api.register_resources(*endpoints)
    return app

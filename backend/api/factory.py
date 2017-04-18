# -*- coding: utf-8 -*-
"""
    api.factory
    ~~~~~~~~~~~~~~~~
    App factory for aidex API
"""

import os
from flask_jwt import JWT
from aidex.core import factory
from .helpers import (
    output_xml, authenticate, identity,
    DateTimeEncoder)
from .core import AIDEXAPI
from .resources import sms, rest


def create_app(package_name, **kwargs):
    app = factory.create_app(package_name, **kwargs)
    app.config.from_object('settings.Config')
    if os.getenv('AIDEX_API_CONFIG_FILE'):
        app.config.from_envvar('AIDEX_API_CONFIG_FILE')
    app.json_encoder = DateTimeEncoder
    app.url_map.strict_slashes = False

    api = AIDEXAPI(app)
    jwt = JWT(app, authenticate, identity)  # noqa
    api._restful_api.representations['application/xml'] = output_xml
    api.register_resources(*sms.endpoints)
    api.register_resources(*rest.endpoints)
    return app

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


def create_app(package_name, settings_module=None, settings_override=None, **kwargs):
    app = factory.create_app(package_name,
                             settings_module=settings_module,
                             settings_override=settings_override,
                             **kwargs)
    app.config.from_object('api.settings')
    if settings_module:
        app.config.from_object(settings_module)
    if os.getenv('AIDEX_API_CONFIG_FILE'):
        app.config.from_envvar('AIDEX_API_CONFIG_FILE')
    app.json_encoder = DateTimeEncoder
    app.url_map.strict_slashes = False

    if settings_override:
        for key, value in settings_override:
            if key.isupper():
                app.config[key] = value

    api = AIDEXAPI(app)
    jwt = JWT(app, authenticate, identity)  # noqa
    api._restful_api.representations['application/xml'] = output_xml
    api.register_resources(*sms.endpoints)
    api.register_resources(*rest.ENDPOINTS)
    return app

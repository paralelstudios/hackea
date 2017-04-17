# -*- coding: utf-8 -*-
"""
    aidex.core.factory
    ~~~~~~~~~~~~~~~~~~~~
    app factory function
"""

import os
import sys
import logging
from flask import Flask
from . import db


def create_app(package_name, settings_module=None, settings_override=None):
    app = Flask(package_name)
    app.config.from_object('aidex.settings')
    if os.getenv('AIDEX_CONFIG_FILE'):
        app.config.from_envvar('AIDEX_CONFIG_FILE')

    if settings_override:
        for key, value in settings_override:
            if key.isupper():
                app.config[key] = value

    dirs = (
        app.config['DATA_DIR'],
        app.config['LOGGING_DIR']
    )

    for path in dirs:
        try:
            os.makedirs(path)
        except:
            pass

    # if we're in debug mode and databases are not localhost, show a warning
    if app.config['DEBUG'] or app.config['TESTING']:
        warnings = [
            key + " is not localhost"
            for key in {'SQLALCHEMY_DATABASE_URI'}
            if app.config.get(key) and 'localhost' not in app.config[key]]
        map(app.logger.warn, warnings)
        if app.config['TESTING'] and warnings:
            raise Exception(
                'RUNNING TESTS ON A NONLOCAL DATABASE IS A DESTRUCTIVE ACTION')
    db.init_app(app)
    if not app.debug:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    return app

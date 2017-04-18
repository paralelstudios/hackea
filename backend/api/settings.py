# -*- coding: utf-8 -*-
"""
    api.settings
    ~~~~~~~~~~~~~~~~
    Global backend package settings
"""


class Config(object):
    TWILIO_API_SID = None
    DEBUG = True
    TWILIO_API_SECRET = None
    SECRET_KEY = "3aa68944-4a88-4200-9b16-694e3319e236"
    JWT_AUTH_USERNAME_KEY = "email"


class TestingConfig(Config):
    TESTING = True

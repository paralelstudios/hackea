# -*- coding: utf-8 -*-
"""
    hackea.settings
    ~~~~~~~~~~~~~~~~
    Global backend package settings
"""

import os

ENVIRONMENT = 'local'
DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGGING_DIR = os.path.join(BASE_DIR, "log")

# SQL DB settings
DB_USER = os.environ.get('POSTGRES_ENV_POSTGRES_USER', 'hackea')
DB_PASSWORD = os.environ.get('POSTGRES_ENV_POSTGRES_PASSWORD', 'hackea')
DB_HOST = os.environ.get('POSTGRES_PORT_5432_TCP_ADDR', 'localhost')
DB_PORT = int(os.environ.get('POSTGRES_PORT_5432_TCP_PORT', 5432))
SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_USER)
SQLALCHEMY_LOG_QUERIES = False
SQLALCHEMY_TRACK_MODIFICATIONS = False


# AWS credentials
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None
AWS_REGION = 'us-east-1'

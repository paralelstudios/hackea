# -*- coding: utf-8 -*-
"""
    hackea.settings
    ~~~~~~~~~~~~~~~~
    Global backend package settings
"""

import os
import operator
from datetime import datetime

ENVIRONMENT = 'local'
DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGGING_DIR = os.path.join(BASE_DIR, "log")

# SQL DB settings
SQLALCHEMY_DATABASE_URI = 'postgresql://hackea:hackea@localhost/hackea'
SQLALCHEMY_LOG_QUERIES = False

# AWS credentials
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None
AWS_REGION = 'us-east-1'

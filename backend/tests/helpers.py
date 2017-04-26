# -*- coding: utf-8 -*-
"""
    tests.helpers
    ~~~~~~~~~~~~~~~~~~~~~
    test utility functions
"""
from uuid import UUID
from api.helpers import DateTimeEncoder
import json


def validate_uuid(s):
    """
    takes a str and verifies that it's a valid uuid4
    """

    try:
        uuid = UUID(s, version=4)
    except ValueError:
        # ensure that the s passed in is proper UUID hex code
        return False

    # ensure that the generated UUID matches the str passed in
    return uuid.hex == s.replace('-', '')


def assert_equal_keys(d1, d2, *keys):
    for k in keys:
        assert d1[k] == d2[k]
    return True


def assert_inequal_keys(d1, d2, *keys):
    for k in keys:
        assert d1[k] != d2[k]
    return True


class TestFixtureException(Exception):
    pass


def jsonify_req(data):
    return dict(data=json.dumps(data, cls=DateTimeEncoder),
                content_type='application/json')

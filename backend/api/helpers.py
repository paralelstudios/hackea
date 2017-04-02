# -*- coding: utf-8 -*-

from functools import wraps
from jsonschema import ValidationError, validate
from . import exceptions
from flask import request, abort

def handle_http_error(err):
    """Returns an HTTP response object based on the specified error. If the error is a
    standard/default Flask/Werkzeug error, an equivalent is looked up in order to return a JSON
    formatted response.
    :param err: the error to evaluate
    """
    if not isinstance(err, exceptions.JSONException):
        if isinstance(err, AssertionError):
            return exceptions.InvalidParameters(errors=[err.message]).get_response()
        err = exceptions.default_exceptions[err.code]()
    return err.get_response()


ACCEPTABLE = set([
    'application/json',
    'application/hal+json',
    'application/vnd.error+json'
])


def request_accepts_json():
    accepts = False
    for content_type in ACCEPTABLE:
        if content_type in request.accept_mimetypes:
            accepts = True

    if not accepts:
        raise exceptions.NotAcceptable()

def get_uri():
    path = request.path
    qs = request.query_string
    if qs:
        return '?'.join([path, qs])
    return path



def not_found(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        result = view(*args, **kwargs)
        if result is None:
            abort(404)
        else:
            return result
    return wrapper

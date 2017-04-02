# -*- coding: utf-8 -*-
"""
    api.exceptions
    ~~~~~~~~~~~~~~~~~~~~

    API exceptions
"""
from collections import OrderedDict

from flask import json, make_response
from werkzeug import exceptions as e

__all__ = ['JSONException']


class JSONException(e.HTTPException):
    """A custom :class:`werkzeug.exceptions.HTTPException` implementation tailored for
    creating `application/vnd.error+json` responses.

    :param links: optional set of links to add to the response.
    :param errors: optional set of errors to add to the response.
    """

    def __init__(self, links=None, errors=None, *args, **kwargs):
        super(JSONException, self).__init__(*args, **kwargs)
        self.links = links
        self.errors = errors

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/vnd.error+json')]

    def get_body(self, environ=None):
        result = OrderedDict()
        if self.links:
            result['_links'] = {name: {'href': href} for name, href in self.links}
        result['message'] = self.description
        if self.errors:
            result['total'] = len(self.errors)
            result['_embedded'] = {'errors': self.errors}
        return result

    def get_response(self, environ=None):
        result = json.dumps(self.get_body(environ), indent=2)
        return make_response(result, self.code, self.get_headers(environ))


class BadRequest(JSONException, e.BadRequest):
    description = 'The browser/client sent a request that this server could not understand.'


class InvalidParameters(BadRequest):
    description = 'The request supplied invalid parameters.'


class NotAcceptable(JSONException, e.NotAcceptable):
    description = (
        'The resource identified by the request is only capable of generating response entities '
        'which have content characteristics not acceptable according to the accept headers sent '
        'in the request.'
    )


class NotFound(JSONException, e.NotFound):
    description = (
        'The requested URL was not found on the server. If you entered the URL manually please '
        'check your spelling and try again.'
    )


class MethodNotAllowed(JSONException, e.MethodNotAllowed):
    description = 'The method is not allowed for the requested URL.'


class InternalServerError(JSONException, e.InternalServerError):
    description = (
        'An internal server error occurred. '
        'Please file a bug report with the full URL of the request'
    )


class ServiceUnavailable(JSONException, e.ServiceUnavailable):
    description = (
        'The server is temporarily unable to service your request due to maintenance downtime or '
        'capacity problems.  Please try again later.'
    )


_exceptions = (
    BadRequest, InvalidParameters, NotAcceptable, NotFound, MethodNotAllowed,
    InternalServerError, ServiceUnavailable
)

default_exceptions = {}
for exception in _exceptions:
    default_exceptions[exception.code] = exception

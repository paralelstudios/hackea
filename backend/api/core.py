# -*- coding: utf-8 -*-
"""
    api.core
    ~~~~~~~~~~~~~~~~
    API core
"""

from hackea.core import factory, db
from hackea.models import User
import flask_restful as restful
from .exceptions import default_exceptions, ServiceUnavailable
from sqlalchemy.exc import OperationalError


class RestfulAPI(restful.Api):
    def handle_error(self, exception):
        """handle api exceptions in as HALly a way as possible"""
        if hasattr(exception, 'code'):
            # it's a wekzeug error
            return handle_http_error(exception)
        else:
            # else log and 500
            current_app.logger.exception(exception)
            errors = None
            if current_app.debug:
                errors = [traceback.format_exc()]
            exception = exceptions.InternalServerError(error=errors)

            return handle_http_error(exception)


class HackeaAPI(object):
    """An API class that registers Users and Organizations"""
    prefix = 'api'
    _ping_uri = '/_ping'

    def __init__(self, app=None):
        self.app = None
        self._restful_api = RestfulAPI(app, prefix="/%s" % self.prefix)
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self._restful_api.init_app(app)

        if 'ping' not in self.app.view_functions:
            self.app.add_url_rule(self._ping_uri, 'ping', self.ping)

    def _test_db(self):
        try:
            list(User.query.limit(1))
            return True
        except OperationalError:
            db.session.rollback()
        return False

    def register_resources(self, *resources):
        for resource in resources:
            self._restful_api.add_resource(resource, resource.uri)

    def ping(self):
        """Called to ensure the API is available."""
        if self._test_db():
            return 'OK'
        else:
            raise ServiceUnavailable

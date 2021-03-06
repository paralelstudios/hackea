# -*- coding: utf-8 -*-

from . import factory


def create_app(**kwargs):
    kwargs.setdefault('settings_module', 'api.settings')
    return factory.create_app(__name__, **kwargs)

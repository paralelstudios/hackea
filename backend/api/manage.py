# -*- coding: utf-8 -*-
"""
    api.manage
    ~~~~~~~~~~~~~~~~
    api's manage.py
"""

from flask_script import Manager

from api import create_app

app = create_app()
manager = Manager(app)

if __name__ == '__main__':
    manager.run()

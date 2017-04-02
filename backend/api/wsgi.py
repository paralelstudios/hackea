#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    api.main
    ~~~~~~~~~~~~~~
    api WSGI main entry point
"""
from api import create_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)

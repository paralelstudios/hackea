# -*- coding: utf-8 -*-

from flask_script import Manager

from hackea.core.factory import create_app

app = create_app(__name__)
manager = Manager(app)

if __name__ == '__main__':
    manager.run()

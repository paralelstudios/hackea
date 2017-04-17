# -*- coding: utf-8 -*-

from flask_script import Manager
from commands.ingest_orgs import IngestOrgs
from aidex.core.factory import create_app

app = create_app(__name__)
manager = Manager(app)
manager.add_command('ingest_orgs', IngestOrgs)
if __name__ == '__main__':
    manager.run()

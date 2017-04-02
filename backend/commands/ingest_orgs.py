# -*- coding: utf-8 -*-
from uuid import uuid4
from hackea.core import db
from hackea.models import Org
from flask_script import Command, Option
import csv
from unidecode import unidecode

class IngestOrgs(Command):
    """From a CSV ingest some orgs"""

    option_list = (
        Option('--filename', '-f', dest='filename', help='an csv file path'),
        Option('--cols', '-c', nargs='+', dest='columns',
                   default=['timestamp', 'name', 'mission', 'location',
                                 'phone', 'email', 'fb', 'registered', 'desires', 'services',
                                 'candidates', 'fiveoone']))
    def _create_org(self, row):
        boolean_keys = {'registered', 'fiveoone'}
        new_org = {}
        for key, v in row.items():
            if key in boolean_keys:
                new_org[key] = True if ('s' in row[key] or 'y' in row[key]) else False
            else:
                new_org[key] = unidecode(v)
        return Org(id=str(uuid4()), **new_org)

    def run(self, filename, columns):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, columns)
            orgs = [self._create_org(row) for row in reader if not list(Org.query.filter_by(name=row['name']))]

        db.session.add_all(orgs)
        db.session.commit()

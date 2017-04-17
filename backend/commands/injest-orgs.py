# -*- coding: utf-8 -*-
from aidex.models import Org
from flask_script import Command, Option
import csv

class IngestOrgs(Command):
    """From a CSV ingest some orgs"""

    option_list(
        Option('--filename', '-f', dest='filename', help='an csv file path'),
        Option('--cols', '-c', nargs='+', dest='columns',
                    default=['timestamp', 'name', 'mission', ' location',
                                 'phone', 'email', 'registered', 'services',
                                 'candidates', 'fiveoone']))


    def run(self, filename, columns):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, columns)
            for row in reader:
                print(row['name'])

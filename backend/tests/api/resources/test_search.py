# -*- coding: utf-8 -*-
"""
    tests.api.resources.test_search
    ~~~~~~~~~~~~~~~~
    tests Search API resources
"""
import os
import csv
import pytest
from toolz import dissoc
from flask import current_app
from aidex.helpers import uuid4, create_location
from api.helpers import clean_and_split
from unidecode import unidecode
from aidex.models import Org
from ...helpers import jsonify_req


@pytest.fixture()
def orgs_sample(session):
    def _create_org(row):
        boolean_keys = {'registered', 'fiveoone'}
        array_keys = {'services', 'categories'}
        location_key = 'cities'
        new_org = {}
        locations = []
        for key, v in row.items():
            if key in boolean_keys:
                new_org[key] = True if ('s' in row[key] or 'y' in row[key]) else False
            elif key in array_keys:
                new_org[key] = clean_and_split(row[key])
            elif key == location_key:
                locations += [create_location(dict(city=city))
                              for city in clean_and_split(row[key])]
            else:
                new_org[key] = unidecode(v)
        org_model = Org(id=str(uuid4()),
                        **dissoc(new_org,
                                 "desires", "fb", "registered",
                                 "candidates", "cities"))
        org_model.locations = locations
        session.add(org_model)
        session.commit()

    columns = ['timestamp', 'name', 'mission', 'cities',
               'phone', 'email', 'fb', 'registered', 'desires', 'services',
               'candidates', 'fiveoone', 'categories']
    path = os.path.join(current_app.config["BASE_DIR"], "tests/data/org-sample.csv")
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, columns)
        orgs = [
            _create_org(row)
            for row in reader
            if not Org.query.filter_by(name=unidecode(row['name'])).first()]
    print("ingested {} orgs for sample set".format(len(orgs)))


@pytest.mark.functional
def test_search_get(client, orgs_sample, auth_key):
    categories = ["jóvenes", "educación"]
    cities = ["San Juan", "Guaynabo"]
    keywords = ["tutorías", "talleres"]
    full_search = jsonify_req(dict(keywords=keywords,
                                   cities=cities,
                                   categories=categories))
    resp = client.get('/search', headers=auth_key, **full_search)
    assert "count" and "matches" in resp.json
    assert resp.json["count"] == 3
    assert set(
        x["name"] for x in resp.json["matches"]
    ) == {
        'Caras con causa', 'Jovenes de PR en Riesgo',
        'Sociedad Americana contra el cancer de Puerto Rico'}
    assert not {"locations", "name", "phone", "categories", "mission"} \
        - set(resp.json['matches'][0].keys())

    # test auth
    resp = client.get('/search', **full_search)
    assert resp.status_code == 401

    # test pagination
    full_search = jsonify_req(dict(categories=["educación"]))
    resp = client.get('/search', headers=auth_key, **full_search)
    assert resp.json["count"] == 5
    full_search = jsonify_req(dict(categories=["educación"],
                                   limit=2))
    resp = client.get('/search', headers=auth_key, **full_search)
    assert "count" and "matches" in resp.json
    assert resp.json["count"] == 2
    match1 = resp.json["matches"]
    full_search = jsonify_req(dict(categories=["educación"],
                                   limit=2,
                                   page=2))
    resp = client.get('/search', headers=auth_key, **full_search)
    assert "count" and "matches" in resp.json
    assert resp.json["count"] == 2
    match2 = resp.json["matches"]
    full_search = jsonify_req(dict(categories=["educación"],
                                   limit=2,
                                   page=3))
    resp = client.get('/search', headers=auth_key, **full_search)
    assert "count" and "matches" in resp.json
    assert resp.json["count"] == 1
    match3 = resp.json["matches"]
    assert match1 != match2 != match3

# -*- coding: utf-8 -*-
"""
    tests.api.resources.test_search
    ~~~~~~~~~~~~~~~~
    tests Search API resources
"""
import pytest
from ...helpers import jsonify_req, make_query_string


@pytest.mark.functional
def test_search_get(client, orgs_sample, auth_key):
    categories = ["jóvenes", "educación"]
    cities = ["San Juan", "Guaynabo"]
    keywords = ["tutorías", "talleres"]
    full_search = make_query_string(dict(keywords=keywords,
                                         cities=cities,
                                         categories=categories))
    resp = client.get('/search?{}'.format(full_search), headers=auth_key)
    assert "count" in resp.json and "matches" in resp.json and "page" in resp.json
    assert resp.json["count"] == 3
    assert resp.json["page"] == 1
    assert set(
        x["name"] for x in resp.json["matches"]
    ) == {
        'Caras con causa', 'Jovenes de PR en Riesgo',
        'Sociedad Americana contra el cancer de Puerto Rico'}
    assert not {"locations", "name", "phone", "categories", "mission"} \
        - set(resp.json['matches'][0].keys())

    # test auth
    resp = client.get('/search?{}'.format(full_search))
    assert resp.status_code == 401

    # test pagination
    full_search = make_query_string(dict(categories=["educación"]))
    resp = client.get('/search?{}'.format(full_search), headers=auth_key)
    assert resp.json["count"] == 5
    full_search = make_query_string(dict(categories=["educación"],
                                         limit=2))
    resp = client.get('/search?{}'.format(full_search), headers=auth_key)
    assert resp.json["count"] == 2
    assert resp.json["page"] == 1
    match1 = resp.json["matches"]
    full_search = make_query_string(dict(categories=["educación"],
                                         limit=2,
                                         page=2))
    resp = client.get('/search?{}'.format(full_search), headers=auth_key)
    assert resp.json["page"] == 2
    assert resp.json["count"] == 2
    match2 = resp.json["matches"]
    full_search = make_query_string(dict(categories=["educación"],
                                         limit=2,
                                         page=3))
    resp = client.get('/search?{}'.format(full_search), headers=auth_key)
    assert resp.json["count"] == 1
    assert resp.json["page"] == 3
    match3 = resp.json["matches"]
    assert match1 != match2 != match3

    # test no criteria
    resp = client.get('/search', headers=auth_key)
    assert resp.status_code == 400


@pytest.mark.integration
def test_full_search(client, auth_key):
    data = make_query_string({
        "page": 1,
        "limit": 5,
        "keywords": ["fa"],
        "categories": ["Educación"],
        "cities": ["Aguada"],
        "country": "pr"
    })
    resp = client.get(
        "/search?{}".format(data), headers=auth_key)
    assert not resp.json["count"]

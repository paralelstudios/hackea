# -*- coding: utf-8 -*-
"""
    tests.api.resources.test_users
    ~~~~~~~~~~~~~~~~
    Tests Users API resources
"""
from toolz import dissoc
import pytest
from aidex.models import User
from ...helpers import jsonify_req, assert_equal_keys, make_query_string


@pytest.mark.functional
def test_user_post(client, session, user_data):
    data = jsonify_req(user_data)
    resp = client.post('/users', **data)
    assert resp.status_code == 201
    assert "user_id" in resp.json
    user_id = resp.json["user_id"]
    user = User.query.get(user_id)
    assert user
    assert assert_equal_keys(user_data, user.as_dict(),
                             *dissoc(user_data, "password").keys())

    # test duplicate post
    resp = client.post('/users', **data)
    assert resp.status_code == 409

    # test post without reqs
    resp = client.post('/users', **jsonify_req(dict(email="foff@foff.gmail.com")))
    assert resp.json == {'message': "/users: 'name' is a required property"}


@pytest.mark.functional
def test_organized_orgs_get(client, session, ingested_user, ingested_org, auth_key):
    ingested_user.orgs.append(ingested_org)
    session.commit()
    data = make_query_string(dict(user_id=ingested_user.id))
    resp = client.get("/organized/orgs?{}".format(data), headers=auth_key)
    assert ingested_org.id == resp.json["orgs"][0]["id"]

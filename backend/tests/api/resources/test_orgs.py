# -*- coding: utf-8 -*-
"""
    tests.api.resources.test_orgs
    ~~~~~~~~~~~~~~~~
    Tests Orgs API resources
"""
from toolz import merge, dissoc
import pytest
from dateparser import parse as dateparse
from aidex.models import Org
from aidex.helpers import create_user
from ...helpers import jsonify_req, assert_equal_keys


@pytest.mark.functional
def test_org_post(client, ingested_user, org_data, location_data, auth_key):
    data = jsonify_req(merge(org_data, dict(location=location_data, user_id=ingested_user.id)))
    resp = client.post('/orgs', headers=auth_key, **data)
    assert resp.status_code == 201
    assert "org_id" in resp.json and "user_id" in resp.json
    org_id = resp.json["org_id"]
    org = Org.query.get(org_id)
    assert ingested_user in org.organizers
    assert assert_equal_keys(org_data, org.as_dict(), *org_data.keys())

    # test dup
    resp = client.post('orgs', headers=auth_key, **data)
    assert resp.status_code == 409

    # test auth
    resp = client.post('orgs', **data)
    assert resp.status_code == 401


@pytest.mark.functional
def test_org_put(client, session, ingested_org, ingested_user, auth_key, user_data):
    original_fiveoone = ingested_org.fiveoone
    data = jsonify_req(dict(user_id=ingested_user.id,
                            org_id=ingested_org.id,
                            fiveoone=not original_fiveoone))
    resp = client.put('/orgs', headers=auth_key, **data)
    assert "org_id" in resp.json and "user_id" in resp.json
    org = Org.query.get(resp.json["org_id"])
    assert org.fiveoone != original_fiveoone

    # test with unauthed user
    user = create_user(merge(user_data, dict(email="notthatusers@email.com")))
    session.add(user)
    session.commit()
    data = jsonify_req(dict(user_id=user.id,
                            org_id=ingested_org.id,
                            fiveoone=not original_fiveoone))
    resp = client.put('/orgs', headers=auth_key, **data)
    assert resp.status_code == 403


@pytest.mark.functional
def test_org_get(client, ingested_org, auth_key):
    data = jsonify_req(dict(org_id=ingested_org.id))
    resp = client.get('/orgs', headers=auth_key, **data)
    assert_equal_keys(ingested_org.as_dict(), resp.json,
                      *dissoc(ingested_org.as_dict(), "timestamp").keys())
    assert ingested_org.timestamp == dateparse(resp.json["timestamp"])

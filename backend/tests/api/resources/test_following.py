# -*- coding: utf-8 -*-
"""
    api.resources.test_following
    ~~~~~~~~~~~~~~~~
    Tests for Following API resources
"""
import pytest
from ...helpers import jsonify_req


@pytest.mark.functional
def test_follow_post(client, ingested_user, ingested_org, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, org_id=ingested_org.id))
    resp = client.post('/follow', headers=auth_key, **data)
    assert "user_id" in resp.json and "org_id" in resp.json
    assert ingested_org in ingested_user.following

    # test dub
    resp = client.post('/follow', headers=auth_key, **data)
    assert resp.status_code == 409

    # test auth
    resp = client.post('/follow', **data)
    assert resp.status_code == 401


@pytest.mark.functional
def test_unfollow_post(client, ingested_user, ingested_org, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, org_id=ingested_org.id))
    client.post('/follow', headers=auth_key, **data)
    resp = client.post('/unfollow', headers=auth_key, **data)
    assert "user_id" in resp.json and "org_id" in resp.json
    assert ingested_org not in ingested_user.following

    # test not following/dup
    resp = client.post('/unfollow', headers=auth_key, **data)
    assert resp.status_code == 409

    # test auth
    resp = client.post('/unfollow', **data)
    assert resp.status_code == 401

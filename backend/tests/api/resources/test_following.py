# -*- coding: utf-8 -*-
"""
    api.resources.test_following
    ~~~~~~~~~~~~~~~~
    Tests for Following API resources
"""
import pytest
from toolz import dissoc
from ...helpers import jsonify_req, make_query_string


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
def test_following_get(client, ingested_user, ingested_org, auth_key):
    query = make_query_string(dict(user_id=ingested_user.id, org_id=ingested_org.id))
    data = jsonify_req(dict(user_id=ingested_user.id, org_id=ingested_org.id))
    resp = client.post('/follow', headers=auth_key, **data)
    resp = client.get('/following?{}'.format(query), headers=auth_key)
    assert "user_id" in resp.json and "count" in resp.json and "followed_orgs" in resp.json
    assert resp.json["count"]
    assert dissoc(
        ingested_org.as_dict(), "timestamp", "locations", "established") in [
            dissoc(x, "timestamp", "locations", "established")
            for x in resp.json["followed_orgs"]]

    # test auth
    resp = client.get('/following?{}'.format(query))
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


@pytest.mark.functional
def test_followers_get(client, ingested_user, ingested_org, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, org_id=ingested_org.id))
    query = make_query_string(dict(user_id=ingested_user.id, org_id=ingested_org.id))
    resp = client.post('/follow', headers=auth_key, **data)
    resp = client.get('/followers?{}'.format(query), headers=auth_key)
    assert "org_id" in resp.json and "count" in resp.json and "followers" in resp.json
    assert resp.json["count"]
    assert ingested_user.id == resp.json["followers"][0]["id"]

    # test auth
    resp = client.get('/followers?{}'.format(query))
    assert resp.status_code == 401

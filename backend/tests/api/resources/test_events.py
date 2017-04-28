# -*- coding: utf-8 -*-
"""
    tests.api.resources.test_events
    ~~~~~~~~~~~~~~~~
    Tests Event API resources
"""
import pytest
from toolz import merge, dissoc
from datetime import timedelta
from aidex.models import Event, EventAttendance
from aidex.helpers import create_user, create_org
from ...helpers import jsonify_req, assert_equal_keys


@pytest.mark.functional
def test_event_post(client, event_data, location_data,
                    ingested_org, ingested_user, auth_key, user_data, session):
    data = jsonify_req(merge(event_data,
                             dict(location=location_data,
                                  user_id=ingested_user.id,
                                  org_id=ingested_org.id)))
    resp = client.post('/events', headers=auth_key, **data)
    assert resp.status_code == 201
    assert "event_id" in resp.json
    event = Event.query.get(resp.json["event_id"])
    assert event in ingested_org.events
    assert event.org == ingested_org

    # test dup
    resp = client.post('/events', headers=auth_key, **data)
    assert resp.status_code == 409

    # test auth
    resp = client.post('/events', **data)
    assert resp.status_code == 401

    # test with unauthed user
    user = create_user(merge(user_data, dict(email="notthatusers@email.com")))
    session.add(user)
    session.commit()
    data = jsonify_req(merge(event_data,
                             dict(user_id=user.id,
                                  org_id=ingested_org.id,
                                  location=location_data)))
    resp = client.post('/events', headers=auth_key, **data)
    assert resp.status_code == 403


@pytest.mark.functional
def test_event_put(client, ingested_event, ingested_org, ingested_user, auth_key,
                   session, org_data, location):
    original_start_date = ingested_event.start_date
    data = jsonify_req(dict(user_id=ingested_user.id,
                            org_id=ingested_org.id,
                            event_id=ingested_event.id,
                            start_date=original_start_date - timedelta(1)))
    resp = client.put("/events", headers=auth_key, **data)
    assert "event_id" in resp.json
    event = Event.query.get(resp.json["event_id"])
    assert event.start_date != original_start_date

    # test with un authed org
    org = create_org(org_data, location)
    session.add(org)
    session.commit()
    data = jsonify_req(dict(user_id=ingested_user.id,
                            org_id=org.id,
                            event_id=ingested_event.id))
    resp = client.put("/events", headers=auth_key, **data)
    assert resp.status_code == 403


@pytest.mark.functional
def test_event_get(client, ingested_event, auth_key):
    data = jsonify_req(dict(event_id=ingested_event.id))
    resp = client.get('/events', headers=auth_key, **data)
    assert_equal_keys(ingested_event.as_dict(), resp.json,
                      *dissoc(ingested_event.as_dict(),
                              "start_date", "end_date", "timestamp").keys())


@pytest.mark.functional
def test_event_attend(client, ingested_event, ingested_user, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, event_id=ingested_event.id))
    resp = client.post("/attend", headers=auth_key, **data)
    assert "user_id" in resp.json and "event_id" in resp.json
    event_attendance = EventAttendance.query.get(
        (resp.json["user_id"], resp.json["event_id"]))
    assert event_attendance
    assert ingested_event in ingested_user.events
    assert ingested_user in ingested_event.attendees

    # test auth
    resp = client.post("/attend", **data)
    assert resp.status_code == 401

    # test dup
    resp = client.post("/attend", headers=auth_key, **data)
    assert resp.status_code == 409


@pytest.mark.functional
def test_event_unattend(ingested_attendance, ingested_user,
                        ingested_event, client, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, event_id=ingested_event.id))
    resp = client.post("/unattend", headers=auth_key, **data)
    assert "user_id" in resp.json and "event_id" in resp.json
    event_attendance = EventAttendance.query.get(
        (resp.json["user_id"], resp.json["event_id"]))
    assert not event_attendance

    # test auth
    resp = client.post("/unattend", **data)
    assert resp.status_code == 401

    # test dup
    resp = client.post("/unattend", headers=auth_key, **data)
    assert resp.status_code == 409


@pytest.mark.functional
def test_event_volunteer(ingested_attendance, ingested_user,
                         ingested_event, client, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, event_id=ingested_event.id))
    resp = client.post("/volunteer", headers=auth_key, **data)
    assert "user_id" in resp.json and "event_id" in resp.json
    event_attendance = EventAttendance.query.get(
        (resp.json["user_id"], resp.json["event_id"]))
    assert event_attendance.as_volunteer

    # test auth
    resp = client.post("/volunteer", **data)
    assert resp.status_code == 401

    # test dup
    resp = client.post("/volunteer", headers=auth_key, **data)
    assert resp.status_code == 409


@pytest.mark.functional
def test_event_unvolunteer(ingested_volunteer_attendance, ingested_user,
                           ingested_event, client, auth_key):
    data = jsonify_req(dict(user_id=ingested_user.id, event_id=ingested_event.id))
    resp = client.post("/unvolunteer", headers=auth_key, **data)
    assert "user_id" in resp.json and "event_id" in resp.json
    event_attendance = EventAttendance.query.get(
        (resp.json["user_id"], resp.json["event_id"]))
    assert not event_attendance.as_volunteer

    # test auth
    resp = client.post("/unvolunteer", **data)
    assert resp.status_code == 401

    # test dup
    resp = client.post("/unvolunteer", headers=auth_key, **data)
    assert resp.status_code == 409


@pytest.mark.functional
def test_volunteers_get(client, auth_key,
                        ingested_event, ingested_user, ingested_org,
                        ingested_volunteer_attendance):
    data = jsonify_req(dict(org_id=ingested_org.id,
                            user_id=ingested_user.id, event_id=ingested_event.id))
    resp = client.get('/volunteers', headers=auth_key, **data)
    assert "event_id" in resp.json and "volunteers" in resp.json
    assert ingested_user.id == resp.json["volunteers"][0]["id"]

    # test auth
    resp = client.get('/volunteers', **data)
    assert resp.status_code == 401

    # test no volunteers
    volunteer_data = jsonify_req(dict(user_id=ingested_user.id,
                                      event_id=ingested_event.id))
    client.post("/unvolunteer", headers=auth_key, **volunteer_data)
    resp = client.get('/volunteers', headers=auth_key, **data)
    assert "event_id" in resp.json and "volunteers" in resp.json
    assert not resp.json["volunteers"]


@pytest.mark.functional
def test_attendees_get(client, auth_key,
                       ingested_event, ingested_user, ingested_org,
                       ingested_attendance):
    data = jsonify_req(dict(org_id=ingested_org.id,
                            user_id=ingested_user.id, event_id=ingested_event.id))
    resp = client.get('/attendees', headers=auth_key, **data)
    assert "event_id" in resp.json and "attendees" in resp.json
    assert ingested_user.id == resp.json["attendees"][0]["id"]

    # test auth
    resp = client.get('/attendees', **data)
    assert resp.status_code == 401

    # test no attendees
    attendee_data = jsonify_req(dict(user_id=ingested_user.id,
                                     event_id=ingested_event.id))
    client.post("/unattend", headers=auth_key, **attendee_data)
    resp = client.get('/attendees', headers=auth_key, **data)
    assert "event_id" in resp.json and "attendees" in resp.json
    assert not resp.json["attendees"]


@pytest.mark.functional
def test_volunteer_review_post(client, auth_key,
                               ingested_old_event, ingested_user, ingested_org,
                               ingested_old_volunteer_attendance):
    review = "great"
    data = jsonify_req(dict(org_id=ingested_org.id,
                            user_id=ingested_user.id,
                            event_id=ingested_old_event.id,
                            review=review))
    resp = client.post('/reviews', headers=auth_key, **data)
    assert "user_id" in resp.json and "event_id" in resp.json and "review" in resp.json

    # test auth
    resp = client.get('/reviews', **data)
    assert resp.status_code == 401

    # test dup
    resp = client.post('/reviews', headers=auth_key, **data)
    assert resp.status_code == 409


@pytest.mark.functional
def test_volunteer_review_get(client, auth_key,
                              ingested_old_event, ingested_user, ingested_org,
                              ingested_old_volunteer_attendance):
    review = "great"
    data = jsonify_req(dict(org_id=ingested_org.id,
                            user_id=ingested_user.id,
                            event_id=ingested_old_event.id,
                            review=review))
    client.post('/reviews', headers=auth_key, **data)
    data = jsonify_req(dict(org_id=ingested_org.id,
                            user_id=ingested_user.id))
    resp = client.get('/reviews', headers=auth_key, **data)
    assert "user_id" in resp.json and "reviews" in resp.json
    assert resp.json["reviews"][0] == review

    # test auth
    resp = client.get('/reviews', **data)
    assert resp.status_code == 401

    # test without org
    data = jsonify_req(dict(user_id=ingested_user.id))
    resp = client.get('/reviews', headers=auth_key, **data)
    assert resp


@pytest.mark.functional
def test_attendances_get(client, auth_key,
                         ingested_old_event, ingested_user, ingested_org,
                         ingested_old_volunteer_attendance,
                         ingested_event, ingested_attendance):
    # test all
    data = jsonify_req(dict(user_id=ingested_user.id))
    resp = client.get("/attendances", headers=auth_key, **data)
    assert "user_id" in resp.json and "attendances" in resp.json
    assert {ingested_event.id, ingested_old_event.id} == \
        {x["id"] for x in resp.json["attendances"]}

    # test active
    data = jsonify_req(dict(user_id=ingested_user.id,
                            active=True))
    resp = client.get("/attendances", headers=auth_key, **data)
    assert "user_id" in resp.json and "attendances" in resp.json
    assert {ingested_event.id} == \
        {x["id"] for x in resp.json["attendances"]}

    # test auth
    resp = client.get('/attendances', **data)
    assert resp.status_code == 401

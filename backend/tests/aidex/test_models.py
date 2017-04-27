# -*- coding: utf-8 -*-
"""
    test aidex models
    ~~~~~~
"""
import pytest
from datetime import datetime
from ..helpers import (
    validate_uuid, assert_equal_keys)
from aidex.models import (
    User, Org, Location, Event, EventAttendance)


@pytest.mark.unit
def test_user_model(user, user_data):
    assert assert_equal_keys(user.as_dict(), user_data, "email", "phone", "name")
    assert user.password != user_data["password"]
    assert user.verify_password(user_data["password"])
    assert validate_uuid(user.id)
    assert not (user.following or user.orgs or user.events or user.timestamp)


@pytest.mark.functional
def test_user_model_commit(user, session):
    session.add(user)
    session.commit()
    committed_user = User.query.get(user.id)
    assert assert_equal_keys(
        user.as_dict(), committed_user.as_dict(),
        "phone", "name", "_password")
    assert isinstance(committed_user.timestamp, datetime)


@pytest.mark.functional
def test_org_location_model_commit(org, session, location):
    org.locations.append(location)
    session.add(org)
    session.commit()
    committed_org = Org.query.get(org.id)
    committed_location = Location.query.get(location.id)
    assert assert_equal_keys(
        org.as_dict(), committed_org.as_dict(),
        "email", "phone", "services")
    assert validate_uuid(committed_org.id)
    assert isinstance(committed_org.timestamp, datetime)
    assert committed_location in org.locations


@pytest.mark.functional
def test_org_owner_relationship(org, user, session):
    org.organizers.append(user)
    session.add(org)
    session.commit()
    committed_user = User.query.get(user.id)
    committed_org = Org.query.get(org.id)
    assert org in committed_user.orgs
    assert user in committed_org.organizers


@pytest.mark.functional
def test_event_commit_and_org_relationship(org, event, location, session):
    org.events.append(event)
    session.add(org)
    session.add(event)
    session.commit()
    committed_event = Event.query.get(event.id)
    committed_org = Org.query.get(org.id)
    assert assert_equal_keys(event.as_dict(), committed_event.as_dict(),
                             "name", "org_id",
                             "start_date", "end_date")
    assert isinstance(committed_event.timestamp, datetime)
    assert committed_event.location == location
    assert committed_event in committed_org.events


@pytest.mark.functional
def tests_event_attendee_relationship(org, session,
                                      event, user, event_attendance):
    org.events.append(event)
    event.attendees.append(event_attendance)
    session.add(org)
    session.add(user)
    session.commit()
    committed_event = Event.query.get(event.id)
    committed_event_a = EventAttendance.query.get((user.id, event.id))
    committed_user = User.query.get(user.id)
    assert event_attendance in committed_event.attendees
    assert event_attendance in committed_user.events
    assert user == committed_event_a.attendee
    assert event == committed_event_a.event

    committed_event_a.query.delete()
    session.commit()
    assert event_attendance not in committed_event.attendees
    assert event_attendance not in committed_user.events

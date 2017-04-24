# -*- coding: utf-8 -*-
"""
    test aidex models
    ~~~~~~
"""
import pytest
from datetime import datetime, timedelta
from aidex.helpers import (
    create_user, create_org, create_location,
    create_event, create_event_attendance)
from ..helpers import (
    validate_uuid, assert_equal_keys)
from aidex.models import (
    User, Org, Location, Event, EventAttendance)


@pytest.fixture
def user_data():
    return dict(
        name="A test user",
        phone="567530909",
        password="password",
        email="test@user.com")


@pytest.fixture
def org_data():
    return dict(
        name="A test org",
        mission="to provide aidex with a dummy org",
        phone="567530909",
        email="test@test.org",
        services=["testing", "ease"],
    )


@pytest.fixture()
def location_data():
    return dict(
        address="AllStreetsAreFake 0",
        city="AllCitiesAreFake",
        country="AllCountriesAreFake")


@pytest.fixture()
def user(app, user_data):
    return create_user(user_data)


@pytest.fixture()
def location(app, location_data):
    return create_location(location_data)


@pytest.fixture()
def org(app, org_data, location):
    return create_org(org_data, location)


@pytest.fixture()
def event_data(org):
    return dict(
        name="FakeEvent",
        org_id=org.id,
        start_date=str(datetime.now()),
        end_date=str(datetime.now() + timedelta(1)))


@pytest.fixture()
def event_attendance_data(user, event):
    return dict(
        user_id=user.id,
        event_id=event.id)


@pytest.fixture()
def event_attendance(event_attendance_data, user):
    return create_event_attendance(event_attendance_data, user)


@pytest.fixture
def event(app, event_data, location):
    return create_event(event_data, location)


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
    session.add(location)
    session.add(org)
    session.commit()
    committed_org = Org.query.get(org.id)
    committed_location = Location.query.get(location.id)
    assert assert_equal_keys(
        org.as_dict(), committed_org.as_dict(),
        "email", "phone", "services", "location_id")
    assert validate_uuid(committed_org.id)
    assert isinstance(committed_org.timestamp, datetime)
    assert org.location == committed_location


@pytest.mark.functional
def test_org_owner_relationship(org, user, session):
    session.add(user)
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
    session.add(location)
    session.commit()
    committed_event = Event.query.get(event.id)
    committed_org = Org.query.get(org.id)
    assert assert_equal_keys(event.as_dict(), committed_event.as_dict(),
                             "name", "org_id",
                             "start_date", "end_date",
                             "location_id")
    assert isinstance(committed_event.timestamp, datetime)
    assert committed_event.location == location
    assert committed_event in committed_org.events


@pytest.mark.functional
def tests_event_attendee_relationship(org, session,
                                      event, user, event_attendance):
    org.events.append(event)
    event.attendees.append(event_attendance)
    session.add(event)
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

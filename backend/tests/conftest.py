# -*- coding: utf-8 -*-
"""
    general aidex test fixtures
    ~~~~~~
"""
import pytest
from datetime import datetime, timedelta
from aidex.helpers import (
    create_user, create_org, create_location,
    create_event, create_event_attendance)


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
def event_data(org):
    return dict(
        name="FakeEvent",
        start_date=str(datetime.now() + timedelta(1)),
        end_date=str(datetime.now() + timedelta(2)))


@pytest.fixture()
def old_event_data(org):
    return dict(
        name="FakeEvent",
        start_date=str(datetime.now() - timedelta(30)),
        end_date=str(datetime.now() - timedelta(29)))


@pytest.fixture()
def event_attendance_data(user, event):
    return dict(
        user_id=user.id,
        event_id=event.id)


@pytest.fixture()
def old_event_attendance_data(user, old_event):
    return dict(
        user_id=user.id,
        event_id=old_event.id)


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
def event_attendance(event_attendance_data, user):
    return create_event_attendance(event_attendance_data, user)


@pytest.fixture()
def old_event_attendance(old_event_attendance_data, user):
    return create_event_attendance(old_event_attendance_data, user)


@pytest.fixture
def event(app, event_data, location):
    return create_event(event_data, location)


@pytest.fixture
def old_event(app, old_event_data, location):
    return create_event(old_event_data, location)

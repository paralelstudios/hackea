# -*- coding: utf-8 -*-
"""
    aidex.helpers
    ~~~~~~~~~~~~~~~~
    helpers for working with aidex data
"""
from toolz import dissoc
from uuid import uuid4
from dateparser import parse as dateparse
from .models import (
    Org, Location, User, Event,
    EventAttendance)


def uuid():
    return str(uuid4())


def try_committing(connection_reference):
    """
    Pass a scoped session or connection (anything with commit and rollback methods)
    to this function, and it will try committing, with rollback on failure.
    """
    try:
        connection_reference.commit()
    except Exception as e:
        connection_reference.rollback()
        raise e


def check_existence(model, *conditions):
    if model.query.filter(*conditions).first():
        return True


def create_location(location, org_id=None, event_id=None):
    return Location(org_id=org_id, event_id=event_id,
                    **location)


def create_org(data, *new_locations):
    return Org(
        id=uuid(),
        locations=list(new_locations),
        **dissoc(data, "locations")
    )


def create_user(data=None):
    return User(
        id=uuid(),
        **data)


def create_event(data, new_location=None):
    return Event(
        id=uuid(),
        location=new_location,
        start_date=dateparse(data["start_date"]),
        end_date=dateparse(data["end_date"]),
        **dissoc(data, "start_date", "end_date", "location"))


def create_event_attendance(data, *attendees):
    ea = EventAttendance(**data)
    ea.attendees = attendees
    return ea

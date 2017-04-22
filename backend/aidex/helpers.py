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


def check_existence(model, pk=None, *conditions):
    if model.query.filter(*conditions).first():
        return True


def create_location(location):
    return Location(**location)


def create_org(data, new_location):
    return Org(
        id=uuid(),
        location=new_location,
        location_id=new_location.id,
        **dissoc(data, "location")
    )


def create_user(data):
    return User(
        id=uuid(),
        **data)


def create_event(data, new_location):
    return Event(
        id=uuid(),
        location=new_location,
        location_id=new_location.id,
        start_date=dateparse(data["start_date"]),
        end_date=dateparse(data["end_date"]),
        **dissoc(data, "start_date", "end_date", "location"))


def create_event_attendance(data, *attendees):
    ea = EventAttendance(**data)
    ea.attendees = attendees
    return ea

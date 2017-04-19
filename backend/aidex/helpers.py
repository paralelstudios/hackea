# -*- coding: utf-8 -*-
"""
    aidex.helpers
    ~~~~~~~~~~~~~~~~
    helpers for working with aidex data
"""
from toolz import dissoc
from uuid import uuid4
from dateparser import parse as dateparse
from datetime import datetime
from .models import Org, Location, User, Event


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
        timestamp=datetime.now(),
        **dissoc(data, "location")
    )


def create_user(data):
    return User(
        id=uuid(),
        timestamp=datetime.now(),
        **data)


def create_event(data, new_location):
    return Event(
        id=uuid(),
        timestamp=datetime.now(),
        location=new_location,
        location_id=new_location.id,
        start_date=dateparse(data["start_date"]),
        end_date=dateparse(data["end_date"]),
        **dissoc(data, "start_date", "end_date", "location"))

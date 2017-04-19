# -*- coding: utf-8 -*-
"""
    api.resources.event
    ~~~~~~~~~~~~~~~~
    Event API resources
"""
from flask_restful import abort
from flask import request
from toolz import valmap, dissoc, keyfilter
from unidecode import unidecode
from aidex.core import db
from aidex.helpers import (
    create_event, create_location, try_committing)
from aidex.models import Org, User, Event
from .base import JWTEndpoint
from ..helpers import get_entity, check_if_org_owner


class EventEndPoint(JWTEndpoint):
    uri = "/events"
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "org_id": {"type": "string"},
            "user_id": {"type": "string"},
            "event_id": {"type": "string"},
            "name": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
            "location": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                }
            }

        },
        "required": ["org_id", "location", "start_date", "end_date", "name", "user_id"]
    }

    def _clean_data(self, data):
        relevant_data = keyfilter(
            lambda key: key in self.schema["properties"], data)
        cleaned_data = valmap(
            unidecode, dissoc(relevant_data, "services", "location"))
        if "location" in data:
            relevant_loc_data = keyfilter(
                lambda key: key in self.schema["properties"]["location"]["properties"],
                data["location"])
            cleaned_data["location"] = valmap(
                unidecode,
                relevant_loc_data)
        return cleaned_data

    def post(self):
        self.validate_form(request.json)
        org = get_entity(Org, request.json["org_id"], update=True)
        user = get_entity(User, request.json["user_id"])
        if not org:
            abort(400, "Org {} does not exist".format(org.id))
        if not user:
            abort(400, "User {} does not exist".format(user.id))
        check_if_org_owner(user, org)
        cleaned_data = self._clean_data(request.json)
        location = create_location(cleaned_data["location"])
        new_event = create_event(cleaned_data)
        org.events.append(new_event)
        db.session.add(location)
        db.session.add(new_event)
        try_committing(db.session)

    def put(self):
        if not ("org_id" in request.json and
                "user_id" in request.json and
                "event_id" in request.json):
            abort(400, "org_id, user_id, and event_id needed to update events")
        org = get_entity(Org, request.json["org_id"], update=True)
        user = get_entity(User, request.json["user_id"])
        event = get_entity(Event, request.json["event_id"], update=True)
        check_if_org_owner(user, org)
        if event not in org.events:
            abort(403, "Event {} does not belong to Org {}".format(
                event.name, org.name))
        cleaned_data = self._clean_data(request.json)
        for key, value in dissoc(cleaned_data, "location").items():
            setattr(event, key, value)

        if "location" in cleaned_data:
            new_location = create_location(cleaned_data["location"])
            db.session.add(new_location)
            event.location = new_location
            event.location_id = new_location.id

    def get(self):
        if "event_id" not in request.json:
            abort(400, "event_id needed to get event")
        event = get_entity(Event, request["event_id"])
        return event.as_dict()


class EventAttendanceEndpoint(JWTEndpoint):
    schema = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "event_id": {"type": "string"}}}

    def _get_entites(user_id, event_id):
        return get_entity(User, user_id, update=True), \
            get_entity(Event, event_id, update=True)

    def _process_post(self, user, event):
        raise NotImplementedError

    def post(self):
        self.validate_form(request.json)
        self._process_post(
            get_entity(User, request.json["user_id"], update=True),
            get_entity(User, request.json["event_id"], update=True))


class AttendEventEndpoint(EventAttendanceEndpoint, JWTEndpoint):
    uri = "/attend"

    def _process_post(self, user, event):
            pass


class UnattendEventEndpoint(EventAttendanceEndpoint, JWTEndpoint):
    uri = "/unattend"

    def _process_post(self):
        pass


class VolunteerEventEndpoint(EventAttendanceEndpoint, JWTEndpoint):
    uri = "/volunteer"

    def _process_post(self):
        pass


class UnvolunteerEventEndpoint(VolunteerEventEndpoint):
    uri = "/unvolunteer"

    def _process_post(self):
        pass


ENDPOINTS = [EventEndPoint,
             AttendEventEndpoint,
             UnattendEventEndpoint,
             VolunteerEventEndpoint,
             UnvolunteerEventEndpoint]
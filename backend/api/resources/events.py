# -*- coding: utf-8 -*-
"""
    api.resources.event
    ~~~~~~~~~~~~~~~~
    Event API resources
"""
from flask_restful import abort
from flask import request, jsonify
from toolz import valmap, dissoc, keyfilter
from dateparser import parse as dateparse
from unidecode import unidecode
from aidex.core import db
from aidex.helpers import (
    create_event, create_location, try_committing,
    create_event_attendance, check_existence)
from aidex.models import (
    Org, User, Event, EventAttendance, Location)
from .base import JWTEndpoint
from ..helpers import (
    get_entity, check_if_org_owner,
    get_event, check_if_org_event,
    get_organizer_and_org)


class EventEndPoint(JWTEndpoint):
    uri = "/events"
    schema = {
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
            unidecode, dissoc(relevant_data, "services", "location", "user_id"))
        if "location" in data:
            relevant_loc_data = keyfilter(
                lambda key: key in self.schema["properties"]["location"]["properties"],
                data["location"])
            cleaned_data["location"] = valmap(
                unidecode,
                relevant_loc_data)
        return cleaned_data

    def _check_dates(self, start, end):
        if dateparse(start) > dateparse(end):
            abort(400,
                  description="Start date {} is after end date {}".format(
                      start, end))

    def post(self):
        self.validate_form(request.json)

        user, org = get_organizer_and_org(
            request.json["user_id"],
            request.json["org_id"],
            update_org=True)

        self._check_dates(request.json["start_date"], request.json["end_date"])

        if check_existence(Event,
                           Event.name == request.json["name"],
                           Event.org == org,
                           Location.city == request.json["location"]["city"],
                           Location.address == request.json["location"]["address"],
                           Location.country == request.json["location"]["country"],
                           Event.start_date == request.json["start_date"],
                           Event.end_date == request.json["end_date"]):
            abort(409,
                  description="Event {} already exists".format(request.json["name"]))
        cleaned_data = self._clean_data(request.json)
        new_event = create_event(cleaned_data)
        location = create_location(cleaned_data["location"])
        new_event.location = location
        org.events.append(new_event)

        try_committing(db.session)
        return {"event_id": new_event.id}, 201

    def _handle_date_update(self, event, data):
        if "start_date" and "end_date" in data:
            self._check_dates(data["start_date"], data["end_date"])
            return
        if "start_date" in data:
            self._check_dates(data["start_date"], event.end_date)
            return
        if "end_date" in data:
            self._check_dates(event.start_date, data["end_date"])
            return

    def put(self):
        if not ("org_id" in request.json and
                "user_id" in request.json and
                "event_id" in request.json):
            abort(400, "org_id, user_id, and event_id needed to update events")
        org = get_entity(Org, request.json["org_id"])
        user = get_entity(User, request.json["user_id"])
        event = get_entity(Event, request.json["event_id"],
                           update=True, lazyloaded="location")

        check_if_org_owner(user, org)
        if event not in org.events:
            abort(403, description="Event {} does not belong to Org {}".format(
                event.name, org.name))

        cleaned_data = self._clean_data(request.json)

        for key, value in dissoc(cleaned_data, "location").items():
            setattr(event, key, value)

        if "location" in cleaned_data:
            new_location = create_location(cleaned_data["location"])
            event.location = new_location
        try_committing(db.session)
        return {"event_id": event.id}, 200

    def get(self):
        if "event_id" not in request.json:
            abort(400, description="event_id needed to get event")
        event = get_entity(Event, request.json["event_id"])
        return jsonify(event)


class AttendEventBaseEndpoint(JWTEndpoint):
    uri = None
    _as_volunteer = False
    _to_attend = True
    schema = {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "event_id": {"type": "string"}}}

    def _get_entites(self, user_id, event_id):
        return get_entity(User, user_id, update=True), \
            get_entity(Event, event_id, update=True, lazyloaded="location")

    def _create_attendance(self, user, event, as_volunteer=False):
        return create_event_attendance(
            dict(user_id=user.id, event_id=event.id,
                 as_volunteer=as_volunteer), user)

    def post(self):
        self.validate_form(request.json)
        attendance = self._process_post(
            *self._get_entites(request.json["user_id"], request.json["event_id"]))
        return dict(user_id=attendance.user_id,
                    event_id=attendance.event_id,
                    volunteer=attendance.as_volunteer)

    def _process_post(self, user, event):
        attendance = EventAttendance.query \
                                    .with_for_update() \
                                    .get((user.id, event.id))
        error = None
        if self._to_attend and not attendance:
            attendance = self._create_attendance(user, event, self._as_volunteer)
            event.attendees.append(attendance)
            db.session.add(attendance)
        elif self._as_volunteer and attendance and self._to_attend and not attendance.as_volunteer:
            attendance.as_volunteer = True
        elif not self._as_volunteer and attendance and attendance.as_volunteer:
            attendance.as_volunteer = False
        elif not self._to_attend and attendance:
            attendance.query.delete()
        elif not self._as_volunteer and attendance and not attendance.as_volunteer and attendance and self._to_attend:
            error = "User {} is not volunteering at Event {}".format(
                      user.id, event.id)
        elif not self._as_volunteer and attendance and self._to_attend:
            error = "User {} is already attending Event {}".format(
                user.id, event.id)
        elif self._as_volunteer and attendance and attendance.as_volunteer:
            error = "User {} is already volunteering Event {}".format(
                user.id, event.id)
        elif not (self._as_volunteer or attendance or self._to_attend):
            error = """User {} not is attending or volunteering at Event {},
                  can't unattend""".format(user.id, event.id)
        elif not self._to_attend and not attendance:
            error = "User {} not is attending Event {}, can't unattend".format(
                user.id, event.id)
        else:
            error = "a flying duck"

        if error:
            abort(409, description=error)
        try_committing(db.session)
        return attendance


class AttendEventEndpoint(AttendEventBaseEndpoint):
    uri = "/attend"


class VolunteerEventEndpoint(AttendEventBaseEndpoint):
    uri = "/volunteer"
    _as_volunteer = True


class UnattendEventEndpoint(AttendEventBaseEndpoint):
    uri = "/unattend"
    _to_attend = False


class UnvolunteerEventEndpoint(VolunteerEventEndpoint):
    uri = "/unvolunteer"
    _as_volunteer = False


class GetAttendeesBase(JWTEndpoint):
    attendee_type = None
    schema = {
        "type": "object",
        "properties": {
            "org_id": {"type": "string"},
            "user_id": {"type": "string"},
            "event_id": {"type": "string"}
            },
        "required": ["org_id", "user_id", "event_id"]
    }

    def get(self):
        self.validate_form(request.json)
        user, org = get_organizer_and_org(request.json["user_id"],
                                          request.json["org_id"])
        event = get_event(request.json["event_id"])
        check_if_org_event(org, event)

        return jsonify({
            "event_id": request.json["event_id"],
            self.attendee_type: getattr(event, self.attendee_type)()})


class VolunteersEndPoint(GetAttendeesBase):
    uri = "/volunteers"
    attendee_type = "volunteer_users"


class AttendeesEndPoint(GetAttendeesBase):
    uri = "/attendees"
    attendee_type = "attendee_users"


ENDPOINTS = [EventEndPoint,
             AttendEventEndpoint,
             UnattendEventEndpoint,
             VolunteerEventEndpoint,
             UnvolunteerEventEndpoint,
             VolunteersEndPoint,
             AttendeesEndPoint]

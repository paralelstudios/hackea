# -*- coding: utf-8 -*-
"""
    api.helpers
    ~~~~~~~~~~~~~~~~
    API helpers
"""
from flask import make_response
from flask_restful import abort
from unidecode import unidecode
from sqlalchemy.orm import lazyload
from datetime import datetime
from twilio import twiml
import json
from toolz import curry
from aidex.core import db
from aidex.models import User, Org, Event


def twilio_send_not_found(message):
    response = twiml.Response()
    response.message(message)
    return str(response)


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


def clean_and_split(s):
    return [unidecode(x.strip().lower()) for x in s.split(',') if x]


class AIDEXJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, db.Model):
            return o.as_dict()
        return json.JSONEncoder.default(self, o)


def get_page_offset(page, limit):
    return (page * limit) - limit if page else page


def authenticate(email, password):
    u = User.query.filter_by(email=email).first()
    if u and u.verify_password(password):
        return u


def identity(payload):
    user_id = payload["identity"]
    return User.query.get(user_id)


def get_entity(model, pk, update=False, lazyloaded=None):
    q = model.query
    if lazyloaded:
        q = q.options(lazyload(lazyloaded))
    if update:
        q = q.with_for_update()

    entity = q.get(pk)
    if not entity:
        abort(400, description="{} {} doesn't exist".format(model.__name__, pk))
    return entity


def check_if_org_owner(user, org):
    if user not in org.organizers:
        abort(403, description="User {} is not an organizer of Org {}".format(
            user.email, org.name))


def check_if_org_event(org, event):
    if org != event.org:
        abort(403, description="Event {} does not belong to Org {}".format(
            event.id, org.id))


def clean_input(input):
    if isinstance(input, (str, bytes)):
        return unidecode(input)
    return input


get_user = curry(get_entity, User)
get_org = curry(get_entity, Org)
get_event = curry(get_entity, Event)


def safe_get_org(org_id, update=False):
    get_options = dict(lazyloaded="locations") if update else {}

    return get_org(org_id,
                   update=update,
                   **get_options)


def safe_get_event(event_id, update=False):
    get_options = dict(lazyloaded="location") if update else {}

    return get_event(event_id,
                     update=update,
                     **get_options)


def get_organizer_and_org(user_id, org_id,
                          update_user=False, update_org=False):
    user = get_user(user_id,
                    update=update_user)
    org = safe_get_org(org_id, update_org)
    check_if_org_owner(user, org)
    return user, org


def get_org_event(event_id, org_id=None,
                  update_event=False, update_org=False):
    event = safe_get_event(event_id, update_event)
    org = safe_get_org(org_id)
    check_if_org_event(org, event)
    return org, event

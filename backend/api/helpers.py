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
from aidex.core import db
from aidex.models import User


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
        abort(403, description="{} is not an organizer of {}, can't update".format(
            user.email, org.name))


def clean_input(input):
    if isinstance(input, (str, bytes)):
        return unidecode(input)
    return input

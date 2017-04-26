# -*- coding: utf-8 -*-
from flask import make_response
from flask_restful import abort
from unidecode import unidecode
from datetime import datetime
from twilio import twiml
import json
from aidex.models import User


def to_regex_or(*strs):
    """returns strs as an or regex, empty args will match anything!"""
    return ".*(" + "|".join(strs) + ").*"


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


def sms_org_format(org):
    return "{name} tel: {phone}".format(name=org.name, phone=org.phone)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def get_page_offset(page, limit):
    return (page * limit) - limit


def authenticate(email, password):
    u = User.query.filter_by(email=email).first()
    if u and u.verify_password(password):
        return u


def identity(payload):
    user_id = payload["identity"]
    return User.query.get(user_id)


def get_entity(model, pk, update=False):
    q = model.query
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

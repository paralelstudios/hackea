# -*- coding: utf-8 -*-

from jsonschema import ValidationError, validate
from flask import make_response
from unidecode import unidecode
from datetime import datetime
import json
from uuid import uuid4


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


def to_regex_or(*strs):
    """returns strs as an or regex, empty args will match anything!"""
    return ".*(" + "|".join(strs) + ").*"


def contains_keyword(col, kw):
    return func.lower(col).contains(kw)


def twilio_send_not_found(message):
    response = twiml.Response()
    response.message(message)
    return str(response)


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp

def validate_form(form, required, uri):
    provided = set(form)
    if required - provided:
        missing = required_fields - keys
        return {'message': '{} post missing {}, only got {}'
                        .format(uri, missing, provided)}, 400

def clean_and_split(s):
    return [unidecode(x.strip().lower()) for x in s.split(',') if x]

def sms_org_format(org):
    return "{name} tel: {phone}".format(name=org.name, phone=org.phone)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

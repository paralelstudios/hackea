# -*- coding: utf-8 -*-
"""
    api.resources
    ~~~~~~~~~~~~~~~~
    API resources
"""
from uuid import uuid4
from flask import Flask, request, current_app, make_response
from flask_restful import abort, Resource
from hackea.models import User, Org
from api.helpers import DateTimeEncoder
import json
from hackea.core import db
from twilio import twiml
from sqlalchemy import func, or_, and_
from unidecode import unidecode

class UsersEndpoint(Resource):
    uri = "/users"
    def post(self):
        data = request.form
        current_app.logger.info(data)
        if list(User.query.filter_by(email=data['email'])):
            # and if two ppl try to create acount at the same time hmmm??
            return {'message': 'User {} already exists'.format(data['email'])}, 400
        new_user = User(
            id=str(uuid4()),
            email=data['email'],
            name=unidecode(data['name']),
            phone=data['phone'])
        new_user.set_password(data['password'])
        current_app.logger.info("created {}".format(data['email']))
        db.session.add(new_user)
        db.session.commit()

        return {"success": True, "user_id": new_user.id}, 201


class OrgsEndpoint(Resource):
    uri = "/orgs"

    def get(self):
        orgs = [json.dumps(org.as_dict(), cls=DateTimeEncoder) for org in Org.query.all()]
        return {"count": len(orgs), "orgs": orgs}

    def post(self):
        name = request.form["name"]
        user_id = request.form["user_id"]
        user = User.query.get(user_id)
        if not user:
            return {"message": "User {} doesn't exist".format(user_id)}, 400
        if list(Org.query.filter_by(name=name)):
            return {"message": "Org {} already exists".format(name)}, 400

        new_org = Org(
            id=str(uuid4()),
            name=unidecode(name))
        new_org.organizers.append(user)
        db.session.add(new_org)
        db.session.commit()
        return {"success": True, "org_id": new_org.id, "user_id": user_id}, 201


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp

def clean_and_split(s):
    return [unidecode(x.strip().lower()) for x in s.split(',') if x]

class SMSOrgEndpoint(Resource):
    uri = '/sms/orgs'
    representations = {'application/xml': output_xml}
    def post(self):
        raw_query = (request.args.get('Body')
                     or request.form.get('Body'))
        if not raw_query:
            return _send_not_found('favor de formar su mensaje de acuerdo a "causa/municipio"')

        query = raw_query.split('/')
        current_app.logger.info(query)
        kw_conditions, mun_conditions = [], []
        key_words, municipios = None, None
        key_words = clean_and_split(query[0])

        # this is terrible forgive me
        def contains_keyword(col, kw):
            return func.lower(col).contains(kw)

        for kw in key_words:
            kw_conditions.append(contains_keyword(Org.name, kw))
            kw_conditions.append(contains_keyword(Org.services, kw))
            kw_conditions.append(contains_keyword(Org.mission, kw))
        if len(query) > 1:
            municipios = clean_and_split(query[1])
        if municipios:
            for m in municipios:
                mun_conditions.append(contains_keyword(Org.location, m))

        current_app.logger.info("got query {}".format(query))
        orgs = list(Org.query.filter(
            and_(
                or_(*kw_conditions),
                or_(*mun_conditions))))

        if not orgs:
            return _send_not_found("No encontramos nada :(")
        org_names = [org.name + " tel: " + org.phone for org in orgs]
        response = twiml.Response()
        message = ["Organizaciones bajo {}:".format(raw_query)]
        response.message(
            '\n'.join(message + set(org_names)))
        return str(response)


def _send_not_found(message):
    response = twiml.Response()
    response.message(message)
    return str(response)


__all__ = [UsersEndpoint, OrgsEndpoint, SMSOrgEndpoint]

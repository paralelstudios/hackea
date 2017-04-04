# -*- coding: utf-8 -*-
"""
    api.resources
    ~~~~~~~~~~~~~~~~
    API resources
"""
from flask import Flask, request, current_app, make_response
from twilio import twiml
from sqlalchemy import func, or_, and_
import json
from unidecode import unidecode
from flask_restful import abort, Resource
from hackea.models import User, Org
from api.helpers import (
    DateTimeEncoder, output_xml, twilio_send_not_found,
    uuid, try_committing, to_regex_or, sms_org_format,
    clean_and_split, validate_form)
from hackea.core import db


class UsersEndpoint(Resource):
    uri = "/users"
    def post(self):
        data = request.form
        # replace validation logic with jsonschema
        form_errs = validate_form(
            data, {'password', 'email', 'name', 'phone'}, self.uri)

        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User {} already exists'.format(data['email'])}, 400
        new_user = User(
            id=uuid(),
            email=data['email'],
            name=unidecode(data['name']),
            phone=data['phone'])

        new_user.set_password(data['password'])

        db.session.add(new_user)
        try_committing(db.session)

        return {"success": True, "user_id": new_user.id}, 201


class OrgsEndpoint(Resource):
    uri = "/orgs"

    def get(self):
        orgs = [
            org.as_dict()
            for org in Org.query.all()]
        return {"count": len(orgs),
                "orgs": json.dumps(orgs, cls=DateTimeEncoder)}

    def post(self):
        form_err = validate_form(
            request.form, {'name', 'user_id'}, self.uri)
        if form_err:
            return form_err

        name = request.form["name"]
        user_id = request.form["user_id"]
        user = User.query.get(user_id)

        if not user:
            return {"message": "User {} doesn't exist".format(user_id)}, 400

        if Org.query.filter_by(name=name).first():
            return {"message": "Org {} already exists".format(name)}, 400

        new_org = Org(
            id=uuid(),
            name=unidecode(name))

        new_org.organizers.append(user)

        db.session.add(new_org)
        try_committing(db.session)

        return {"success": True, "org_id": new_org.id, "user_id": user_id}, 201



class SMSOrgEndpoint(Resource):
    uri = '/sms/orgs'
    representations = {'application/xml': output_xml}

    def post(self):
        raw_query = (
            request.args.get('Body')
            or request.form.get('Body'))

        if not raw_query:
            return send_not_found(
                'favor de formar su mensaje de acuerdo a "causa/municipio"')

        query = raw_query.split('/')

        key_words = query[0]
        municipios = query[1] if len(query) > 1 else None
        kw_conditions, mun_conditions = [], []
        kw_regex = to_regex_or(*clean_and_split(query[0]))

        if key_words:
            kw_conditions += [
                Org.name.op('~*')(kw_regex),
                Org.services.op('~*')(kw_regex),
                Org.mission.op('~*')(kw_regex)
            ]

        if municipios:
            muni_regex = to_regex_or(*clean_and_split(municipios))
            mun_conditions.append(Org.location.op('~*')(muni_regex))

        orgs = list(Org.query.filter(
            and_(
                or_(*kw_conditions),
                or_(*mun_conditions))))

        if not orgs:
            return _send_not_found("No encontramos nada :(")

        org_names = [sms_org_format(org) for org in orgs]

        response = twiml.Response()
        message = ['Organizaciones encontrado bajo "{}":'.format(raw_query)]
        response.message(
            '\n'.join(message + org_names))
        return str(response)




endpoints = [UsersEndpoint, OrgsEndpoint, SMSOrgEndpoint]

# -*- coding: utf-8 -*-
"""
    api.resources
    ~~~~~~~~~~~~~~~~
    API resources
"""
from uuid import uuid4
from flask import Flask, request, current_app
from flask_restful import abort, Resource
from hackea.models import User, Org
from hackea.core import db
from twilio import twiml

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
            name=data['name'],
            phone=data['phone'])
        new_user.set_password(data['password'])
        current_app.logger.info("created {}".format(data['email']))
        db.session.add(new_user)
        db.session.commit()

        return {"success": True, "user_id": new_user.id}, 201


class OrgsEndpoint(Resource):
    uri = "/orgs"

    def get(self):
        orgs = [org.as_dict() for org in Org.query.all()]
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
            name=name)
        new_org.organizers.append(user)
        db.session.add(new_org)
        db.session.commit()
        return {"success": True, "org_id": new_org.id, "user_id": user_id}, 201

class SMSOrgEndpoint(Resource):
    uri = '/sms/orgs'

    def post(self):
        name = request.form['Body']
        orgs = list(Org.query.filter(Org.name.contains(name)))

        if not orgs:
            return _send_not_found()
        org_names = [org.name for org in orgs]
        response = twiml.Response()
        message = ["Organizaciones con {} en su nombre:".format(name)]
        response.message(
            '\n'.join(message + org_names))
        return str(response)


def _send_not_found():
    response = twiml.Response()
    response.message("No encontramos nada :(")
    return str(response)


__all__ = [UsersEndpoint, OrgsEndpoint, SMSOrgEndpoint]
B

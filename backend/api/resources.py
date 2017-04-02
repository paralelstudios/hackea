# -*- coding: utf-8 -*-
"""
    api.resources
    ~~~~~~~~~~~~~~~~
    API resources
"""
import uuid
from flask import Flask, request, current_app
from flask_restful import abort, Resource
from hackea.models import User, Org
from hackea.core import db


class UsersEndpoint(Resource):
    uri = "/users"
    def post(self):
        data = request.form

        if list(User.query.filter_by(email=data['email'])):
            # and if two ppl try to create acount at the same time hmmm??
            return abort(400, message='User {} already exists'.format(data['email']))
        new_user = User(
            id=str(uuid.uuid4()),
            email=data['email'],
            name=data['name'],
            phone=data['phone'])
        new_user.set_password(data['password'])
        current_app.logger.info("created {}".format(data['email'])
        db.session.add(new_user)
        db.session.commit()

        return {"success": True}, 201


class OrgsEndpoint(Resource):
    uri = "/orgs"

    def post(self):
        query = request.form["query"]
        orgs = list(Org.query.filter(Org.name.contains(query)))
        if not orgs:
            return abort(404, message="No org with {} in name".format(query))
        return '\n'.join(org.name for org in orgs)

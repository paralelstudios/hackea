# -*- coding: utf-8 -*-
"""
    api.resources.following
    ~~~~~~~~~~~~~~~~
    Following API resources
"""


from flask import request

from flask_restful import abort
from aidex.models import User, Org
from aidex.helpers import try_committing
from aidex.core import db
from ..helpers import get_entity
from .base import JWTEndpoint


class FollowEndpoint(JWTEndpoint):
    uri = "/follow"
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "org_id": {"type": "string"}},
        "required": ["user_id", "org_id"]
    }

    def _get_entites(self, data):
        if "org_id" not in data:
            abort(400, "Need an org_id to (un)follow")
        user = get_entity(User, data['user_id'], True)
        org = get_entity(Org, data['org_id'], True)

        return user, org

    def post(self):
        self.validate_form(request.json)
        user, org = self._get_entites(request.json)
        if org in user.following:
            abort(409, description="User {} is already following {}".format(user.email, org.name))
        user.following.append(org)
        try_committing(db.session)
        return {"user_id": user.id,
                "org_id": org.id}, 200

    def get(self):
        self.validate_form(request.json)
        user = get_entity(User, request.json["user_id"])
        followed_orgs = [org.as_dict() for org in user.following]
        return {"count": len(followed_orgs),
                "followed_orgs": followed_orgs}


class UnfollowEndpoint(FollowEndpoint):
    uri = "/unfollow"
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "org_id": {"type": "string"}},
        "required": ["user_id"]
    }

    def post(self):
        self.validate_form(request.json)
        user, org = self._get_entites(request.json)
        if org not in user.following:
            abort(409, description="User {} is not following {}".format(user.email, org.name))
        user.following.remove(org)
        try_committing(db.session)
        return {"user_id": user.id,
                "org_id": org.id}, 200


ENDPOINTS = [FollowEndpoint, UnfollowEndpoint]

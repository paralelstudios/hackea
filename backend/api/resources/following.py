# -*- coding: utf-8 -*-
"""
    api.resources.following
    ~~~~~~~~~~~~~~~~
    Following API resources
"""
from flask import request, jsonify
from flask_restful import abort
from aidex.helpers import try_committing
from aidex.core import db
from ..helpers import get_org, get_user, get_organizer_and_org
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
        user = get_user(data['user_id'], True)
        org = get_org(data['org_id'], True)

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


class FollowingEndpoint(FollowEndpoint):
    uri = "/following"

    def get(self):
        if "user_id" not in request.json:
            abort(400, description="User id need to find user's follows")
        user = get_user(request.json["user_id"])
        return jsonify({
            "user_id": user.id,
            "count": len(user.following),
            "followed_orgs": user.following})


class UnfollowEndpoint(FollowEndpoint):
    uri = "/unfollow"

    def post(self):
        self.validate_form(request.json)
        user, org = self._get_entites(request.json)
        if org not in user.following:
            abort(409, description="User {} is not following {}".format(user.email, org.name))
        user.following.remove(org)
        try_committing(db.session)
        return {"user_id": user.id,
                "org_id": org.id}


class FollowersEndpoint(FollowEndpoint):
    uri = "/followers"

    def get(self):
        self.validate_form(request.json)
        user, org = get_organizer_and_org(request.json["user_id"],
                                          request.json["org_id"])
        return jsonify({"org_id": org.id,
                        "count": len(org.followers),
                        "followers": org.followers})


ENDPOINTS = [FollowEndpoint, UnfollowEndpoint, FollowingEndpoint, FollowersEndpoint]

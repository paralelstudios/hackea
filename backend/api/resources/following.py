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
        self.validate_query(request.args, "user_id")
        user = get_user(request.args["user_id"])
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
        self.validate_query(request.args.keys())
        user, org = get_organizer_and_org(request.args["user_id"],
                                          request.args["org_id"])
        return jsonify({"org_id": org.id,
                        "count": len(org.followers),
                        "followers": org.followers})


ENDPOINTS = [FollowEndpoint, UnfollowEndpoint, FollowingEndpoint, FollowersEndpoint]

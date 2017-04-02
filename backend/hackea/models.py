# -*- coding: utf-8 -*-
"""
    hackea
    ~~~~~~
"""
import bcrypt

from .core import db
from sqlalchemy.dialects.postgresql import (UUID, JSONB)
from flask import current_app

class User(db.Model):
    """
    User represents the base agent in the system
    """
    __tablename__ = 'users'
    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    name = db.Column(db.String)
    phone = db.Column(db.String)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password.encode("UTF-8"), self.password)
        return self.password == pwhash


org_owners_table = db.Table('org_owners',
    db.Column('user_id', UUID,
                  db.ForeignKey('users.id')),
    db.Column('org_id', UUID,
                  db.ForeignKey('orgs.id'))
)
class Org(db.Model):
    """
    Org represents an organization that a user may found
    """
    __tablename__ = 'orgs'
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    features = db.Column(JSONB)

    def as_dict(self):
        return {x: y
                    for (x, y)
                    in self.__dict__.items()
                    if x != "_sa_instance_state"}

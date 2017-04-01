# -*- coding: utf-8 -*-
"""
    hackea
    ~~~~~~
"""

from .core import db
from sqlalchemy.dialects.postgresql import (UUID, JSONB)


class User(db.Model):
    """
    User represents the base agent in the system
    """
    __tablename__ = 'users'
    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    entity_id = db.Column(
        UUID,
        db.ForeignKey('entities.id', ondelete="CASCADE"),
        index=True)

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash


class Entity(db.Model):
    """
    Entity represents the connector between Users and their roles in the system
    """

    __tablename__ = 'entities'
    id = db.Column(UUID, primary_key=True)


class Org(db.Model):
    """
    Org represents an organization that a user may found
    """
    __tablename__ = 'orgs'
    id = db.Column(UUID, primary_key=True)
    features = db.Column(JSONB)
    organizers = db.relationship(
        Entity, backref='orgs', lazy='dynamic')

# -*- coding: utf-8 -*-
"""
    aidex models
    ~~~~~~
"""
from toolz import valfilter
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm.state import InstanceState
from flask_bcrypt import generate_password_hash, check_password_hash
from flask import current_app
from .core import db


class Dictable(object):
    def _is_dictable(self, x):
        if not isinstance(x, (InstanceState, db.Model)):
            return True
        return False

    def as_dict(self):
        return valfilter(self._is_dictable, dict(self.__dict__))


org_owners_table = db.Table('org_owners',
                            db.Column('user_id', UUID,
                                      ForeignKey('users.id')),
                            db.Column('org_id', UUID,
                                      ForeignKey('orgs.id')))


follower_followee_table = db.Table('follows',
                                   db.Column('user_id', UUID,
                                             ForeignKey('users.id')),
                                   db.Column('org_id', UUID,
                                             ForeignKey('orgs.id')))


class EventAttendance(db.Model, Dictable):
    __tablename_ = 'event_attendances'
    user_id = db.Column(UUID, ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(UUID, ForeignKey('events.id'), primary_key=True)
    reviews = db.Column(JSONB)
    as_volunteer = db.Column(db.Boolean, server_default='f')
    attendee = db.relationship("User", back_populates="events")
    event = db.relationship("Event", back_populates="attendees")


class User(db.Model, Dictable):
    """
    User represents the base agent in the system
    """
    __tablename__ = 'users'
    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime,
                          server_default=func.now())
    _password = db.Column(db.Binary, nullable=False)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    following = db.relationship(
        "Org", secondary=follower_followee_table,
        backref="followers")
    orgs = db.relationship(
        "Org", secondary=org_owners_table,
        backref="organizers")
    events = db.relationship("EventAttendance", back_populates="attendee")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, password):
        self._password = generate_password_hash(
            password, current_app.config['BCRYPT_LOG_ROUNDS'])

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def __str__(self):
        return "User(id='%s')" % self.id


class Org(db.Model, Dictable):
    """
    Org represents an organization that a user may found
    """
    __tablename__ = 'orgs'
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String, nullable=False)
    mission = db.Column(db.String, nullable=False)
    location_id = db.Column(db.Integer, ForeignKey("locations.id"))
    location = db.relationship("Location", uselist=False)
    phone = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    services = db.Column(ARRAY(db.String), nullable=False)
    established = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    fiveoone = db.Column(db.Boolean, server_default='f')
    premium = db.Column(db.Boolean, server_default='f')
    products = db.relationship("Product", backref="org")
    events = db.relationship("Event", backref="org")


class Product(db.Model, Dictable):
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    photo_uri = db.Column(db.String)
    org_id = db.Column(UUID, ForeignKey('orgs.id'))
    price = db.Column(db.Float)


class Location(db.Model, Dictable):
    """
    Location represents a geographical location (crazy right?))
    """
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)


class Event(db.Model, Dictable):
    __tablename__ = 'events'
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    org_id = db.Column(UUID, ForeignKey("orgs.id"))
    timestamp = db.Column(db.DateTime, server_default=func.now())
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    location_id = db.Column(db.Integer, ForeignKey("locations.id"))
    location = db.relationship("Location", uselist=False)
    attendees = db.relationship("EventAttendance", back_populates="event")

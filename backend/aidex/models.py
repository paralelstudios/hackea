# -*- coding: utf-8 -*-
"""
    aidex models
    ~~~~~~
"""
from toolz import valfilter, dissoc
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import ForeignKey, func
from datetime import datetime
from sqlalchemy.orm.state import InstanceState
from flask_bcrypt import generate_password_hash, check_password_hash
from flask import current_app
from .core import db


class Dictable(object):
    _secret_keys = None

    def _is_dictable(self, x):
        if not isinstance(x, InstanceState):
            return True
        return False

    def as_dict(self, with_secrets=False):
        d = dict(self.__dict__)
        if not with_secrets:
            d = dissoc(d, *self._secret_keys or [])
        return valfilter(self._is_dictable, d)


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
    __tablename__ = 'event_attendances'
    user_id = db.Column(UUID, ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(UUID, ForeignKey('events.id'), primary_key=True)
    review = db.Column(db.String)
    as_volunteer = db.Column(db.Boolean, server_default='f')
    attendee = db.relationship("User", back_populates="_events")
    event = db.relationship("Event", back_populates="_attendees")


class User(db.Model, Dictable):
    """
    User represents the base agent in the system
    """
    __tablename__ = 'users'
    _secret_keys = ["_password"]
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
    _events = db.relationship("EventAttendance", back_populates="attendee",
                              cascade="all, delete-orphan", passive_deletes=True)

    @hybrid_property
    def reviews(self):
        return [x.review for x in self._events if x.as_volunteer and x.review]

    @hybrid_property
    def events(self):
        return [x.event for x in self._events]

    @hybrid_property
    def attendances(self):
        return [x for x in self.events if x.is_active]

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
    locations = db.relationship("Location", back_populates="org",
                                cascade="all, delete-orphan", passive_deletes=True,
                                lazy="joined")
    phone = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    services = db.Column(ARRAY(db.String))
    categories = db.Column(ARRAY(db.String), nullable=False)
    established = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    premium = db.Column(db.Boolean, server_default='f')
    products = db.relationship("Product", back_populates="org",
                               cascade="all, delete-orphan", passive_deletes=True)
    events = db.relationship("Event", back_populates="org",
                             cascade="all, delete-orphan", passive_deletes=True)

    @hybrid_property
    def active_events(self):
        return [e for e in self.events if e.is_active]


class Product(db.Model, Dictable):
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    photo_uri = db.Column(db.String)
    org_id = db.Column(UUID, ForeignKey('orgs.id'))
    org = db.relationship("Org", back_populates="products", single_parent=True)
    price = db.Column(db.Float)


class Location(db.Model, Dictable):
    """
    Location represents a geographical location (crazy right?))
    """
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String)
    city = db.Column(db.String)
    org_id = db.Column(UUID, ForeignKey("orgs.id"))
    org = db.relationship("Org", back_populates="locations", single_parent=True)
    event_id = db.Column(UUID, ForeignKey("events.id"))
    event = db.relationship("Event", back_populates="location", single_parent=True)
    country = db.Column(db.String)


class Event(db.Model, Dictable):
    __tablename__ = 'events'
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    org_id = db.Column(UUID, ForeignKey("orgs.id"))
    timestamp = db.Column(db.DateTime, server_default=func.now())
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    org = db.relationship("Org", back_populates="events", single_parent=True)
    location = db.relationship("Location", uselist=False, back_populates="event",
                               cascade="all, delete-orphan", lazy="joined")
    _attendees = db.relationship("EventAttendance", back_populates="event",
                                 cascade="all, delete-orphan", passive_deletes=True)

    @hybrid_property
    def is_active(self):
        return self.start_date > datetime.now()

    @hybrid_property
    def volunteers(self):
        return [x.attendee for x in self._attendees if x.as_volunteer]

    @hybrid_property
    def attendees(self):
        return [x.attendee for x in self._attendees]

    @hybrid_property
    def non_volunteer_attendees(self):
        return [x.attendee for x in self._attendees if not x.as_volunteer]

# -*- coding: utf-8 -*-
"""
    hackea
    ~~~~~~
"""
import bcrypt

from .core import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import ForeignKey


class Dictable(object):
    def as_dict(self):
        return {x: y
                for (x, y)
                in self.__dict__.items()
                if x != "_sa_instance_state"}


org_owners_table = db.Table('org_owners',
                            db.Column('user_id', UUID,
                                      ForeignKey('users.id')),
                            db.Column('org_id', UUID,
                                      ForeignKey('orgs.id')))


event_attendance_table = db.Table('event_attendances',
                                  db.Column('user_id', UUID,
                                            ForeignKey('users.id')),
                                  db.Column('event_id', UUID,
                                            ForeignKey('events.id')),
                                  db.Column('reviews', JSONB),
                                  db.Column('as_volunteer', db.Boolean))


class User(db.Model, Dictable):
    """
    User represents the base agent in the system
    """
    __tablename__ = 'users'
    id = db.Column(UUID, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    orgs = db.relationship(
        "Org", secondary=org_owners_table,
        backref="organizers")
    attendances = db.relationship(
        "Event", secondary=event_attendance_table,
        backref="attendees")

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password.encode("UTF-8"), self.password)
        return self.password == pwhash


class Org(db.Model, Dictable):
    """
    Org represents an organization that a user may found
    """
    __tablename__ = 'orgs'
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    mission = db.Column(db.String)
    location_id = db.Column(UUID, ForeignKey("locations.id"))
    location = db.relationship("Location", uselist=False)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    registered = db.Column(db.Boolean)
    services = db.Column(db.String)
    created = db.Column(db.DateTime)
    fiveoone = db.Column(db.Boolean)
    premium = db.Column(db.Boolean)
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
    id = db.Column(UUID, primary_key=True)
    address = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    timezone = db.Column(db.String)


class Event(db.Model, Dictable):
    __tablename__ = 'events'
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String)
    location_id = db.Column(UUID, ForeignKey("locations.id"))
    location = db.relationship("Location", uselist=False)

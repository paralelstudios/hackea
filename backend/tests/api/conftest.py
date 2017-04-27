# -*- coding: utf-8 -*-
"""
    aidex test configuration
    ~~~~~~
"""
import os
import csv
import pytest
from toolz import dissoc
from api.factory import create_app
from aidex.core import db as _db
from alembic.command import upgrade
from alembic.config import Config
from aidex.models import User, Org, Location, Event
from ..helpers import TestFixtureException, jsonify_req
from unidecode import unidecode
from api.helpers import clean_and_split
from aidex.helpers import create_location, uuid
from sqlalchemy.exc import ProgrammingError


@pytest.yield_fixture(scope="session")
def app():
    app = create_app('aidex', settings_module='tests.settings')
    app_ctx = app.app_context()
    app_ctx.push()

    def teardown():
        app_ctx.pop()

    yield app

    teardown()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.yield_fixture(scope="session")
def db(app):
    def teardown():
        print("closing all sessions")
        _db.session.close_all()
        print("reflecting")
        _db.reflect()
        print("dropping all")
        _db.drop_all()

    def buildup_alembic():
        os.environ["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"]
        config = Config(app.config["ALEMBIC_CONFIG"])
        config.set_main_option("script_location", app.config["ALEMBIC_MIGRATIONS"])
        upgrade(config, 'head')
        try:
            User.query.first()
        except ProgrammingError:
            raise TestFixtureException(
                "DB fixture not ready: Users table not built")

    def buildup():
        _db.create_all()

    buildup_alembic()

    yield _db
    print("tearing down db")
    teardown()
    print("done")


@pytest.yield_fixture(scope="function")
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    yield session
    print("tearing down session")
    teardown()
    print("done")


@pytest.fixture()
def ingested_user(user, session):
    session.add(user)
    session.commit()
    return User.query.get(user.id)


@pytest.fixture()
def auth_key(ingested_user, client, user_data):
    data = jsonify_req(dict(email=ingested_user.email,
                            password=user_data["password"]))
    resp = client.post("/auth", **data)
    return dict(Authorization="JWT {}".format(resp.json["access_token"]))


@pytest.fixture()
def ingested_location(session, location):
    session.add(location)
    session.commit()
    return Location.query.get(location.id)


@pytest.fixture()
def ingested_org(ingested_user, session, org):
    org.organizers.append(ingested_user)
    session.add(org)
    session.commit()
    return Org.query.get(org.id)


@pytest.fixture()
def ingested_event(event, ingested_org, session):
    session.add(event)
    ingested_org.events.append(event)
    session.commit()
    return Event.query.get(event.id)


@pytest.fixture()
def ingested_attendance(ingested_event, event_attendance, session):
    ingested_event.attendees.append(event_attendance)
    session.add(event_attendance)
    session.commit()
    return event_attendance


@pytest.fixture()
def orgs_sample(session, app):
    def _create_org(row):
        boolean_keys = {'registered', 'fiveoone'}
        array_keys = {'services', 'categories'}
        location_key = 'cities'
        new_org = {}
        locations = []
        for key, v in row.items():
            if key in boolean_keys:
                new_org[key] = True if ('s' in row[key] or 'y' in row[key]) else False
            elif key in array_keys:
                new_org[key] = clean_and_split(row[key])
            elif key == location_key:
                locations += [create_location(dict(city=city))
                              for city in clean_and_split(row[key])]
            else:
                new_org[key] = unidecode(v)
        org_model = Org(id=uuid(),
                        **dissoc(new_org,
                                 "desires", "fb", "registered",
                                 "candidates", "cities"))
        org_model.locations = locations
        session.add(org_model)
        session.commit()

    columns = ['timestamp', 'name', 'mission', 'cities',
               'phone', 'email', 'fb', 'registered', 'desires', 'services',
               'candidates', 'fiveoone', 'categories']
    path = os.path.join(app.config["BASE_DIR"], "tests/data/org-sample.csv")
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, columns)
        orgs = [
            _create_org(row)
            for row in reader
            if not Org.query.filter_by(name=unidecode(row['name'])).first()]
    print("ingested {} orgs for sample set".format(len(orgs)))

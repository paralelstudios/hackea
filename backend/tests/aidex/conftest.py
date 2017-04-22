# -*- coding: utf-8 -*-
"""
    aidex test configuration
    ~~~~~~
"""
import os
import pytest
from aidex.core import db as _db
from aidex.core.factory import create_app
from alembic.command import upgrade
from alembic.config import Config
from aidex.models import User
from sqlalchemy.exc import ProgrammingError
from ..helpers import TestFixtureException


@pytest.yield_fixture(scope="session")
def app():
    app = create_app('aidex', settings_module='tests.settings')
    app_ctx = app.app_context()
    app_ctx.push()

    def teardown():
        app_ctx.pop()

    yield app

    teardown()


@pytest.yield_fixture(scope="session")
def db(app):
    def teardown():
        _db.reflect()
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

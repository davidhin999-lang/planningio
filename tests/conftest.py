import pytest
from unittest.mock import patch
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from flask import g

from config import TestConfig
import db as db_module

TEST_USER_ID = "test-user-id"
TEST_USER_EMAIL = "teacher@example.com"


@pytest.fixture(scope="session")
def engine():
    from sqlalchemy.pool import StaticPool

    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # pysqlite workaround: use manual transaction control so that SAVEPOINT +
    # RELEASE SAVEPOINT inside a session.commit() can still be rolled back by
    # the outer connection.rollback() in test teardown.
    @event.listens_for(eng, "connect")
    def _set_autocommit(dbapi_conn, _rec):
        dbapi_conn.isolation_level = None  # disable pysqlite implicit transactions

    @event.listens_for(eng, "begin")
    def _begin(conn):
        conn.exec_driver_sql("BEGIN")

    from db import init_db
    init_db(engine=eng)
    return eng


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
    session = Session()
    with patch.object(db_module, "SessionLocal", Session):
        yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def app(db_session):
    from app import create_app

    application = create_app(TestConfig)

    def mock_require_auth(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            g.user_id = TEST_USER_ID
            return f(*args, **kwargs)
        return decorated

    with patch("auth.middleware.require_auth", mock_require_auth), \
         patch("auth.routes.require_auth", mock_require_auth), \
         patch("generation.routes.require_auth", mock_require_auth), \
         patch("planeaciones.routes.require_auth", mock_require_auth), \
         patch("billing.routes.require_auth", mock_require_auth), \
         patch("admin.routes.require_auth", mock_require_auth):
        yield application


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def seeded_user(db_session):
    from models.models import User, Subscription
    from datetime import datetime, timezone, timedelta

    user = User(id=TEST_USER_ID, email=TEST_USER_EMAIL, display_name="Test Teacher")
    db_session.add(user)
    sub = Subscription(
        user_id=TEST_USER_ID,
        plan="free",
        status="active",
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(sub)
    db_session.commit()
    return user

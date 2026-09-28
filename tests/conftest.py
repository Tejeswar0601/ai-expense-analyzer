"""
Shared pytest fixtures for the whole test suite.

IMPORTANT: this file patches the database to an in-memory SQLite
database BEFORE any other backend module is imported, so every
module's `from backend.database.connection import engine` picks up
the test database rather than trying to reach real MySQL.

Individual tests get isolation not by wiping the database between
tests, but by each registering its own fresh user - since every
service in this app already filters strictly by user_id, this mirrors
exactly how the real app keeps users' data separate.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.database.connection as conn_module

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
conn_module.engine = _test_engine
conn_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

from backend.models import user, expense, budget, ai_insight  # noqa: E402
from backend.database.connection import Base  # noqa: E402

Base.metadata.create_all(bind=_test_engine)

from backend.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

# Registration now sends a real OTP email - make sure tests NEVER hit
# a real SMTP server regardless of what's in .env. Individual tests
# (e.g. test_otp_service.py) can still override this per-test with
# pytest's monkeypatch fixture when they need to inspect what was sent.
from backend.services import email_service  # noqa: E402


def _no_op_send_email(to_address, subject, body):
    pass


email_service.send_email = _no_op_send_email


@pytest.fixture(scope="session")
def client():
    """A single TestClient shared across the whole test session."""
    return TestClient(app)


_email_counter = itertools.count(1)


@pytest.fixture()
def auth_headers(client):
    """Registers and logs in a brand-new user for this test only, so
    it never sees another test's data even on the shared database."""
    n = next(_email_counter)
    email = f"tester{n}@example.com"
    client.post("/api/auth/register", json={
        "full_name": f"Test User {n}",
        "email": email,
        "password": "testpass123",
    })
    login = client.post("/api/auth/login", json={"email": email, "password": "testpass123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def db_session():
    """A raw DB session for tests that exercise a service layer
    directly rather than going through the HTTP API."""
    from backend.database.connection import SessionLocal
    session = SessionLocal()
    yield session
    session.close()

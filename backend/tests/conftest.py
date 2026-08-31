"""
Pytest Configuration

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import os

# Tests must NEVER write into the developer's real/dev database - this
# has to happen before any `app.*` module is imported anywhere (below,
# or transitively via other test files pytest collects first), because
# `app.config.settings.settings` is a module-level singleton read once
# at import time. Redirect to an isolated database on the same
# Postgres server/credentials, regardless of what POSTGRES_DATABASE
# a local .env points at. Override with POSTGRES_TEST_DATABASE if the
# default name collides with something.
os.environ["POSTGRES_DATABASE"] = os.environ.get(
    "POSTGRES_TEST_DATABASE", "expenseiq_test"
)

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.main import app
from app.models.employee import Employee


@pytest.fixture(scope="session", autouse=True)
def _test_database_schema():
    """
    Creates every table on the isolated test database if they don't
    already exist yet (e.g. a fresh `expenseiq_test` a developer just
    created locally). A no-op against a database Alembic already
    migrated (CI). `app.database.base` imports every model, so
    `Base.metadata` is always fully populated here.
    """

    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    """
    FastAPI Test Client.
    """

    return TestClient(app)


@pytest.fixture
def hr_head_headers(client):
    """
    Bootstraps a fresh HR_HEAD employee directly against the DB -
    there is no public endpoint to create the very first HR_HEAD
    (same real-world chicken-and-egg every company solves by hand
    once) - then logs in via the real /auth/login API, so every test
    built on top of this fixture exercises genuine authenticated
    endpoints from that point on.
    """

    unique = uuid.uuid4().hex[:8]
    email = f"hrhead{unique}@example.com"
    password = "HrHead@123"

    db = SessionLocal()

    try:
        employee = Employee(
            employee_code=f"HRH{unique}",
            full_name="Test HR Head",
            email=email,
            department="HR",
            designation="HR Head",
            role="HR_HEAD",
            hashed_password=hash_password(password),
        )
        db.add(employee)
        db.commit()

    finally:
        db.close()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

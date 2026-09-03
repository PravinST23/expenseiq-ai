"""
Pytest Configuration

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import os

# Tests must NEVER write into the developer's real/dev data - this has
# to happen before any `app.*` module is imported anywhere (below, or
# transitively via other test files pytest collects first), because
# `app.config.settings.settings` is a module-level singleton read once
# at import time.
#
# Isolation is schema-based, not database-based: every connection this
# process opens gets its search_path pinned to a dedicated schema (see
# Settings.DATABASE_URL / POSTGRES_SCHEMA), inside whatever database
# POSTGRES_DATABASE already points at - the app's real dev/CI database
# is left untouched, since an app user only needs ordinary CREATE
# SCHEMA rights on a database it already owns, not the CREATEDB
# superuser-adjacent privilege a separate database would need. Override
# the schema name with POSTGRES_TEST_SCHEMA if it collides with
# something.
os.environ["POSTGRES_SCHEMA"] = os.environ.get(
    "POSTGRES_TEST_SCHEMA", "pgtest"
)

import uuid

import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.main import app
from app.models.employee import Employee


@pytest.fixture(scope="session", autouse=True)
def _test_database_schema():
    """
    Drops and recreates the isolated test schema fresh at the start
    of every pytest session, then creates every table on it.

    A genuinely disposable `expenseiq_test` database would give this
    for free each time it's (re)created; a persisted schema that's
    only ever created-if-missing does not - repeat local runs would
    silently accumulate data across sessions. That's not hypothetical:
    it's exactly what caused a real, non-deterministic failure the
    first time this schema was reused across three manual runs in the
    same session - a fuzzy-duplicate-match test picked up an unrelated
    expense left over from an earlier run instead of the one it
    created itself. Dropping first guarantees every run starts from
    the same clean slate the original database-per-run design assumed.
    """

    with engine.begin() as conn:
        conn.execute(
            text(f'DROP SCHEMA IF EXISTS "{settings.POSTGRES_SCHEMA}" CASCADE')
        )
        conn.execute(
            text(f'CREATE SCHEMA "{settings.POSTGRES_SCHEMA}"')
        )

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

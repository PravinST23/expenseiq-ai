"""
Auth API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import time
from uuid import uuid4

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

EMPLOYEE_URL = "/api/v1/employees"
AUTH_URL = "/api/v1/auth"


def create_employee_payload(role="EMPLOYEE", password="Password@123"):

    unique = uuid4().hex[:8]

    payload = {
        "employee_code": f"AUTH{unique}",
        "full_name": "Auth Test Employee",
        "email": f"auth{unique}@example.com",
        "department": "IT",
        "designation": "Developer",
        "role": role,
    }

    if password is not None:
        payload["password"] = password

    return payload


# ---------------------------------------------------------
# Password hashing
# ---------------------------------------------------------


def test_hash_password_is_not_plaintext():

    hashed = hash_password("Password@123")

    assert hashed != "Password@123"
    assert hashed.startswith("$2b$")


def test_verify_password_correct_and_incorrect():

    hashed = hash_password("Password@123")

    assert verify_password("Password@123", hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_verify_password_handles_malformed_hash_gracefully():

    assert verify_password("anything", "not-a-real-hash") is False


# ---------------------------------------------------------
# JWT create / decode
# ---------------------------------------------------------


def test_token_round_trips_employee_id_and_role():

    employee_id = uuid4()

    token, expires_at = create_access_token(
        employee_id=employee_id,
        role="L2_FINANCE",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == str(employee_id)
    assert payload["role"] == "L2_FINANCE"
    assert expires_at is not None


def test_expired_token_is_rejected():

    token, _ = create_access_token(
        employee_id=uuid4(),
        role="EMPLOYEE",
        expires_minutes=0,
    )

    time.sleep(2)

    try:
        decode_access_token(token)
        assert False, "expired token should have been rejected"
    except InvalidTokenError:
        pass


def test_tampered_token_is_rejected():

    token, _ = create_access_token(employee_id=uuid4(), role="EMPLOYEE")

    tampered = token[:-4] + "abcd"

    try:
        decode_access_token(tampered)
        assert False, "tampered token should have been rejected"
    except InvalidTokenError:
        pass


# ---------------------------------------------------------
# Employee creation with password
# ---------------------------------------------------------


def test_create_employee_with_password_never_leaks_hash(client):

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json=create_employee_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["has_password"] is True
    assert "password" not in data
    assert "hashed_password" not in data


def test_create_employee_without_password_cannot_log_in(client):

    payload = create_employee_payload(password=None)

    response = client.post(f"{EMPLOYEE_URL}/", json=payload)

    assert response.status_code == 201
    assert response.json()["has_password"] is False

    login = client.post(
        f"{AUTH_URL}/login",
        json={"email": payload["email"], "password": "anything"},
    )

    assert login.status_code == 401


# ---------------------------------------------------------
# Login API
# ---------------------------------------------------------


def test_login_success_returns_bearer_token(client):

    payload = create_employee_payload(password="Password@123")

    client.post(f"{EMPLOYEE_URL}/", json=payload)

    response = client.post(
        f"{AUTH_URL}/login",
        json={"email": payload["email"], "password": "Password@123"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["role"] == payload["role"]
    assert len(data["access_token"]) > 20


def test_login_wrong_password_rejected(client):

    payload = create_employee_payload(password="Password@123")

    client.post(f"{EMPLOYEE_URL}/", json=payload)

    response = client.post(
        f"{AUTH_URL}/login",
        json={"email": payload["email"], "password": "WrongPassword"},
    )

    assert response.status_code == 401


def test_login_unknown_email_rejected(client):

    response = client.post(
        f"{AUTH_URL}/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# Token validation via /auth/me
# ---------------------------------------------------------


def _login(client, role="EMPLOYEE"):

    payload = create_employee_payload(role=role, password="Password@123")

    client.post(f"{EMPLOYEE_URL}/", json=payload)

    login = client.post(
        f"{AUTH_URL}/login",
        json={"email": payload["email"], "password": "Password@123"},
    )

    return login.json()["access_token"], payload


def test_me_requires_no_token(client):

    response = client.get(f"{AUTH_URL}/me")

    assert response.status_code == 401


def test_me_rejects_garbage_token(client):

    response = client.get(
        f"{AUTH_URL}/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


def test_me_returns_identity_for_valid_token(client):

    token, payload = _login(client)

    response = client.get(
        f"{AUTH_URL}/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]
    assert response.json()["role"] == payload["role"]

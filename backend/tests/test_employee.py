"""
Employee API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4


BASE_URL = "/api/v1/employees"


def create_employee_payload():

    unique = uuid4().hex[:6]

    return {
        "employee_code": f"EMP{unique}",
        "full_name": "Test Employee",
        "email": f"employee{unique}@example.com",
        "phone_number": "9876543210",
        "department": "Engineering",
        "designation": "Software Engineer",
        "manager_name": "John Manager",
    }


def test_create_employee(client):

    payload = create_employee_payload()

    response = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["employee_code"] == payload["employee_code"]
    assert data["full_name"] == payload["full_name"]
    assert data["email"] == payload["email"]
    assert "id" in data


def test_get_all_employees(client):

    response = client.get(
        f"{BASE_URL}/",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_employee_by_id(client):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    employee_id = create.json()["id"]

    response = client.get(
        f"{BASE_URL}/{employee_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == employee_id


def test_update_employee(client):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    employee_id = create.json()["id"]

    update_payload = {
        "designation": "Senior Software Engineer",
    }

    response = client.put(
        f"{BASE_URL}/{employee_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["designation"]
        == "Senior Software Engineer"
    )


def test_delete_employee(client):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    employee_id = create.json()["id"]

    response = client.delete(
        f"{BASE_URL}/{employee_id}",
    )

    assert response.status_code == 204
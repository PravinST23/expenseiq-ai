"""
Employee API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

Create/Update/Delete are HR_HEAD only.
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
    }


def test_create_employee_requires_hr_head(client):

    response = client.post(f"{BASE_URL}/", json=create_employee_payload())

    assert response.status_code == 401


def test_create_employee(client, hr_head_headers):

    payload = create_employee_payload()

    response = client.post(
        f"{BASE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["employee_code"] == payload["employee_code"]
    assert data["full_name"] == payload["full_name"]
    assert data["email"] == payload["email"]
    assert data["role"] == "EMPLOYEE"
    assert "id" in data


def test_get_all_employees(client):

    response = client.get(f"{BASE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_employee_by_id(client, hr_head_headers):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    assert create.status_code == 201

    employee_id = create.json()["id"]

    response = client.get(f"{BASE_URL}/{employee_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == employee_id


def test_update_employee_requires_hr_head(client, hr_head_headers):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    employee_id = create.json()["id"]

    response = client.put(
        f"{BASE_URL}/{employee_id}",
        json={"designation": "Senior Software Engineer"},
    )

    assert response.status_code == 401


def test_update_employee(client, hr_head_headers):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    assert create.status_code == 201

    employee_id = create.json()["id"]

    response = client.put(
        f"{BASE_URL}/{employee_id}",
        json={"designation": "Senior Software Engineer"},
        headers=hr_head_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["designation"] == "Senior Software Engineer"


def test_delete_employee(client, hr_head_headers):

    payload = create_employee_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    assert create.status_code == 201

    employee_id = create.json()["id"]

    response = client.delete(
        f"{BASE_URL}/{employee_id}",
        headers=hr_head_headers,
    )

    assert response.status_code == 204

"""
Project API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

BASE_URL = "/api/v1/projects"


def create_project_payload():

    unique = uuid4().hex[:6]

    return {
        "project_code": f"PRJ{unique}",
        "project_name": f"ExpenseIQ-{unique}",
        "client_name": "Internal",
        "project_description": "Expense Management System",
        "start_date": "2026-07-01",
        "end_date": "2026-12-31",
        "project_manager": "Pravin Shanmugavel",
        "project_budget": 100000.00,
    }


def test_create_project(client):

    payload = create_project_payload()

    response = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_code"] == payload["project_code"]
    assert data["project_name"] == payload["project_name"]
    assert data["client_name"] == payload["client_name"]
    assert "id" in data


def test_get_all_projects(client):

    response = client.get(
        f"{BASE_URL}/",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project_by_id(client):

    payload = create_project_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    project_id = create.json()["id"]

    response = client.get(
        f"{BASE_URL}/{project_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id


def test_update_project(client):

    payload = create_project_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    project_id = create.json()["id"]

    update_payload = {
        "project_manager": "Updated Manager",
    }

    response = client.put(
        f"{BASE_URL}/{project_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_manager"] == "Updated Manager"


def test_delete_project(client):

    payload = create_project_payload()

    create = client.post(
        f"{BASE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    project_id = create.json()["id"]

    response = client.delete(
        f"{BASE_URL}/{project_id}",
    )

    assert response.status_code == 204
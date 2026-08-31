"""
Project API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

Create/Update/Delete are HR_HEAD only; every project requires a
team_id (which MAC it runs under).
"""

from uuid import uuid4

from tests.helpers import create_team

BASE_URL = "/api/v1/projects"


def create_project_payload(team_id):

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
        "team_id": team_id,
    }


def test_create_project_requires_hr_head(client, hr_head_headers):

    team_id = create_team(client, hr_head_headers)

    response = client.post(
        f"{BASE_URL}/",
        json=create_project_payload(team_id),
    )

    assert response.status_code == 401


def test_create_project(client, hr_head_headers):

    team_id = create_team(client, hr_head_headers)
    payload = create_project_payload(team_id)

    response = client.post(
        f"{BASE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_code"] == payload["project_code"]
    assert data["project_name"] == payload["project_name"]
    assert data["client_name"] == payload["client_name"]
    assert data["team_id"] == team_id
    assert "id" in data


def test_get_all_projects(client):

    response = client.get(f"{BASE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project_by_id(client, hr_head_headers):

    team_id = create_team(client, hr_head_headers)

    create = client.post(
        f"{BASE_URL}/",
        json=create_project_payload(team_id),
        headers=hr_head_headers,
    )

    assert create.status_code == 201

    project_id = create.json()["id"]

    response = client.get(f"{BASE_URL}/{project_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id


def test_update_project(client, hr_head_headers):

    team_id = create_team(client, hr_head_headers)

    create = client.post(
        f"{BASE_URL}/",
        json=create_project_payload(team_id),
        headers=hr_head_headers,
    )

    assert create.status_code == 201

    project_id = create.json()["id"]

    response = client.put(
        f"{BASE_URL}/{project_id}",
        json={"project_manager": "Updated Manager"},
        headers=hr_head_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_manager"] == "Updated Manager"


def test_delete_project(client, hr_head_headers):

    team_id = create_team(client, hr_head_headers)

    create = client.post(
        f"{BASE_URL}/",
        json=create_project_payload(team_id),
        headers=hr_head_headers,
    )

    assert create.status_code == 201

    project_id = create.json()["id"]

    response = client.delete(
        f"{BASE_URL}/{project_id}",
        headers=hr_head_headers,
    )

    assert response.status_code == 204

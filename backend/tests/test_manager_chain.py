"""
Manager-Chain Resolver Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import pytest

from app.database.session import SessionLocal
from app.models.employee import Employee
from app.workflow.manager_chain import ApproverResolutionError, resolve_approver
from tests.helpers import create_employee, create_org_chain


def test_resolve_level_1_is_direct_manager(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)

    requester, _ = chain["requester"]
    manager, _ = chain["manager"]

    db = SessionLocal()

    try:
        requester_row = db.get(Employee, requester["id"])
        resolved = resolve_approver(db, requester_row, 1)
        assert str(resolved.employee.id) == manager["id"]
        assert resolved.label == "Reporting Manager"
    finally:
        db.close()


def test_resolve_level_2_is_skip_level_manager(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)

    requester, _ = chain["requester"]
    skip_manager, _ = chain["skip_manager"]

    db = SessionLocal()

    try:
        requester_row = db.get(Employee, requester["id"])
        resolved = resolve_approver(db, requester_row, 2)
        assert str(resolved.employee.id) == skip_manager["id"]
        assert resolved.label == "Skip-Level Manager"
    finally:
        db.close()


def test_resolve_level_3_is_cfo(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)

    requester, _ = chain["requester"]
    cfo, _ = chain["cfo"]

    db = SessionLocal()

    try:
        requester_row = db.get(Employee, requester["id"])
        resolved = resolve_approver(db, requester_row, 3)
        assert str(resolved.employee.id) == cfo["id"]
        assert resolved.label == "CFO"
    finally:
        db.close()


def test_no_cfo_configured_raises(client, hr_head_headers):
    """
    Uses a dedicated DB session and reverts any pre-existing CFO
    accounts for the duration of this assertion only, so it doesn't
    permanently disturb CFOs other tests created.
    """

    requester, _ = create_employee(client, hr_head_headers, role="EMPLOYEE")

    db = SessionLocal()

    try:
        requester_row = db.get(Employee, requester["id"])

        existing_cfo_ids = [
            row.id
            for row in db.query(Employee).filter(Employee.role == "CFO").all()
        ]

        db.query(Employee).filter(Employee.role == "CFO").update(
            {"role": "EMPLOYEE"}
        )
        db.commit()

        try:
            with pytest.raises(ApproverResolutionError):
                resolve_approver(db, requester_row, 1)
        finally:
            if existing_cfo_ids:
                db.query(Employee).filter(
                    Employee.id.in_(existing_cfo_ids)
                ).update({"role": "CFO"}, synchronize_session=False)
                db.commit()

    finally:
        db.close()

"""
Manager-Chain Approval Resolver

Author: Pravin Shanmugavel
Project: ExpenseIQ

Resolves WHO must act at each level of an expense's approval
routing, based on the requester's real org-chart position rather
than a generic role:

  Level 1 - Reporting Manager (RM)        -> requester.manager
  Level 2 - Skip-Level Manager (RM's RM)  -> requester.manager.manager
  Level 3 - CFO                            -> the employee holding
                                               the CFO role

If an employee has no manager on file (or their manager has no
manager), routing escalates straight to the CFO for that level
rather than failing - every claim must still resolve to someone.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.employee import Employee

HEAD_ROLE = "CFO"

LEVEL_LABELS = {
    1: "Reporting Manager",
    2: "Skip-Level Manager",
    3: "CFO",
}


class ApproverResolutionError(Exception):
    """
    Raised when no CFO-role employee exists to resolve routing
    against - a configuration problem (org setup incomplete), not a
    per-request one.
    """


@dataclass
class ResolvedApprover:
    employee: Employee
    level: int
    label: str


def _head_employee(db: Session) -> Employee:
    """
    In a well-formed deployment there is exactly one active CFO;
    ordering by most-recently-created is a defensive tie-break if
    more than one somehow exists (e.g. an HR Head reassigning the
    role without deactivating the previous holder).
    """

    head = (
        db.query(Employee)
        .filter(Employee.role == HEAD_ROLE, Employee.is_active.is_(True))
        .order_by(Employee.created_at.desc())
        .first()
    )

    if head is None:
        raise ApproverResolutionError(
            "No active employee holds the CFO role - cannot route "
            "expense approvals. An HR Head must assign the CFO role "
            "to someone first."
        )

    return head


def resolve_approver(
    db: Session,
    requester: Employee,
    level: int,
) -> ResolvedApprover:
    """
    Resolve which employee must act at the given approval level for
    a claim submitted by `requester`.
    """

    if level == 1:

        manager = requester.manager

        employee = manager if manager is not None else _head_employee(db)

    elif level == 2:

        manager = requester.manager
        skip_level = manager.manager if manager is not None else None

        employee = (
            skip_level if skip_level is not None else _head_employee(db)
        )

    elif level == 3:

        employee = _head_employee(db)

    else:
        raise ValueError(f"Unsupported approval level: {level}")

    return ResolvedApprover(
        employee=employee,
        level=level,
        label=LEVEL_LABELS[level],
    )


def level_label(level: int) -> str:
    return LEVEL_LABELS[level]

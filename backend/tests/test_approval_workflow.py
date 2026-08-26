"""
Approval Workflow Unit Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from app.workflow.approval_workflow import approval_workflow
from app.workflow.auto_approval_engine import AutoApprovalResult


def test_auto_approve_level_1_is_system_approved():

    result = approval_workflow.decide(
        AutoApprovalResult(
            recommendation="AUTO_APPROVE_RECOMMENDED",
            required_approval_level=1,
            reason="low risk",
        )
    )

    assert result["approval_status"] == "Approved"
    assert result["approved_by"] == "System"
    assert result["current_approval_level"] == 1


def test_escalate_level_2_awaits_finance():

    result = approval_workflow.decide(
        AutoApprovalResult(
            recommendation="ESCALATE_FOR_REVIEW",
            required_approval_level=2,
            reason="medium risk",
        )
    )

    assert result["approval_status"] == "Pending L1 Manager Approval"
    assert result["approved_by"] is None
    assert result["current_approval_level"] == 1


def test_role_and_level_mapping_round_trip():

    for level in (1, 2, 3):

        role = approval_workflow.role_for_level(level)

        assert approval_workflow.level_for_role(role) == level


def test_unknown_role_returns_none():

    assert approval_workflow.level_for_role("UNKNOWN") is None

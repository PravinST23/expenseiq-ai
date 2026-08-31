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


def test_escalate_level_2_awaits_reporting_manager():

    result = approval_workflow.decide(
        AutoApprovalResult(
            recommendation="ESCALATE_FOR_REVIEW",
            required_approval_level=2,
            reason="medium risk",
        )
    )

    assert result["approval_status"] == "Pending Reporting Manager Approval"
    assert result["approved_by"] is None
    assert result["current_approval_level"] == 1

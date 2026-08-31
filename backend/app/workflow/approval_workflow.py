"""
Approval Workflow

Author: Pravin Shanmugavel
Project: ExpenseIQ

Routes an expense through its 3-level manager-chain approval:
Reporting Manager -> Skip-Level Manager -> CFO (see
app.workflow.manager_chain for how each level resolves to a real
employee). The required routing level for a given expense is
computed by the Smart Auto-Approval Engine (see
app.workflow.auto_approval_engine) from the AI risk score, duplicate
flag, and employee history; this module turns that recommendation
into the initial workflow state.
"""

from app.workflow.auto_approval_engine import AutoApprovalResult
from app.workflow.manager_chain import level_label


class ApprovalWorkflow:
    """
    Approval Decision Workflow.
    """

    def decide(
        self,
        auto_approval: AutoApprovalResult,
    ) -> dict:
        """
        Decide the initial approval status for a freshly
        processed expense, based on the Auto-Approval Engine's
        recommendation.
        """

        if (
            auto_approval.recommendation
            == "AUTO_APPROVE_RECOMMENDED"
            and auto_approval.required_approval_level == 1
        ):

            return {
                "approval_status": "Approved",
                "approved_by": "System",
                "current_approval_level": 1,
            }

        # Routing always starts at level 1 (Reporting Manager),
        # regardless of how high the required level escalates - the
        # auto-approval engine's required_approval_level only
        # decides how many levels the claim must pass through.

        return {
            "approval_status": f"Pending {level_label(1)} Approval",
            "approved_by": None,
            "current_approval_level": 1,
        }


approval_workflow = ApprovalWorkflow()

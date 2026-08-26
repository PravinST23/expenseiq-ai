"""
Approval Workflow

Author: Pravin Shanmugavel
Project: ExpenseIQ

Implements the 3-role (L1 Manager / L2 Finance / L3 CFO) approval
routing described in the approved proposal. The required routing
level for a given expense is computed by the Smart Auto-Approval
Engine (see app.workflow.auto_approval_engine) from the AI risk
score, duplicate flag, and employee history; this module turns that
recommendation into the initial workflow state and governs how an
expense advances from one approval level to the next.
"""

from app.workflow.auto_approval_engine import AutoApprovalResult

# ---------------------------------------------------------
# Approval Levels
# ---------------------------------------------------------

LEVEL_ROLES = {
    1: "L1_MANAGER",
    2: "L2_FINANCE",
    3: "L3_CFO",
}

ROLE_LEVELS = {role: level for level, role in LEVEL_ROLES.items()}

LEVEL_LABELS = {
    1: "L1 Manager",
    2: "L2 Finance",
    3: "L3 CFO",
}


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

        # Routing always starts at L1 Manager, regardless of how
        # high the required level escalates - the auto-approval
        # engine's required_approval_level only decides how many
        # levels the claim must pass through, not where it enters.

        level_label = LEVEL_LABELS[1]

        return {
            "approval_status": f"Pending {level_label} Approval",
            "approved_by": None,
            "current_approval_level": 1,
        }

    def role_for_level(self, level: int) -> str:
        return LEVEL_ROLES[level]

    def level_for_role(self, role: str) -> int | None:
        return ROLE_LEVELS.get(role)


approval_workflow = ApprovalWorkflow()

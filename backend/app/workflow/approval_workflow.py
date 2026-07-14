"""
Approval Workflow

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""


class ApprovalWorkflow:
    """
    Approval Decision Workflow.
    """

    def decide(
        self,
        policy_status: str,
        requires_manager_approval: bool,
    ) -> dict:
        """
        Decide approval status.
        """

        # -------------------------------------
        # PASS
        # -------------------------------------

        if policy_status == "PASS":

            if requires_manager_approval:

                return {
                    "approval_status": "Pending Manager Approval",
                    "approved_by": None,
                }

            return {
                "approval_status": "Approved",
                "approved_by": "System",
            }

        # -------------------------------------
        # FAIL
        # -------------------------------------

        if requires_manager_approval:

            return {
                "approval_status": "Pending Manager Review",
                "approved_by": None,
            }

        return {
            "approval_status": "Rejected",
            "approved_by": "System",
        }


approval_workflow = ApprovalWorkflow()
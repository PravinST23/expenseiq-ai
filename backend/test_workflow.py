"""
Approval Workflow Test

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pprint import pprint

from app.workflow.approval_workflow import approval_workflow

result = approval_workflow.decide(
    policy_status="FAIL",
    requires_manager_approval=True,
)

print("\n========== APPROVAL ==========\n")

pprint(result)
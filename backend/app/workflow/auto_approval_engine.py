"""
Smart Auto-Approval Recommendation Engine

Author: Pravin Shanmugavel
Project: ExpenseIQ

Implements Novelty 3 from the approved proposal - ExpenseIQ tells
approvers what it recommends and why. Combines:

  - the Groq-generated AI Risk Score (fraud_risk, compliance_risk,
    confidence)
  - the Duplicate Fraud Detector result
  - the employee's recent compliance history
  - the deterministic company policy decision (PASS / FAIL)

into one of three recommendations:

  - AUTO_APPROVE_RECOMMENDED
  - ESCALATE_FOR_REVIEW
  - REJECT_RECOMMENDED

and the required approval routing level:

  - 1 -> L1 Manager only
  - 2 -> L1 Manager + L2 Finance
  - 3 -> L1 Manager + L2 Finance + L3 CFO
"""

from dataclasses import dataclass

HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40
LOW_CONFIDENCE_THRESHOLD = 50
HIGH_VALUE_THRESHOLD = 10000


@dataclass
class AutoApprovalResult:

    recommendation: str
    required_approval_level: int
    reason: str


class AutoApprovalEngine:
    """
    Deterministic rule engine layered on top of the Groq risk score.
    """

    def evaluate(
        self,
        *,
        policy_status: str,
        requires_manager_approval: bool,
        fraud_risk: float,
        compliance_risk: float,
        confidence: float,
        duplicate_found: bool,
        amount: float,
        employee_rejection_ratio: float = 0.0,
    ) -> AutoApprovalResult:

        composite_risk = max(fraud_risk or 0, compliance_risk or 0)

        # ------------------------------------------------------
        # Duplicate claims always escalate to the top - a
        # duplicate is either fraud or a genuine mistake, and
        # only a human (CFO level) should resolve which.
        # ------------------------------------------------------

        if duplicate_found:

            return AutoApprovalResult(
                recommendation="REJECT_RECOMMENDED",
                required_approval_level=3,
                reason=(
                    "Duplicate expense detected - matches an "
                    "existing claim on 3 or more fields "
                    "(merchant, amount, date, invoice number)."
                ),
            )

        # ------------------------------------------------------
        # Low confidence extraction - cannot trust the risk
        # score itself, so force a human to look at it.
        # ------------------------------------------------------

        if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:

            return AutoApprovalResult(
                recommendation="ESCALATE_FOR_REVIEW",
                required_approval_level=3,
                reason=(
                    f"AI confidence is low ({confidence:.0f}%) - "
                    "routed to CFO-level manual review."
                ),
            )

        # ------------------------------------------------------
        # Employee has a history of rejected claims - escalate
        # regardless of this claim's own risk score.
        # ------------------------------------------------------

        history_flag = employee_rejection_ratio >= 0.3

        # ------------------------------------------------------
        # High composite risk
        # ------------------------------------------------------

        if composite_risk >= HIGH_RISK_THRESHOLD:

            return AutoApprovalResult(
                recommendation="REJECT_RECOMMENDED",
                required_approval_level=3,
                reason=(
                    f"Composite AI risk score is high "
                    f"({composite_risk:.0f}/100) - fraud or "
                    "policy violation likely."
                ),
            )

        # ------------------------------------------------------
        # Medium risk, high value, or a flagged employee history
        # ------------------------------------------------------

        if (
            composite_risk >= MEDIUM_RISK_THRESHOLD
            or amount > HIGH_VALUE_THRESHOLD
            or history_flag
        ):

            level = 3 if history_flag else 2

            reason_bits = []

            if composite_risk >= MEDIUM_RISK_THRESHOLD:
                reason_bits.append(
                    f"moderate AI risk score "
                    f"({composite_risk:.0f}/100)"
                )

            if amount > HIGH_VALUE_THRESHOLD:
                reason_bits.append("high claim value")

            if history_flag:
                reason_bits.append(
                    "employee has a recent history of "
                    "rejected claims"
                )

            return AutoApprovalResult(
                recommendation="ESCALATE_FOR_REVIEW",
                required_approval_level=level,
                reason=(
                    "Escalated for review: "
                    + ", ".join(reason_bits)
                    + "."
                ),
            )

        # ------------------------------------------------------
        # Policy already failed but risk is low - still needs a
        # human decision, one level up.
        # ------------------------------------------------------

        if policy_status == "FAIL" or requires_manager_approval:

            return AutoApprovalResult(
                recommendation="ESCALATE_FOR_REVIEW",
                required_approval_level=2,
                reason=(
                    "Policy check failed or requires manager "
                    "sign-off - routed to Finance review."
                ),
            )

        # ------------------------------------------------------
        # Everything checks out - low risk, in-policy, no
        # duplicate, confident extraction.
        # ------------------------------------------------------

        return AutoApprovalResult(
            recommendation="AUTO_APPROVE_RECOMMENDED",
            required_approval_level=1,
            reason=(
                f"Low AI risk ({composite_risk:.0f}/100), "
                f"policy check passed, confidence "
                f"{confidence:.0f}% - eligible for fast-track "
                "approval."
            ),
        )


auto_approval_engine = AutoApprovalEngine()

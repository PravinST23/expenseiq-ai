"""
Smart Auto-Approval Engine Unit Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from app.workflow.auto_approval_engine import auto_approval_engine


def _evaluate(**overrides):

    params = {
        "policy_status": "PASS",
        "requires_manager_approval": False,
        "fraud_risk": 10,
        "compliance_risk": 10,
        "confidence": 90,
        "duplicate_found": False,
        "amount": 500,
        "employee_rejection_ratio": 0.0,
    }

    params.update(overrides)

    return auto_approval_engine.evaluate(**params)


def test_low_risk_pass_is_auto_approved():

    result = _evaluate()

    assert result.recommendation == "AUTO_APPROVE_RECOMMENDED"
    assert result.required_approval_level == 1


def test_duplicate_always_rejects_at_level_3():

    result = _evaluate(duplicate_found=True)

    assert result.recommendation == "REJECT_RECOMMENDED"
    assert result.required_approval_level == 3


def test_low_confidence_escalates_to_level_3():

    result = _evaluate(confidence=20)

    assert result.recommendation == "ESCALATE_FOR_REVIEW"
    assert result.required_approval_level == 3


def test_high_composite_risk_rejects():

    result = _evaluate(fraud_risk=85, compliance_risk=20)

    assert result.recommendation == "REJECT_RECOMMENDED"
    assert result.required_approval_level == 3


def test_medium_risk_escalates_to_level_2():

    result = _evaluate(fraud_risk=50, compliance_risk=20)

    assert result.recommendation == "ESCALATE_FOR_REVIEW"
    assert result.required_approval_level == 2


def test_high_value_escalates_even_with_low_risk():

    result = _evaluate(amount=25000)

    assert result.recommendation == "ESCALATE_FOR_REVIEW"
    assert result.required_approval_level == 2


def test_bad_employee_history_forces_level_3():

    result = _evaluate(amount=25000, employee_rejection_ratio=0.5)

    assert result.recommendation == "ESCALATE_FOR_REVIEW"
    assert result.required_approval_level == 3


def test_policy_fail_low_risk_escalates_to_level_2():

    result = _evaluate(
        policy_status="FAIL",
        requires_manager_approval=True,
        fraud_risk=5,
        compliance_risk=5,
    )

    assert result.recommendation == "ESCALATE_FOR_REVIEW"
    assert result.required_approval_level == 2

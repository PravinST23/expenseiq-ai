"""
Hybrid Router Unit Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

Mocks the Gemini / Ollama clients so this test suite never makes a
real network / on-device AI call.
"""

from app.ai import hybrid_router as hybrid_router_module


def test_sensitive_receipt_always_uses_ollama(monkeypatch):

    monkeypatch.setattr(
        hybrid_router_module.ollama_service,
        "extract_receipt",
        lambda path: {"merchant_name": "Local Merchant"},
    )

    def fail_if_called(path):
        raise AssertionError(
            "Gemini should never be called for a sensitive receipt"
        )

    monkeypatch.setattr(
        hybrid_router_module.gemini_service,
        "extract_receipt",
        fail_if_called,
    )

    result = hybrid_router_module.hybrid_router.route(
        "dummy.jpg",
        is_sensitive=True,
    )

    assert result["_engine"] == "ollama"
    assert result["_fallback"] is False


def test_non_sensitive_receipt_uses_gemini(monkeypatch):

    monkeypatch.setattr(
        hybrid_router_module.gemini_service,
        "extract_receipt",
        lambda path: {"merchant_name": "Cloud Merchant"},
    )

    result = hybrid_router_module.hybrid_router.route(
        "dummy.jpg",
        is_sensitive=False,
    )

    assert result["_engine"] == "gemini"
    assert result["_fallback"] is False
    assert result["merchant_name"] == "Cloud Merchant"


def test_gemini_rate_limit_falls_back_to_ollama(monkeypatch):

    def raise_rate_limit(path):
        raise RuntimeError("429 Resource has been exhausted (quota)")

    monkeypatch.setattr(
        hybrid_router_module.gemini_service,
        "extract_receipt",
        raise_rate_limit,
    )

    monkeypatch.setattr(
        hybrid_router_module.ollama_service,
        "extract_receipt",
        lambda path: {"merchant_name": "Fallback Merchant"},
    )

    result = hybrid_router_module.hybrid_router.route(
        "dummy.jpg",
        is_sensitive=False,
    )

    assert result["_engine"] == "ollama"
    assert result["_fallback"] is True
    assert "rate limit" in result["_fallback_reason"].lower()


def test_gemini_other_error_still_falls_back(monkeypatch):

    def raise_generic_error(path):
        raise RuntimeError("network unreachable")

    monkeypatch.setattr(
        hybrid_router_module.gemini_service,
        "extract_receipt",
        raise_generic_error,
    )

    monkeypatch.setattr(
        hybrid_router_module.ollama_service,
        "extract_receipt",
        lambda path: {"merchant_name": "Fallback Merchant"},
    )

    result = hybrid_router_module.hybrid_router.route(
        "dummy.jpg",
        is_sensitive=False,
    )

    assert result["_engine"] == "ollama"
    assert result["_fallback"] is True


def test_both_engines_failing_preserves_the_gemini_reason(monkeypatch):
    """
    Regression test for a real bug found live on Render: when Gemini
    fails (e.g. quota exhaustion) AND the Ollama fallback also fails
    (Ollama unreachable from a cloud deployment, by design), the
    Ollama connection error used to silently replace the Gemini
    failure in the final exception message - hiding the actually
    actionable reason (quota exhausted) behind a generic "Ollama
    unreachable" message that's true everywhere on Render, always,
    and tells you nothing about what specifically went wrong today.
    """

    def raise_quota_error(path):
        raise RuntimeError(
            "429 RESOURCE_EXHAUSTED. Quota exceeded for metric: "
            "generate_content_free_tier_requests"
        )

    def raise_connection_error(path):
        raise RuntimeError("Failed to connect to Ollama.")

    monkeypatch.setattr(
        hybrid_router_module.gemini_service,
        "extract_receipt",
        raise_quota_error,
    )

    monkeypatch.setattr(
        hybrid_router_module.ollama_service,
        "extract_receipt",
        raise_connection_error,
    )

    try:
        hybrid_router_module.hybrid_router.route(
            "dummy.jpg",
            is_sensitive=False,
        )
        assert False, "expected route() to raise when both engines fail"
    except Exception as ex:
        message = str(ex)
        # The router recognises the rate-limit marker in the raw
        # Gemini exception and rewrites it into this friendlier,
        # still-actionable reason - that's what must survive, not
        # the raw "RESOURCE_EXHAUSTED" string.
        assert "quota" in message.lower()
        assert "ollama" in message.lower()

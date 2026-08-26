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

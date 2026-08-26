"""
Expense Pipeline Utility Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

Regression test for a real failure hit while seeding demo data: an
AI-extracted expense_date with a non-midnight time component
(e.g. "2007-03-12T14:22:00") crashed AIAnalysisCreate with Pydantic's
date_from_datetime_inexact error.
"""

from app.langchain.expense_pipeline import _normalize_date


def test_plain_date_passes_through():
    assert _normalize_date("2026-08-01") == "2026-08-01"


def test_datetime_with_time_component_is_trimmed():
    assert _normalize_date("2007-03-12T14:22:00") == "2007-03-12"


def test_datetime_with_space_separator_is_trimmed():
    assert _normalize_date("2007-03-12 14:22:00") == "2007-03-12"


def test_none_passes_through():
    assert _normalize_date(None) is None


def test_empty_string_becomes_none():
    assert _normalize_date("") is None


def test_non_string_value_passes_through():
    assert _normalize_date(12345) == 12345

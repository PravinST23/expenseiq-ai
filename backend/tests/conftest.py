"""
Pytest Configuration

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    FastAPI Test Client.
    """

    return TestClient(app)
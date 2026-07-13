"""
SQLAlchemy Declarative Base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models
import app.models  # noqa: F401,E402
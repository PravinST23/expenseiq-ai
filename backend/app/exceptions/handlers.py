"""
Global Exception Handlers

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.core import ApiResponse


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):

        return ApiResponse.error(
            message="Validation Failed",
            status_code=422,
            errors=exc.errors(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):

        return ApiResponse.error(
            message=exc.detail,
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(
        request: Request,
        exc: Exception,
    ):

        return ApiResponse.error(
            message="Internal Server Error",
            status_code=500,
        )
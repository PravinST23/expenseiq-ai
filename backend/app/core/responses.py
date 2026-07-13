"""
Standard API Responses

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from typing import Any

from fastapi.responses import JSONResponse


class ApiResponse:

    @staticmethod
    def success(
        message: str,
        data: Any = None,
        status_code: int = 200,
    ):

        return JSONResponse(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "data": data,
            },
        )

    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
        errors: Any = None,
    ):

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "errors": errors,
            },
        )
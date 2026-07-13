"""
Main API Router

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import APIRouter

from app.api.v1.employee import router as employee_router
from app.api.v1.project import router as project_router
from app.api.v1.expense import router as expense_router
from app.api.v1.receipt import router as receipt_router
from app.api.v1.approval import router as approval_router

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(employee_router)
api_router.include_router(project_router)
api_router.include_router(expense_router)
api_router.include_router(receipt_router)
api_router.include_router(approval_router)
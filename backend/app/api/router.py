"""
Main API Router

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.employee import router as employee_router
from app.api.v1.project import router as project_router
from app.api.v1.expense import router as expense_router
from app.api.v1.receipt import router as receipt_router
from app.api.v1.approval import router as approval_router
from app.api.v1.ai_analysis import router as ai_analysis_router
from app.api.v1.compliance_check import router as compliance_check_router
from app.api.v1.duplicate_check import router as duplicate_check_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(auth_router)
api_router.include_router(employee_router)
api_router.include_router(project_router)
api_router.include_router(expense_router)
api_router.include_router(receipt_router)
api_router.include_router(approval_router)
api_router.include_router(ai_analysis_router)
api_router.include_router(compliance_check_router)
api_router.include_router(duplicate_check_router)
api_router.include_router(analytics_router)
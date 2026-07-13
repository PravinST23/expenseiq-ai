"""
ExpenseIQ Backend Application

Author: Pravin Shanmugavel
Project: AI Powered Expense Management System
"""

from fastapi import FastAPI

from app.api.router import api_router
from app.config.settings import settings
from app.exceptions.handlers import register_exception_handlers

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register Global Exception Handlers
register_exception_handlers(app)

# Register API Routes
app.include_router(api_router)


@app.get(
    "/",
    tags=["Home"],
    summary="Application Information",
)
def home():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
        "message": "Welcome to ExpenseIQ Backend API",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
)
def health():

    return {
        "status": "Healthy",
        "message": "Application is running successfully.",
    }
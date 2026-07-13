from fastapi import APIRouter

router = APIRouter(
    tags=["Health"]
)

@router.get("/")
async def home():
    return {
        "application": "ExpenseIQ",
        "version": "1.0.0",
        "status": "Running",
        "message": "Welcome to ExpenseIQ Backend API"
    }

@router.get("/health")
async def health():
    return {
        "status": "Healthy"
    }
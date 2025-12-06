"""
Authentication API router
"""
from fastapi import APIRouter

# Create placeholder router
auth_router = APIRouter()

@auth_router.get("/status")
async def auth_status():
    """Authentication status endpoint"""
    return {"status": "Authentication module loaded"}
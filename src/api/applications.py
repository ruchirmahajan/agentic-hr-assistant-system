"""
Applications API router placeholder
"""
from fastapi import APIRouter

applications_router = APIRouter()

@applications_router.get("/")
async def list_applications():
    """List applications endpoint"""
    return {"message": "Applications endpoint - coming soon"}
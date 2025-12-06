"""
Jobs API router placeholder
"""
from fastapi import APIRouter

jobs_router = APIRouter()

@jobs_router.get("/")
async def list_jobs():
    """List jobs endpoint"""
    return {"message": "Jobs endpoint - coming soon"}
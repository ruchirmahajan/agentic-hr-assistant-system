"""
Dashboard API router placeholder
"""
from fastapi import APIRouter

dashboard_router = APIRouter()

@dashboard_router.get("/metrics")
async def get_metrics():
    """Dashboard metrics endpoint"""
    return {"message": "Dashboard endpoint - coming soon"}
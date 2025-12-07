"""
Dashboard API router with AI status
"""
from fastapi import APIRouter
from ..services import claude_service

dashboard_router = APIRouter()

@dashboard_router.get("/metrics")
async def get_metrics():
    """Dashboard metrics endpoint"""
    return {"message": "Dashboard endpoint - coming soon"}


@dashboard_router.get("/ai-status")
async def get_ai_status():
    """
    Get AI service status.
    
    Returns information about which AI provider is active (Ollama or rule-based),
    available models, and service health.
    """
    try:
        status = await claude_service.get_ai_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "provider": "rule-based",
                "status": "fallback-mode"
            }
        }
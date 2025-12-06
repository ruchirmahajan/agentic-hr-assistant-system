"""
Main FastAPI application entry point
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from .core.config import settings
from .core.database import init_db, close_db
from .core.exceptions import HRAssistantException
from .api.auth import auth_router
from .api.candidates import candidates_router
from .api.jobs import jobs_router
from .api.applications import applications_router
from .api.dashboard import dashboard_router
from .api.demo import demo_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting HR Assistant application...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down HR Assistant application...")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered HR Assistant with GDPR compliance",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Allow all hosts for demo
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"({process_time:.3f}s)"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(HRAssistantException)
async def hr_exception_handler(request: Request, exc: HRAssistantException):
    """Handle custom HR Assistant exceptions"""
    logger.error(f"HR Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": exc.__class__.__name__}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include API routers
app.include_router(
    auth_router,
    prefix=f"{settings.API_PREFIX}/auth",
    tags=["authentication"]
)

app.include_router(
    candidates_router,
    prefix=f"{settings.API_PREFIX}/candidates",
    tags=["candidates"]
)

app.include_router(
    jobs_router,
    prefix=f"{settings.API_PREFIX}/jobs",
    tags=["jobs"]
)

app.include_router(
    applications_router,
    prefix=f"{settings.API_PREFIX}/applications",
    tags=["applications"]
)

app.include_router(
    dashboard_router,
    prefix=f"{settings.API_PREFIX}/dashboard",
    tags=["dashboard"]
)

# Demo router for testing without auth
app.include_router(
    demo_router,
    prefix=f"{settings.API_PREFIX}/demo",
    tags=["demo"]
)


# Login route
@app.get("/login")
async def login():
    """Serve the login HTML file"""
    login_path = Path(__file__).parent.parent / "login.html"
    return FileResponse(login_path)

# Dashboard route - serve the main dashboard HTML
@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard HTML file"""
    dashboard_path = Path(__file__).parent.parent / "dashboard.html"
    return FileResponse(dashboard_path)

# Serve dashboard JavaScript
@app.get("/dashboard.js")
async def dashboard_js():
    """Serve the dashboard JavaScript file"""
    js_path = Path(__file__).parent.parent / "dashboard.js"
    return FileResponse(js_path, media_type="application/javascript")

# Root endpoint - redirect to dashboard
@app.get("/")
async def root():
    """Redirect to dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
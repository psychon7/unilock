from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger
from pathlib import Path
from app.routes import domains
from app.core.dependencies import admin_required
from app.core.settings import settings

# Initialize the FastAPI application
app = FastAPI(
    title="Unilock Identity Platform",
    description="Simplified Keycloak management interface",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logger.add("logs/app.log", rotation="500 MB", retention="10 days")

# Create static directories if they don't exist
static_dir = Path("static")
logos_dir = static_dir / "logos"
logos_dir.mkdir(parents=True, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include all routers
from app.routes import auth

# Auth routes don't require authentication
app.include_router(auth.router)

# Protected routes
app.include_router(
    domains.router,
    dependencies=[Depends(admin_required)],
    prefix="/api/v1"
)

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "ok", "version": app.version}

@app.get("/secure-test")
async def secure_test(current_user=Depends(admin_required)):
    """Test endpoint for admin access"""
    return {"message": "Admin access granted", "user": current_user.username}

if __name__ == "__main__":
    # Run with auto-reload for development
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

from fastapi import APIRouter
from app.api.v1 import auth, music

# Create main API router
api_router = APIRouter()

@api_router.get("/")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Music Atlas API v1",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/auth/*",
            "music": "/music/*",
            "recommendations": "/recommendations/*",
            "search": "/search/*"
        }
    }

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(music.router, prefix="/music", tags=["music"])

# TODO: Include other routers when implemented
# api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
# api_router.include_router(search_router, prefix="/search", tags=["search"])

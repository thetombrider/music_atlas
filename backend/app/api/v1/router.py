from fastapi import APIRouter

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
            "users": "/users/*",
            "music": "/music/*",
            "recommendations": "/recommendations/*",
            "search": "/search/*"
        }
    }

# TODO: Include specific routers when implemented
# api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(music_router, prefix="/music", tags=["music"])
# api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
# api_router.include_router(search_router, prefix="/search", tags=["search"])

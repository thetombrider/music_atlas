from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Music Atlas API - Backend Only",
    description="Backend puro per testare Spotify + Neo4j",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.on_event("startup")
async def startup_event():
    """Startup senza Neo4j per ora"""
    logger.info("🚀 Music Atlas API started - Backend only mode")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Music Atlas API shutdown")

# Configure CORS minimo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissivo per testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Music Atlas API - Backend Only", 
        "version": "1.0.0",
        "mode": "testing",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "spotify_login": "/api/v1/auth/spotify/login",
            "spotify_callback": "/api/v1/auth/spotify/callback"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "music-atlas-api", "mode": "backend-only"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

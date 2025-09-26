from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.database.connection import neo4j_db
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Music Atlas API",
    description="Knowledge Graph API for music discovery and recommendations",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        neo4j_db.connect()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Failed to initialize database connection: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    try:
        neo4j_db.close()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Music Atlas API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "music-atlas-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )

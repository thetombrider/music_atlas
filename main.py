import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.main import app
except ImportError:
    # If backend import fails, create a minimal app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="Music Atlas API", version="1.0.0")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Music Atlas API is running", "version": "1.0.0"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "music-atlas-api"}

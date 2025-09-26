from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Neo4j Database
    NEO4J_URI: str = "neo4j+s://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = 100
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: int = 60
    
    # Spotify API
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REDIRECT_URI: str = "http://localhost:3000/callback"
    SPOTIFY_API_TIMEOUT: int = 10
    
    # External APIs
    WIKIPEDIA_USER_AGENT: str = "MusicAtlas/1.0"
    WIKIPEDIA_BASE_URL: str = "https://en.wikipedia.org/api/rest_v1"
    
    MUSICBRAINZ_USER_AGENT: str = "MusicAtlas/1.0"
    MUSICBRAINZ_BASE_URL: str = "https://musicbrainz.org/ws/2"
    
    SETLISTFM_API_KEY: str = ""
    SETLISTFM_BASE_URL: str = "https://api.setlist.fm/rest/1.0"
    
    TMDB_API_KEY: str = ""
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    
    BANDSINTOWN_API_KEY: str = ""
    BANDSINTOWN_BASE_URL: str = "https://rest.bandsintown.com"
    
    # Caching
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 3600
    
    # Performance
    API_TIMEOUT_SECONDS: int = 30
    EXTERNAL_API_TIMEOUT: int = 15
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create global settings instance
settings = Settings()

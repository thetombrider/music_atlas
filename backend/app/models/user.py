from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base model per utente"""
    spotify_user_id: str
    nome_utente: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    """Model per creazione utente"""
    pass

class UserUpdate(BaseModel):
    """Model per aggiornamento utente"""
    nome_utente: Optional[str] = None
    email: Optional[str] = None

class User(UserBase):
    """Model completo utente"""
    ultima_sincronizzazione: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SpotifyTokens(BaseModel):
    """Model per i token Spotify"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    scope: Optional[str] = None

class SpotifyAuthCallback(BaseModel):
    """Model per callback OAuth Spotify"""
    code: str
    state: Optional[str] = None

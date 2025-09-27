from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.auth.jwt_handler import jwt_handler
from app.models.user import User

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency per ottenere l'utente corrente dal JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt_handler.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        return payload
        
    except Exception:
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency per ottenere l'utente corrente attivo"""
    # Qui potresti aggiungere controlli aggiuntivi come user.is_active
    return current_user

# Dependency opzionale per endpoint che possono funzionare sia con che senza autenticazione
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """Dependency opzionale per l'utente corrente"""
    if credentials is None:
        return None
    
    try:
        payload = jwt_handler.verify_token(credentials.credentials)
        return payload
    except Exception:
        return None

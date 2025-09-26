from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import logging
from datetime import datetime

from app.external.spotify_client import spotify_client
from app.auth.jwt_handler import jwt_handler
from app.auth.middleware import get_current_user, get_current_active_user
from app.models.user import SpotifyAuthCallback, SpotifyTokens, User

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage per demo - in produzione usare Redis o database
auth_states = {}
user_tokens = {}  # spotify_user_id -> tokens

@router.get("/spotify/login")
async def spotify_login():
    """Inizia il flusso OAuth2 con Spotify"""
    try:
        # Genera state token per sicurezza
        state = jwt_handler.create_state_token()
        
        # Salva state (in produzione usare Redis con TTL)
        auth_states[state] = {
            "created_at": datetime.utcnow(),
            "used": False
        }
        
        # Ottieni URL di autorizzazione
        auth_url = spotify_client.get_authorization_url(state=state)
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
        
    except Exception as e:
        logger.error(f"Error in spotify_login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Spotify authorization URL"
        )

@router.post("/spotify/callback")
async def spotify_callback(callback_data: SpotifyAuthCallback):
    """Gestisce il callback OAuth2 da Spotify"""
    try:
        # Verifica state token
        if callback_data.state and callback_data.state in auth_states:
            state_data = auth_states[callback_data.state]
            if state_data["used"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="State token already used"
                )
            # Marca come usato
            auth_states[callback_data.state]["used"] = True
        else:
            logger.warning("Invalid or missing state token in callback")
        
        # Scambia codice con token
        tokens = await spotify_client.exchange_code_for_token(callback_data.code)
        
        # Ottieni profilo utente
        user_profile = await spotify_client.get_user_profile(tokens["access_token"])
        
        spotify_user_id = user_profile["id"]
        
        # Salva tokens (in produzione salvare in database criptati)
        user_tokens[spotify_user_id] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": datetime.utcnow().timestamp() + tokens["expires_in"],
            "user_profile": user_profile
        }
        
        # Crea JWT token per l'applicazione
        jwt_payload = {
            "sub": spotify_user_id,  # Subject (user ID)
            "spotify_user_id": spotify_user_id,
            "user_name": user_profile.get("display_name"),
            "email": user_profile.get("email"),
            "type": "access_token"
        }
        
        access_token = jwt_handler.create_access_token(jwt_payload)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "spotify_user_id": spotify_user_id,
            "user_profile": {
                "id": user_profile["id"],
                "display_name": user_profile.get("display_name"),
                "email": user_profile.get("email"),
                "images": user_profile.get("images", []),
                "followers": user_profile.get("followers", {}).get("total", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in spotify_callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process Spotify callback: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Ottiene informazioni sull'utente corrente"""
    try:
        spotify_user_id = current_user["spotify_user_id"]
        
        # Ottieni tokens salvati
        if spotify_user_id not in user_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Spotify tokens not found. Please re-authenticate."
            )
        
        user_data = user_tokens[spotify_user_id]
        
        # Controlla se il token è ancora valido
        if datetime.utcnow().timestamp() > user_data["expires_at"]:
            # Token scaduto, prova a rinnovarlo
            try:
                new_tokens = await spotify_client.refresh_access_token(user_data["refresh_token"])
                user_data["access_token"] = new_tokens["access_token"]
                user_data["expires_at"] = datetime.utcnow().timestamp() + new_tokens["expires_in"]
                
                if "refresh_token" in new_tokens:
                    user_data["refresh_token"] = new_tokens["refresh_token"]
                    
            except Exception as e:
                logger.error(f"Failed to refresh token for user {spotify_user_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired and refresh failed. Please re-authenticate."
                )
        
        return {
            "spotify_user_id": spotify_user_id,
            "user_profile": user_data["user_profile"],
            "token_valid": True,
            "expires_at": user_data["expires_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user_info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_active_user)):
    """Rinnova il token Spotify dell'utente"""
    try:
        spotify_user_id = current_user["spotify_user_id"]
        
        if spotify_user_id not in user_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tokens not found"
            )
        
        user_data = user_tokens[spotify_user_id]
        
        # Rinnova token
        new_tokens = await spotify_client.refresh_access_token(user_data["refresh_token"])
        
        # Aggiorna tokens salvati
        user_data["access_token"] = new_tokens["access_token"]
        user_data["expires_at"] = datetime.utcnow().timestamp() + new_tokens["expires_in"]
        
        if "refresh_token" in new_tokens:
            user_data["refresh_token"] = new_tokens["refresh_token"]
        
        return {
            "message": "Token refreshed successfully",
            "expires_at": user_data["expires_at"]
        }
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh token: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_active_user)):
    """Logout dell'utente (rimuove tokens)"""
    try:
        spotify_user_id = current_user["spotify_user_id"]
        
        # Rimuovi tokens (in produzione cancellare dal database)
        if spotify_user_id in user_tokens:
            del user_tokens[spotify_user_id]
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )

# Utility function per ottenere il token Spotify valido
async def get_valid_spotify_token(current_user: dict = Depends(get_current_active_user)) -> str:
    """Dependency per ottenere un token Spotify valido"""
    spotify_user_id = current_user["spotify_user_id"]
    
    if spotify_user_id not in user_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify tokens not found. Please re-authenticate."
        )
    
    user_data = user_tokens[spotify_user_id]
    
    # Controlla se il token è scaduto
    if datetime.utcnow().timestamp() > user_data["expires_at"]:
        # Token scaduto, prova a rinnovarlo
        try:
            new_tokens = await spotify_client.refresh_access_token(user_data["refresh_token"])
            user_data["access_token"] = new_tokens["access_token"]
            user_data["expires_at"] = datetime.utcnow().timestamp() + new_tokens["expires_in"]
            
            if "refresh_token" in new_tokens:
                user_data["refresh_token"] = new_tokens["refresh_token"]
                
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired and refresh failed. Please re-authenticate."
            )
    
    return user_data["access_token"]

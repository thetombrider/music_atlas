from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import Dict, Any
import logging

from app.auth.middleware import get_current_active_user
from app.api.v1.auth import get_valid_spotify_token
from app.services.spotify_service import spotify_ingestion_service
from app.external.spotify_client import spotify_client

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/import")
async def import_user_data(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_active_user),
    spotify_token: str = Depends(get_valid_spotify_token)
):
    """Importa i dati dell'utente da Spotify nel knowledge graph"""
    try:
        spotify_user_id = current_user["spotify_user_id"]
        
        # Avvia import in background
        background_tasks.add_task(
            _background_import_task,
            spotify_user_id,
            spotify_token
        )
        
        return {
            "message": "Import started in background",
            "spotify_user_id": spotify_user_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error starting import: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start import: {str(e)}"
        )

@router.get("/top-artists")
async def get_user_top_artists(
    time_range: str = "medium_term",
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user),
    spotify_token: str = Depends(get_valid_spotify_token)
):
    """Ottiene i top artists dell'utente da Spotify"""
    try:
        if time_range not in ["short_term", "medium_term", "long_term"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="time_range must be one of: short_term, medium_term, long_term"
            )
        
        if limit > 50:
            limit = 50
        
        top_artists = await spotify_client.get_user_top_artists(
            spotify_token, 
            time_range=time_range, 
            limit=limit
        )
        
        return {
            "time_range": time_range,
            "total": top_artists.get("total", 0),
            "limit": limit,
            "artists": top_artists.get("items", [])
        }
        
    except Exception as e:
        logger.error(f"Error getting top artists: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top artists: {str(e)}"
        )

@router.get("/top-tracks")
async def get_user_top_tracks(
    time_range: str = "medium_term",
    limit: int = 20,
    current_user: dict = Depends(get_current_active_user),
    spotify_token: str = Depends(get_valid_spotify_token)
):
    """Ottiene i top tracks dell'utente da Spotify"""
    try:
        if time_range not in ["short_term", "medium_term", "long_term"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="time_range must be one of: short_term, medium_term, long_term"
            )
        
        if limit > 50:
            limit = 50
        
        top_tracks = await spotify_client.get_user_top_tracks(
            spotify_token,
            time_range=time_range,
            limit=limit
        )
        
        return {
            "time_range": time_range,
            "total": top_tracks.get("total", 0),
            "limit": limit,
            "tracks": top_tracks.get("items", [])
        }
        
    except Exception as e:
        logger.error(f"Error getting top tracks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top tracks: {str(e)}"
        )

@router.get("/profile")
async def get_spotify_profile(
    current_user: dict = Depends(get_current_active_user),
    spotify_token: str = Depends(get_valid_spotify_token)
):
    """Ottiene il profilo Spotify dell'utente"""
    try:
        profile = await spotify_client.get_user_profile(spotify_token)
        
        return {
            "spotify_profile": profile
        }
        
    except Exception as e:
        logger.error(f"Error getting Spotify profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Spotify profile: {str(e)}"
        )

@router.get("/import-status")
async def get_import_status(
    current_user: dict = Depends(get_current_active_user)
):
    """Ottiene lo stato dell'import dell'utente dal knowledge graph"""
    try:
        spotify_user_id = current_user["spotify_user_id"]
        
        # Query per ottenere statistiche utente dal grafo
        query = """
        MATCH (u:Utente {spotify_user_id: $spotify_user_id})
        OPTIONAL MATCH (u)-[:ASCOLTA]->(t:Brano)
        OPTIONAL MATCH (u)-[:ASCOLTA]->(:Brano)<-[:CONTIENE]-(al:Album)
        OPTIONAL MATCH (u)-[:ASCOLTA]->(:Brano)<-[:ESEGUE]-(a:Artista)
        
        RETURN u.ultima_sincronizzazione as last_sync,
               u.nome_utente as username,
               u.email as email,
               count(DISTINCT t) as tracks_count,
               count(DISTINCT al) as albums_count,
               count(DISTINCT a) as artists_count
        """
        
        from app.database.connection import neo4j_db
        result = neo4j_db.execute_query(query, {"spotify_user_id": spotify_user_id})
        
        if not result:
            return {
                "user_exists": False,
                "message": "User not found in knowledge graph. Run import first."
            }
        
        data = result[0]
        
        return {
            "user_exists": True,
            "spotify_user_id": spotify_user_id,
            "username": data["username"],
            "email": data["email"],
            "last_sync": data["last_sync"],
            "statistics": {
                "tracks_in_graph": data["tracks_count"],
                "albums_in_graph": data["albums_count"],
                "artists_in_graph": data["artists_count"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting import status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get import status: {str(e)}"
        )

async def _background_import_task(spotify_user_id: str, spotify_token: str):
    """Task in background per l'import dei dati"""
    try:
        logger.info(f"Starting background import for user {spotify_user_id}")
        
        result = await spotify_ingestion_service.import_user_data(
            spotify_user_id, 
            spotify_token
        )
        
        logger.info(f"Background import completed for user {spotify_user_id}: {result}")
        
    except Exception as e:
        logger.error(f"Background import failed for user {spotify_user_id}: {str(e)}")

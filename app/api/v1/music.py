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
    """Ottiene i top artists dell'utente dal database Neo4j o da Spotify se non disponibili"""
    try:
        if time_range not in ["short_term", "medium_term", "long_term"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="time_range must be one of: short_term, medium_term, long_term"
            )
        
        if limit > 50:
            limit = 50
        
        spotify_user_id = current_user["spotify_user_id"]
        
        # Prima prova a leggere dal database Neo4j
        from app.database.connection import neo4j_db
        
        query = """
        MATCH (u:Utente {spotify_user_id: $spotify_user_id})
        -[r:ASCOLTA {time_range: $time_range}]->
        (:Brano)<-[:ESEGUE]-(a:Artista)
        RETURN DISTINCT a.nome as name, a.spotify_id as id, a.popolarita as popularity,
               a.followers as followers, a.immagini as images, a.external_urls as external_urls
        ORDER BY a.popolarita DESC
        LIMIT $limit
        """
        
        db_artists = neo4j_db.execute_query(query, {
            "spotify_user_id": spotify_user_id,
            "time_range": time_range,
            "limit": limit
        })
        
        if db_artists:
            # Formatta i dati dal database nel formato Spotify API
            artists_items = []
            for record in db_artists:
                artists_items.append({
                    "id": record["id"],
                    "name": record["name"],
                    "popularity": record["popularity"],
                    "followers": {"total": record["followers"]} if record["followers"] else {"total": 0},
                    "images": [{"url": url} for url in (record["images"] or [])],
                    "external_urls": record["external_urls"] or {}
                })
            
            return {
                "time_range": time_range,
                "total": len(artists_items),
                "limit": limit,
                "artists": artists_items,
                "source": "database"
            }
        
        # Se non ci sono dati nel database, usa Spotify API
        top_artists = await spotify_client.get_user_top_artists(
            spotify_token, 
            time_range=time_range, 
            limit=limit
        )
        
        return {
            "time_range": time_range,
            "total": top_artists.get("total", 0),
            "limit": limit,
            "artists": top_artists.get("items", []),
            "source": "spotify_api"
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
    """Ottiene i top tracks dell'utente dal database Neo4j o da Spotify se non disponibili"""
    try:
        if time_range not in ["short_term", "medium_term", "long_term"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="time_range must be one of: short_term, medium_term, long_term"
            )
        
        if limit > 50:
            limit = 50
            
        spotify_user_id = current_user["spotify_user_id"]
        
        # Prima prova a leggere dal database Neo4j
        from app.database.connection import neo4j_db
        
        query = """
        MATCH (u:Utente {spotify_user_id: $spotify_user_id})
        -[r:ASCOLTA {time_range: $time_range}]->(t:Brano)
        OPTIONAL MATCH (t)<-[:CONTIENE]-(al:Album)
        OPTIONAL MATCH (t)<-[:ESEGUE]-(ar:Artista)
        RETURN t.nome as name, t.spotify_id as id, t.popolarita as popularity,
               t.durata_ms as duration_ms, t.preview_url as preview_url,
               t.external_urls as external_urls,
               al.nome as album_name, al.spotify_id as album_id, al.immagini as album_images,
               collect(DISTINCT ar.nome) as artist_names, collect(DISTINCT ar.spotify_id) as artist_ids
        ORDER BY t.popolarita DESC
        LIMIT $limit
        """
        
        db_tracks = neo4j_db.execute_query(query, {
            "spotify_user_id": spotify_user_id,
            "time_range": time_range,
            "limit": limit
        })
        
        if db_tracks:
            # Formatta i dati dal database nel formato Spotify API
            tracks_items = []
            for record in db_tracks:
                # Costruisci l'oggetto artisti
                artists = []
                if record["artist_names"] and record["artist_ids"]:
                    for i, name in enumerate(record["artist_names"]):
                        if i < len(record["artist_ids"]):
                            artists.append({
                                "id": record["artist_ids"][i],
                                "name": name
                            })
                
                # Costruisci l'oggetto album
                album = None
                if record["album_name"]:
                    album = {
                        "id": record["album_id"],
                        "name": record["album_name"],
                        "images": [{"url": url} for url in (record["album_images"] or [])]
                    }
                
                tracks_items.append({
                    "id": record["id"],
                    "name": record["name"],
                    "popularity": record["popularity"],
                    "duration_ms": record["duration_ms"],
                    "preview_url": record["preview_url"],
                    "external_urls": record["external_urls"] or {},
                    "artists": artists,
                    "album": album
                })
            
            return {
                "time_range": time_range,
                "total": len(tracks_items),
                "limit": limit,
                "tracks": tracks_items,
                "source": "database"
            }
        
        # Se non ci sono dati nel database, usa Spotify API
        top_tracks = await spotify_client.get_user_top_tracks(
            spotify_token,
            time_range=time_range,
            limit=limit
        )
        
        return {
            "time_range": time_range,
            "total": top_tracks.get("total", 0),
            "limit": limit,
            "tracks": top_tracks.get("items", []),
            "source": "spotify_api"
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
        logger.info(f"🚀 Starting background import for user {spotify_user_id}")
        
        result = await spotify_ingestion_service.import_user_data(
            spotify_user_id, 
            spotify_token
        )
        
        logger.info(f"✅ Background import completed for user {spotify_user_id}")
        logger.info(f"📊 Import results: {result}")
        
        # Stampa anche sulla console per debug
        print(f"✅ Import completed for {spotify_user_id}: {result}")
        
    except Exception as e:
        logger.error(f"❌ Background import failed for user {spotify_user_id}: {str(e)}")
        print(f"❌ Import failed for {spotify_user_id}: {str(e)}")
        raise

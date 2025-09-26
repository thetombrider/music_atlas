from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.database.connection import neo4j_db
from app.external.spotify_client import spotify_client
from app.models.music import Artist, Album, Track

logger = logging.getLogger(__name__)

class SpotifyIngestionService:
    """Servizio per l'ingestion dei dati Spotify nel knowledge graph"""
    
    def __init__(self):
        self.db = neo4j_db
    
    async def import_user_data(self, spotify_user_id: str, access_token: str) -> Dict[str, Any]:
        """Importa i dati dell'utente da Spotify nel knowledge graph"""
        try:
            logger.info(f"🔄 Starting import_user_data for {spotify_user_id}")
            results = {
                "user_created": False,
                "artists_imported": 0,
                "albums_imported": 0,
                "tracks_imported": 0,
                "relationships_created": 0
            }
            
            # 1. Crea o aggiorna nodo Utente
            logger.info(f"👤 Getting user profile for {spotify_user_id}")
            user_profile = await spotify_client.get_user_profile(access_token)
            logger.info(f"👤 Creating/updating user node for {spotify_user_id}")
            results["user_created"] = self._create_or_update_user(spotify_user_id, user_profile)
            logger.info(f"👤 User created/updated: {results['user_created']}")
            
            # 2. Importa top artists (short, medium, long term)
            logger.info(f"🎵 Starting artists import for {spotify_user_id}")
            for time_range in ["short_term", "medium_term", "long_term"]:
                logger.info(f"🎵 Getting top artists for {time_range}")
                top_artists = await spotify_client.get_user_top_artists(
                    access_token, time_range=time_range, limit=50
                )
                artist_count = len(top_artists.get("items", []))
                logger.info(f"🎵 Found {artist_count} artists for {time_range}")
                for artist_data in top_artists.get("items", []):
                    self._create_or_update_artist(artist_data)
                    results["artists_imported"] += 1
            logger.info(f"🎵 Total artists imported: {results['artists_imported']}")
            
            # 3. Importa top tracks (short, medium, long term)
            logger.info(f"🎵 Starting tracks import for {spotify_user_id}")
            for time_range in ["short_term", "medium_term", "long_term"]:
                logger.info(f"🎵 Getting top tracks for {time_range}")
                top_tracks = await spotify_client.get_user_top_tracks(
                    access_token, time_range=time_range, limit=50
                )
                track_count = len(top_tracks.get("items", []))
                logger.info(f"🎵 Found {track_count} tracks for {time_range}")
                
                for track_data in top_tracks.get("items", []):
                    # Importa track, album e artisti
                    track_result = await self._import_track_with_relations(track_data, access_token)
                    results["tracks_imported"] += track_result["tracks"]
                    results["albums_imported"] += track_result["albums"]
                    results["artists_imported"] += track_result["artists"]
                    
                    # Crea relazione ASCOLTA
                    self._create_user_listens_relationship(
                        spotify_user_id, 
                        track_data["id"],
                        time_range
                    )
                    results["relationships_created"] += 1
                    
            logger.info(f"🎵 Total tracks imported: {results['tracks_imported']}")
            logger.info(f"🎵 Total albums imported: {results['albums_imported']}")
            logger.info(f"🎵 Total relationships created: {results['relationships_created']}")
            
            # 4. Aggiorna timestamp ultima sincronizzazione
            logger.info(f"⏰ Updating last sync timestamp for {spotify_user_id}")
            self._update_user_last_sync(spotify_user_id)
            
            logger.info(f"Import completed for user {spotify_user_id}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error importing user data for {spotify_user_id}: {str(e)}")
            raise
    
    def _create_or_update_user(self, spotify_user_id: str, user_profile: Dict) -> bool:
        """Crea o aggiorna un nodo Utente"""
        query = """
        MERGE (u:Utente {spotify_user_id: $spotify_user_id})
        SET u.nome_utente = $nome_utente,
            u.email = $email,
            u.followers = $followers,
            u.paese = $paese,
            u.immagini = $immagini,
            u.aggiornato_il = datetime()
        RETURN u.spotify_user_id as user_id, 
               CASE WHEN u.creato_il IS NULL THEN true ELSE false END as created
        """
        
        parameters = {
            "spotify_user_id": spotify_user_id,
            "nome_utente": user_profile.get("display_name"),
            "email": user_profile.get("email"),
            "followers": user_profile.get("followers", {}).get("total", 0),
            "paese": user_profile.get("country"),
            "immagini": [img["url"] for img in user_profile.get("images", [])]
        }
        
        result = self.db.execute_write_query(query, parameters)
        return result[0]["created"] if result else False
    
    def _create_or_update_artist(self, artist_data: Dict) -> Dict[str, Any]:
        """Crea o aggiorna un nodo Artista"""
        query = """
        MERGE (a:Artista {spotify_id: $spotify_id})
        SET a.nome = $nome,
            a.popolarita = $popolarita,
            a.followers = $followers,
            a.immagini = $immagini,
            a.external_urls = $external_urls,
            a.aggiornato_il = datetime()
        WITH a
        
        // Gestisci generi
        UNWIND $generi as genere_nome
        MERGE (g:Genere {nome: genere_nome})
        MERGE (a)-[:DI_GENERE]->(g)
        
        RETURN a.spotify_id as artist_id, count(g) as genres_linked
        """
        
        parameters = {
            "spotify_id": artist_data["id"],
            "nome": artist_data["name"],
            "popolarita": artist_data.get("popularity"),
            "followers": artist_data.get("followers", {}).get("total", 0),
            "immagini": [img["url"] for img in artist_data.get("images", [])],
            "external_urls": artist_data.get("external_urls", {}),
            "generi": artist_data.get("genres", [])
        }
        
        result = self.db.execute_write_query(query, parameters)
        return result[0] if result else {}
    
    async def _import_track_with_relations(self, track_data: Dict, access_token: str) -> Dict[str, int]:
        """Importa una traccia con tutte le sue relazioni (album, artisti)"""
        results = {"tracks": 0, "albums": 0, "artists": 0}
        
        try:
            # 1. Importa artisti della traccia
            for artist_data in track_data.get("artists", []):
                # Ottieni dettagli completi dell'artista
                full_artist = await spotify_client.get_artist_details(access_token, artist_data["id"])
                self._create_or_update_artist(full_artist)
                results["artists"] += 1
            
            # 2. Importa album se presente
            album_data = track_data.get("album")
            if album_data:
                album_result = await self._import_album_with_relations(album_data, access_token)
                results["albums"] += album_result["albums"]
                results["artists"] += album_result["artists"]
            
            # 3. Importa traccia
            self._create_or_update_track(track_data)
            results["tracks"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error importing track {track_data.get('id', 'unknown')}: {str(e)}")
            return results
    
    async def _import_album_with_relations(self, album_data: Dict, access_token: str) -> Dict[str, int]:
        """Importa un album con le sue relazioni"""
        results = {"albums": 0, "artists": 0}
        
        try:
            # Importa artisti dell'album
            for artist_data in album_data.get("artists", []):
                full_artist = await spotify_client.get_artist_details(access_token, artist_data["id"])
                self._create_or_update_artist(full_artist)
                results["artists"] += 1
            
            # Importa album
            self._create_or_update_album(album_data)
            results["albums"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error importing album {album_data.get('id', 'unknown')}: {str(e)}")
            return results
    
    def _create_or_update_album(self, album_data: Dict) -> Dict[str, Any]:
        """Crea o aggiorna un nodo Album"""
        # Estrai anno dalla data di release
        release_date = album_data.get("release_date", "")
        anno_pubblicazione = None
        if release_date:
            try:
                anno_pubblicazione = int(release_date.split("-")[0])
            except (ValueError, IndexError):
                pass
        
        query = """
        MERGE (al:Album {spotify_id: $spotify_id})
        SET al.titolo = $titolo,
            al.anno_pubblicazione = $anno_pubblicazione,
            al.tipo_album = $tipo_album,
            al.total_tracks = $total_tracks,
            al.immagini = $immagini,
            al.external_urls = $external_urls,
            al.aggiornato_il = datetime()
        WITH al
        
        // Collega artisti all'album
        UNWIND $artist_ids as artist_id
        MATCH (a:Artista {spotify_id: artist_id})
        MERGE (a)-[:PUBBLICATO]->(al)
        
        RETURN al.spotify_id as album_id, count(a) as artists_linked
        """
        
        parameters = {
            "spotify_id": album_data["id"],
            "titolo": album_data["name"],
            "anno_pubblicazione": anno_pubblicazione,
            "tipo_album": album_data.get("album_type"),
            "total_tracks": album_data.get("total_tracks"),
            "immagini": [img["url"] for img in album_data.get("images", [])],
            "external_urls": album_data.get("external_urls", {}),
            "artist_ids": [artist["id"] for artist in album_data.get("artists", [])]
        }
        
        result = self.db.execute_write_query(query, parameters)
        return result[0] if result else {}
    
    def _create_or_update_track(self, track_data: Dict) -> Dict[str, Any]:
        """Crea o aggiorna un nodo Brano"""
        query = """
        MERGE (t:Brano {spotify_id: $spotify_id})
        SET t.titolo = $titolo,
            t.durata_ms = $durata_ms,
            t.numero_traccia = $numero_traccia,
            t.esplicito = $esplicito,
            t.popolarita = $popolarita,
            t.preview_url = $preview_url,
            t.external_urls = $external_urls,
            t.aggiornato_il = datetime()
        WITH t
        
        // Collega al album se presente
        WITH t, $album_id as album_id
        CALL {
            WITH t, album_id
            WITH t, album_id WHERE album_id IS NOT NULL
            MATCH (al:Album {spotify_id: album_id})
            MERGE (al)-[:CONTIENE {numero_traccia: $numero_traccia}]->(t)
            RETURN 1 as album_linked
        }
        
        // Collega artisti
        WITH t
        UNWIND $artist_ids as artist_id
        MATCH (a:Artista {spotify_id: artist_id})
        MERGE (a)-[:ESEGUE]->(t)
        
        RETURN t.spotify_id as track_id, count(a) as artists_linked
        """
        
        parameters = {
            "spotify_id": track_data["id"],
            "titolo": track_data["name"],
            "durata_ms": track_data.get("duration_ms"),
            "numero_traccia": track_data.get("track_number"),
            "esplicito": track_data.get("explicit", False),
            "popolarita": track_data.get("popularity"),
            "preview_url": track_data.get("preview_url"),
            "external_urls": track_data.get("external_urls", {}),
            "album_id": track_data.get("album", {}).get("id"),
            "artist_ids": [artist["id"] for artist in track_data.get("artists", [])]
        }
        
        result = self.db.execute_write_query(query, parameters)
        return result[0] if result else {}
    
    def _create_user_listens_relationship(self, spotify_user_id: str, track_id: str, time_range: str):
        """Crea relazione ASCOLTA tra utente e brano"""
        query = """
        MATCH (u:Utente {spotify_user_id: $spotify_user_id})
        MATCH (t:Brano {spotify_id: $track_id})
        MERGE (u)-[r:ASCOLTA]->(t)
        SET r.time_range = $time_range,
            r.ultimo_ascolto = datetime(),
            r.conteggio = coalesce(r.conteggio, 0) + 1
        RETURN r.conteggio as count
        """
        
        parameters = {
            "spotify_user_id": spotify_user_id,
            "track_id": track_id,
            "time_range": time_range
        }
        
        self.db.execute_write_query(query, parameters)
    
    def _update_user_last_sync(self, spotify_user_id: str):
        """Aggiorna il timestamp dell'ultima sincronizzazione"""
        query = """
        MATCH (u:Utente {spotify_user_id: $spotify_user_id})
        SET u.ultima_sincronizzazione = datetime()
        RETURN u.ultima_sincronizzazione as last_sync
        """
        
        parameters = {"spotify_user_id": spotify_user_id}
        self.db.execute_write_query(query, parameters)

# Istanza globale del servizio
spotify_ingestion_service = SpotifyIngestionService()

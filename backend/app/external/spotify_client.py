import httpx
import asyncio
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SpotifyClient:
    """Client per interagire con le API di Spotify"""
    
    def __init__(self):
        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = settings.SPOTIFY_REDIRECT_URI
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.authorize_url = "https://accounts.spotify.com/authorize"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def get_authorization_url(self, state: str = None) -> str:
        """Genera URL per l'autorizzazione Spotify OAuth2"""
        scopes = [
            "user-read-private",
            "user-read-email", 
            "user-top-read",
            "user-read-recently-played",
            "user-library-read",
            "playlist-read-private",
            "playlist-read-collaborative"
        ]
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "show_dialog": "true"  # Force user to re-approve
        }
        
        if state:
            params["state"] = state
            
        return f"{self.authorize_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Scambia il codice di autorizzazione con un access token"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.auth_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=settings.SPOTIFY_API_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to exchange code for token: {response.status_code}")
                
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Aggiorna l'access token usando il refresh token"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.auth_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=settings.SPOTIFY_API_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to refresh token: {response.status_code}")
                
            return response.json()
    
    async def _make_request(self, 
                           method: str, 
                           endpoint: str, 
                           access_token: str,
                           params: Optional[Dict] = None,
                           data: Optional[Dict] = None) -> Dict[str, Any]:
        """Esegue una richiesta HTTP alle API Spotify con rate limiting"""
        
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last_request)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=settings.SPOTIFY_API_TIMEOUT)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data, timeout=settings.SPOTIFY_API_TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        self.last_request_time = time.time()
        
        if response.status_code == 401:
            raise Exception("Access token expired or invalid")
        elif response.status_code == 429:
            # Rate limited
            retry_after = int(response.headers.get("Retry-After", 1))
            logger.warning(f"Rate limited, waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return await self._make_request(method, endpoint, access_token, params, data)
        elif response.status_code >= 400:
            logger.error(f"Spotify API error: {response.status_code} - {response.text}")
            raise Exception(f"Spotify API error: {response.status_code}")
        
        return response.json()
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Ottiene il profilo dell'utente corrente"""
        return await self._make_request("GET", "/me", access_token)
    
    async def get_user_top_artists(self, 
                                  access_token: str, 
                                  time_range: str = "medium_term",
                                  limit: int = 50) -> Dict[str, Any]:
        """Ottiene i top artists dell'utente
        
        Args:
            time_range: "short_term" (4 weeks), "medium_term" (6 months), "long_term" (years)
            limit: Numero di artisti da recuperare (max 50)
        """
        params = {
            "time_range": time_range,
            "limit": limit
        }
        return await self._make_request("GET", "/me/top/artists", access_token, params=params)
    
    async def get_user_top_tracks(self, 
                                 access_token: str,
                                 time_range: str = "medium_term", 
                                 limit: int = 50) -> Dict[str, Any]:
        """Ottiene i top tracks dell'utente"""
        params = {
            "time_range": time_range,
            "limit": limit
        }
        return await self._make_request("GET", "/me/top/tracks", access_token, params=params)
    
    async def get_artist_albums(self, 
                               access_token: str,
                               artist_id: str, 
                               limit: int = 50) -> Dict[str, Any]:
        """Ottiene gli album di un artista"""
        params = {
            "include_groups": "album,single,compilation",
            "limit": limit,
            "market": "US"  # Default market
        }
        return await self._make_request("GET", f"/artists/{artist_id}/albums", access_token, params=params)
    
    async def get_album_tracks(self, 
                              access_token: str,
                              album_id: str,
                              limit: int = 50) -> Dict[str, Any]:
        """Ottiene le tracce di un album"""
        params = {"limit": limit}
        return await self._make_request("GET", f"/albums/{album_id}/tracks", access_token, params=params)
    
    async def get_artist_details(self, 
                                access_token: str,
                                artist_id: str) -> Dict[str, Any]:
        """Ottiene i dettagli di un artista"""
        return await self._make_request("GET", f"/artists/{artist_id}", access_token)
    
    async def get_album_details(self, 
                               access_token: str,
                               album_id: str) -> Dict[str, Any]:
        """Ottiene i dettagli di un album"""
        return await self._make_request("GET", f"/albums/{album_id}", access_token)
    
    async def search(self, 
                    access_token: str,
                    query: str, 
                    search_type: str = "artist,album,track",
                    limit: int = 20) -> Dict[str, Any]:
        """Cerca artisti, album o tracce"""
        params = {
            "q": query,
            "type": search_type,
            "limit": limit
        }
        return await self._make_request("GET", "/search", access_token, params=params)

# Istanza globale del client
spotify_client = SpotifyClient()

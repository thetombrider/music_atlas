from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SpotifyImage(BaseModel):
    """Model per immagini Spotify"""
    url: str
    height: Optional[int] = None
    width: Optional[int] = None

class SpotifyExternalIds(BaseModel):
    """Model per ID esterni (ISRC, etc.)"""
    isrc: Optional[str] = None
    ean: Optional[str] = None
    upc: Optional[str] = None

class SpotifyExternalUrls(BaseModel):
    """Model per URL esterni"""
    spotify: str

class ArtistBase(BaseModel):
    """Base model per artista"""
    spotify_id: str
    nome: str
    generi_iniziali: List[str] = []
    popolarita: Optional[int] = None

class Artist(ArtistBase):
    """Model completo artista"""
    followers: Optional[int] = None
    images: List[SpotifyImage] = []
    external_urls: Optional[SpotifyExternalUrls] = None
    
class AlbumBase(BaseModel):
    """Base model per album"""
    spotify_id: str
    titolo: str
    anno_pubblicazione: Optional[int] = None
    tipo_album: Optional[str] = None  # album, single, compilation

class Album(AlbumBase):
    """Model completo album"""
    artists: List[Artist] = []
    images: List[SpotifyImage] = []
    external_urls: Optional[SpotifyExternalUrls] = None
    total_tracks: Optional[int] = None
    markets: List[str] = []

class TrackBase(BaseModel):
    """Base model per brano"""
    spotify_id: str
    titolo: str
    durata_ms: Optional[int] = None
    numero_traccia: Optional[int] = None
    esplicito: Optional[bool] = None

class Track(TrackBase):
    """Model completo brano"""
    artists: List[Artist] = []
    album: Optional[Album] = None
    external_urls: Optional[SpotifyExternalUrls] = None
    external_ids: Optional[SpotifyExternalIds] = None
    popolarita: Optional[int] = None
    preview_url: Optional[str] = None
    is_local: Optional[bool] = False

class SpotifyTopItemsResponse(BaseModel):
    """Response per top items da Spotify"""
    items: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int
    href: str
    next: Optional[str] = None
    previous: Optional[str] = None

# Specifiche Tecniche Dettagliate

## Architettura Sistema

### Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   Neo4j AuraDB  │
│                 │◄──►│                 │◄──►│                 │
│ - Dashboard     │    │ - API Routes    │    │ - Knowledge     │
│ - Graph Viz     │    │ - Auth System   │    │   Graph         │
│ - Search        │    │ - Data Ingestion│    │ - Relationships │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │  External APIs  │
         │              │ - Spotify       │
         │              │ - Wikipedia     │
         │              │ - Setlist.fm    │
         └──────────────┤ - TMDb          │
                        │ - Bandsintown   │
                        └─────────────────┘
```

## Backend Architecture (FastAPI)

### Struttura Directory
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── auth/                   # Authentication system
│   │   ├── __init__.py
│   │   ├── spotify_oauth.py    # Spotify OAuth2 implementation
│   │   ├── jwt_handler.py      # JWT token management
│   │   └── middleware.py       # Auth middleware
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py            # User models
│   │   ├── music.py           # Artist, Album, Track models
│   │   ├── graph.py           # Graph relationship models
│   │   └── external.py        # External API response models
│   │
│   ├── database/              # Neo4j database layer
│   │   ├── __init__.py
│   │   ├── connection.py      # Neo4j driver setup
│   │   ├── repositories/      # Repository pattern implementation
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # Base repository class
│   │   │   ├── user.py        # User repository
│   │   │   ├── artist.py      # Artist repository
│   │   │   ├── album.py       # Album repository
│   │   │   └── track.py       # Track repository
│   │   └── queries/           # Cypher queries
│   │       ├── __init__.py
│   │       ├── user_queries.py
│   │       ├── music_queries.py
│   │       └── recommendation_queries.py
│   │
│   ├── services/              # Business logic services
│   │   ├── __init__.py
│   │   ├── spotify_service.py # Spotify API integration
│   │   ├── wikipedia_service.py # Wikipedia API integration
│   │   ├── enrichment_service.py # Data enrichment logic
│   │   ├── recommendation_service.py # Recommendation algorithms
│   │   └── graph_service.py   # Graph operations
│   │
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── users.py       # User management endpoints
│   │   │   ├── music.py       # Music data endpoints
│   │   │   ├── recommendations.py # Recommendation endpoints
│   │   │   └── search.py      # Search endpoints
│   │   └── dependencies.py    # API dependencies
│   │
│   ├── core/                  # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py        # Security utilities
│   │   ├── cache.py           # Caching utilities (Redis)
│   │   └── logging.py         # Logging configuration
│   │
│   └── external/              # External API clients
│       ├── __init__.py
│       ├── spotify_client.py  # Spotify API client
│       ├── wikipedia_client.py # Wikipedia API client
│       ├── musicbrainz_client.py # MusicBrainz API client
│       ├── setlistfm_client.py # Setlist.fm API client
│       └── tmdb_client.py     # TMDb API client
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── test_auth/            # Authentication tests
│   ├── test_services/        # Service tests
│   ├── test_api/             # API endpoint tests
│   └── test_database/        # Database tests
│
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── .env.example             # Environment variables template
└── alembic/                 # Database migrations (if needed)
```

### Dipendenze Principali
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
neo4j==5.15.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
requests==2.31.0
redis==5.0.1
celery==5.3.4  # For background tasks
aiofiles==23.2.1
```

## Frontend Architecture (React + TypeScript)

### Struttura Directory
```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── index.tsx              # App entry point
│   ├── App.tsx                # Main App component
│   │
│   ├── components/            # Reusable components
│   │   ├── common/            # Common UI components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   │
│   │   ├── auth/              # Authentication components
│   │   │   ├── LoginButton.tsx
│   │   │   ├── SpotifyCallback.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   │
│   │   ├── graph/             # Graph visualization components
│   │   │   ├── GraphVisualization.tsx
│   │   │   ├── NodeDetail.tsx
│   │   │   └── GraphControls.tsx
│   │   │
│   │   ├── music/             # Music-related components
│   │   │   ├── ArtistCard.tsx
│   │   │   ├── AlbumCard.tsx
│   │   │   ├── TrackList.tsx
│   │   │   └── RecommendationsList.tsx
│   │   │
│   │   └── search/            # Search components
│   │       ├── SearchBar.tsx
│   │       ├── SearchResults.tsx
│   │       └── SearchFilters.tsx
│   │
│   ├── pages/                 # Page components
│   │   ├── Dashboard.tsx      # Main dashboard
│   │   ├── Artist.tsx         # Artist detail page
│   │   ├── Album.tsx          # Album detail page
│   │   ├── Recommendations.tsx # Recommendations page
│   │   ├── Search.tsx         # Search page
│   │   └── Profile.tsx        # User profile page
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.tsx        # Authentication hook
│   │   ├── useApi.tsx         # API calling hook
│   │   ├── useSpotify.tsx     # Spotify integration hook
│   │   └── useGraph.tsx       # Graph data hook
│   │
│   ├── services/              # API and external services
│   │   ├── api.ts             # Main API client
│   │   ├── auth.ts            # Authentication service
│   │   ├── spotify.ts         # Spotify service
│   │   └── graph.ts           # Graph service
│   │
│   ├── store/                 # State management (Zustand/Redux)
│   │   ├── authStore.ts       # Authentication state
│   │   ├── musicStore.ts      # Music data state
│   │   ├── graphStore.ts      # Graph state
│   │   └── uiStore.ts         # UI state
│   │
│   ├── types/                 # TypeScript type definitions
│   │   ├── auth.ts            # Authentication types
│   │   ├── music.ts           # Music entity types
│   │   ├── graph.ts           # Graph types
│   │   └── api.ts             # API response types
│   │
│   ├── utils/                 # Utility functions
│   │   ├── constants.ts       # App constants
│   │   ├── helpers.ts         # Helper functions
│   │   ├── formatters.ts      # Data formatters
│   │   └── validators.ts      # Validation functions
│   │
│   └── styles/                # Styling
│       ├── globals.css        # Global styles
│       ├── components.css     # Component styles
│       └── tailwind.config.js # Tailwind configuration
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts            # Vite configuration
```

### Dipendenze Principali
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "typescript": "^5.2.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.3.0",
    "vis-network": "^9.1.6",
    "zustand": "^4.4.6",
    "axios": "^1.6.0",
    "react-query": "^3.39.0",
    "lucide-react": "^0.290.0"
  }
}
```

## Database Schema (Neo4j)

### Constraint e Indici
```cypher
// Constraint per unicità
CREATE CONSTRAINT user_spotify_id IF NOT EXISTS FOR (u:Utente) REQUIRE u.spotify_user_id IS UNIQUE;
CREATE CONSTRAINT artist_spotify_id IF NOT EXISTS FOR (a:Artista) REQUIRE a.spotify_id IS UNIQUE;
CREATE CONSTRAINT album_spotify_id IF NOT EXISTS FOR (al:Album) REQUIRE al.spotify_id IS UNIQUE;
CREATE CONSTRAINT track_spotify_id IF NOT EXISTS FOR (t:Brano) REQUIRE t.spotify_id IS UNIQUE;
CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Persona) REQUIRE p.nome IS UNIQUE;
CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genere) REQUIRE g.nome IS UNIQUE;
CREATE CONSTRAINT place_name IF NOT EXISTS FOR (l:Luogo) REQUIRE l.nome IS UNIQUE;

// Indici per performance
CREATE INDEX artist_name_idx IF NOT EXISTS FOR (a:Artista) ON (a.nome);
CREATE INDEX album_year_idx IF NOT EXISTS FOR (al:Album) ON (al.anno_pubblicazione);
CREATE INDEX track_title_idx IF NOT EXISTS FOR (t:Brano) ON (t.titolo);
CREATE INDEX person_birth_idx IF NOT EXISTS FOR (p:Persona) ON (p.nascita_data);
```

### Esempio Query Complesse

#### Raccomandazioni H-Index
```cypher
// Trova artisti con collaboratori in comune
MATCH (u:Utente {spotify_user_id: $user_id})-[:ASCOLTA]->(t:Brano)<-[:CONTIENE]-(al:Album)<-[:PUBBLICATO]-(a:Artista)
WITH u, collect(DISTINCT a) as ascolto_artisti
UNWIND ascolto_artisti as artista_ascoltato
MATCH (artista_ascoltato)<-[:È_MEMBRO_DI]-(p:Persona)-[:È_MEMBRO_DI]->(artista_suggerito:Artista)
WHERE NOT artista_suggerito IN ascolto_artisti
WITH artista_suggerito, count(DISTINCT p) as collaboratori_comuni
WHERE collaboratori_comuni >= 2
RETURN artista_suggerito, collaboratori_comuni
ORDER BY collaboratori_comuni DESC
LIMIT 10
```

#### Discovery Geografico
```cypher
// Trova artisti dalla stessa area geografica
MATCH (u:Utente {spotify_user_id: $user_id})-[:ASCOLTA]->(t:Brano)<-[:CONTIENE]-(al:Album)<-[:PUBBLICATO]-(a:Artista)
WITH u, collect(DISTINCT a) as ascolto_artisti
UNWIND ascolto_artisti as artista_ascoltato
MATCH (artista_ascoltato)<-[:È_MEMBRO_DI]-(p:Persona)-[:NATO_A]->(l:Luogo)<-[:NATO_A]-(p2:Persona)-[:È_MEMBRO_DI]->(artista_suggerito:Artista)
WHERE NOT artista_suggerito IN ascolto_artisti
WITH artista_suggerito, l, count(DISTINCT p2) as membri_stessa_area
RETURN artista_suggerito, l.nome as luogo, membri_stessa_area
ORDER BY membri_stessa_area DESC
LIMIT 10
```

## Configurazione Environment

### Backend (.env)
```env
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Spotify API
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
SPOTIFY_REDIRECT_URI=http://localhost:3000/callback

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External APIs
WIKIPEDIA_USER_AGENT=MusicAtlas/1.0 (your-email@example.com)
MUSICBRAINZ_USER_AGENT=MusicAtlas/1.0 (your-email@example.com)
SETLISTFM_API_KEY=your-setlistfm-key
TMDB_API_KEY=your-tmdb-key
BANDSINTOWN_API_KEY=your-bandsintown-key

# Redis Cache
REDIS_URL=redis://localhost:6379

# Development
DEBUG=true
ENVIRONMENT=development
```

### Frontend (.env)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_SPOTIFY_CLIENT_ID=your-client-id
REACT_APP_ENVIRONMENT=development
```

## Deployment Configuration

### Docker Compose per Development
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=${NEO4J_URI}
      - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
    depends_on:
      - redis
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

Questa architettura fornisce una base solida e scalabile per l'implementazione di Music Atlas, mantenendo la separazione delle responsabilità e facilitando la manutenzione e l'estensione del sistema.

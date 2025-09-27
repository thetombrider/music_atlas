# 🎯 Music Atlas - Backend Only Test

## Obiettivo
Testare in locale solo il backend per:
1. ✅ Login Spotify 
2. ✅ Import top artists e tracks
3. ✅ Creazione knowledge graph su Neo4j

## Come testare

### 1. Avvia server
```bash
cd /Users/tommy/Progetti\ Python/music_atlas
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test endpoints

**Health check:**
```
GET http://localhost:8000/health
```

**API docs:**
```
GET http://localhost:8000/docs
```

**Spotify login:**
```
GET http://localhost:8000/api/v1/auth/spotify/login
```

**Import user data (dopo login):**
```
POST http://localhost:8000/api/v1/music/import
```

### 3. Controlla Neo4j
- Neo4j Browser: https://09391438.databases.neo4j.io/browser/
- Query per vedere i dati: `MATCH (n) RETURN n LIMIT 25`

## Database
- ✅ Neo4j Aura già configurato nel .env
- ✅ Credenziali valide
- ✅ Connection testata

## Focus del test
- **NO frontend** - solo API pura
- **NO deployment** - solo locale
- **SÌ core features** - Spotify + Neo4j

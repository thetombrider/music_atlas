# 🔧 Railway Environment Variables - Configurazione Finale

## ✅ Variabili Corrette (già configurate)
```env
NEO4J_URI="neo4j+s://09391438.databases.neo4j.io"
NEO4J_USERNAME="neo4j" 
NEO4J_PASSWORD="8meA_X77OcafrF8TWG21IqJC_CWNHFSNi7BESwNMS08"
NEO4J_DATABASE="neo4j"
SPOTIFY_CLIENT_ID="dcf1a6ccbd884bf9869551ebb5fee918"
SPOTIFY_CLIENT_SECRET="dc4f3e0e685b46aebb75b1b3f22a76bf"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"
PORT="8000"
```

## ⚠️ DA AGGIORNARE SUBITO

### 1. SPOTIFY_REDIRECT_URI (CRITICO)
```env
# Cambia da:
SPOTIFY_REDIRECT_URI="https://music-atlas-1758921214.loca.lt/api/v1/auth/spotify/callback"

# A:
SPOTIFY_REDIRECT_URI="https://musicatlas-production.up.railway.app/api/v1/auth/spotify/callback"
```

### 2. JWT_SECRET_KEY (SICUREZZA)
```env
# Cambia da:
JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"

# A (genera una chiave sicura):
JWT_SECRET_KEY="MusicAtlas2025_SuperSecretKey_Railway_Production_XyZ789!"
```

## 🆕 VARIABILI DA AGGIUNGERE

```env
DEBUG="false"
ENVIRONMENT="production"
CORS_ORIGINS=["https://musicatlas-production.up.railway.app"]
LOG_LEVEL="INFO"
```

## 📋 AZIONI IMMEDIATE

### 1. Aggiorna Railway Variables
Nel tuo Railway Dashboard:
- Modifica `SPOTIFY_REDIRECT_URI`
- Modifica `JWT_SECRET_KEY` 
- Aggiungi le nuove variabili

### 2. Aggiorna Spotify App Dashboard
Vai su https://developer.spotify.com/dashboard:
- Trova la tua app
- Vai in "Settings"
- Aggiungi in "Redirect URIs": 
  `https://musicatlas-production.up.railway.app/api/v1/auth/spotify/callback`

### 3. Re-deploy
Dopo aver aggiornato le variabili, Railway farà il re-deploy automaticamente.

## ⚡ Variabili Finali Railway (Copy-Paste Ready)

```env
NEO4J_URI=neo4j+s://09391438.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=8meA_X77OcafrF8TWG21IqJC_CWNHFSNi7BESwNMS08
NEO4J_DATABASE=neo4j
SPOTIFY_CLIENT_ID=dcf1a6ccbd884bf9869551ebb5fee918
SPOTIFY_CLIENT_SECRET=dc4f3e0e685b46aebb75b1b3f22a76bf
SPOTIFY_REDIRECT_URI=https://musicatlas-production.up.railway.app/api/v1/auth/spotify/callback
JWT_SECRET_KEY=MusicAtlas2025_SuperSecretKey_Railway_Production_XyZ789!
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
PORT=8000
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=["https://musicatlas-production.up.railway.app"]
LOG_LEVEL=INFO
```

## 🚨 IMPORTANTE
Senza l'aggiornamento dell'`SPOTIFY_REDIRECT_URI`, l'autenticazione Spotify non funzionerà in produzione!

🔄 **Aggiorna subito queste variabili e poi testa il deploy!**

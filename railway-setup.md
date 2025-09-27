# Railway Deployment Setup

## Vantaggi di Railway:
- Un solo provider per frontend e backend
- Supporto nativo per databases (Neo4j incluso)
- Deploy automatico da Git
- Configurazione semplice
- Tier gratuito disponibile

## Struttura Consigliata:

### 1. Backend Service (FastAPI)
- Porta: 8000
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 2. Frontend Service (React)
- Build command: `cd frontend && npm install && npm run build`
- Start command: Servito staticamente o con nginx

### 3. Database Service
- Neo4j Aura (cloud) o Railway Neo4j addon

## File di configurazione necessari:

### railway.toml (root project)
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "always"

[env]
NODE_VERSION = "18"
PYTHON_VERSION = "3.11"
```

### Dockerfile alternativo (opzionale ma raccomandato)
Per avere più controllo sul build process.

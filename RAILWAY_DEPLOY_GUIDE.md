# 🚀 Guida Deployment Railway

## Step 1: Configurazione Servizio Railway

### Porta del Servizio
- **Porta**: `8000` 
- Railway mapperà automaticamente questa porta al suo load balancer

### Build Settings
- **Build Command**: Automatico (usa Dockerfile)
- **Start Command**: Automatico (definito nel Dockerfile)

## Step 2: Variabili d'Ambiente Necessarie

Vai in Railway Dashboard → Settings → Variables e aggiungi:

### Database (Neo4j)
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j  
NEO4J_PASSWORD=your_neo4j_password
```

### Spotify API
```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://your-app.railway.app/callback
```

### JWT Authentication
```env
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
```

### App Configuration
```env
DEBUG=false
CORS_ORIGINS=["https://your-app.railway.app"]
```

## Step 3: Database Setup Options

### Option A: Neo4j Aura (Raccomandato)
1. Vai su https://neo4j.com/aura
2. Crea un database gratuito
3. Usa le credenziali ottenute nelle env vars

### Option B: Railway Neo4j Plugin
1. Nel tuo progetto Railway
2. Vai su "Add Service" → "Database" → "Neo4j"
3. Le variabili saranno configurate automaticamente

## Step 4: Deploy Process

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Railway Auto-Deploy**:
   - Railway rileva il Dockerfile
   - Esegue il build multi-stage
   - Deploy automatico

## Step 5: Primo Deploy

### URL Generato
Railway genererà un URL tipo:
- `https://your-app-name-production.up.railway.app`

### Test Endpoints
- **API Health**: `https://your-app.railway.app/health`
- **API Docs**: `https://your-app.railway.app/docs` (se DEBUG=true)
- **Frontend**: `https://your-app.railway.app/`

## Step 6: Configurazione Post-Deploy

### Aggiorna Spotify Redirect URI
Nel tuo Spotify App Dashboard:
- **Redirect URI**: `https://your-app.railway.app/callback`

### Aggiorna CORS Origins
Nelle Railway env vars:
```env
CORS_ORIGINS=["https://your-actual-railway-url.up.railway.app"]
```

## ⚡ Quick Deploy Checklist

- [ ] Progetto pushato su GitHub
- [ ] Railway collegato al repo
- [ ] Porta configurata: 8000
- [ ] Variabili d'ambiente aggiunte
- [ ] Database Neo4j configurato
- [ ] Primo deploy completato
- [ ] Spotify redirect URI aggiornato
- [ ] Test API endpoints funzionanti

## 🔧 Troubleshooting

### Se il deploy fallisce:
1. Controlla i logs in Railway Dashboard
2. Verifica che tutte le env vars siano settate
3. Assicurati che il database sia raggiungibile

### Se l'app non risponde:
1. Controlla che la porta sia 8000
2. Verifica i logs del container
3. Testa l'endpoint `/health`

## 📝 Prossimi Passi Dopo il Deploy

1. **Test completo dell'applicazione**
2. **Setup monitoring e alerts**
3. **Configurazione custom domain** (opzionale)
4. **SSL certificate** (automatico su Railway)

🚀 **Pronto per il deploy!**

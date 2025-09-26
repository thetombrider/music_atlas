# Music Atlas

Un knowledge graph musicale che interconnette i tuoi dati di streaming Spotify con informazioni contestuali per scoperte musicali avanzate.

## Panoramica del Progetto

Music Atlas utilizza Neo4j per creare un grafo di conoscenza musicale che collega:
- I tuoi ascolti Spotify personali
- Informazioni su artisti, album e brani
- Dati biografici e geografici (Wikipedia/MusicBrainz)
- Eventi e concerti (Setlist.fm/Bandsintown)
- Connessioni con media (TMDb)

## Struttura del Progetto

```
music_atlas/
├── backend/                 # API FastAPI e logica business
├── frontend/               # Interfaccia React
├── docs/                   # Documentazione progetto
├── scripts/                # Script di utilità e setup
├── product.md              # Specifica di prodotto
├── implementation_plan.md   # Piano di implementazione
└── README.md              # Questo file
```

## Quick Start

### Prerequisiti
- Python 3.11+
- Node.js 18+
- Neo4j AuraDB account
- Spotify Developer account

### Setup Sviluppo

1. **Clone e setup**:
```bash
git clone <repository-url>
cd music_atlas
```

2. **Backend setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. **Frontend setup**:
```bash
cd frontend
npm install
```

4. **Environment variables**:
```bash
cp .env.example .env
# Configura le tue API keys
```

5. **Database setup**:
```bash
# Esegui script di inizializzazione Neo4j
python scripts/init_database.py
```

## Sviluppo

### Backend (FastAPI)
```bash
cd backend
uvicorn main:app --reload
```

### Frontend (React)
```bash
cd frontend
npm start
```

## Documentazione

- [Specifica di Prodotto](product.md) - Requisiti completi e architettura
- [Piano di Implementazione](implementation_plan.md) - Roadmap sviluppo
- [API Documentation](docs/api.md) - Documentazione API (TBD)
- [Database Schema](docs/database.md) - Schema Neo4j (TBD)

## Contribuire

Questo è un progetto in sviluppo. Per contribuire:

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## Licenza

TBD - Da definire in base ai requisiti del progetto.

## Roadmap

Vedi [Piano di Implementazione](implementation_plan.md) per la roadmap dettagliata.

### Milestone Principali
- [ ] **M1**: MVP con autenticazione Spotify
- [ ] **M2**: Knowledge graph completo
- [ ] **M3**: Sistema raccomandazioni
- [ ] **M4**: Interfaccia utente completa
- [ ] **M5**: Release produzione

## Contatti

Per domande o supporto, apri un issue su GitHub.

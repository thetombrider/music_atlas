# Product Requirements Document (PRD): Music Knowledge Graph & Recommendation Engine

---

## 1. Visione del Prodotto

Il **Music Knowledge Graph (MKG)** è una piattaforma che utilizza un database a grafo (Neo4j) per interconnettere i dati di streaming personali dell'utente (Spotify) con dati di contesto esterno (Wikipedia, Setlist.fm, TMDb).  

L'obiettivo è trasformare l'ascolto passivo in una scoperta attiva e contestuale, offrendo raccomandazioni e analisi delle affinità che i sistemi basati sul genere o sulla similarità non possono offrire.

### Obiettivi Chiave
- **Unicità**: Superare i sistemi di raccomandazione esistenti, sfruttando le connessioni nascoste (produttori comuni, luoghi di nascita, influenze storiche).
- **Scalabilità**: Utilizzare l'istruzione Cypher `MERGE` per garantire che il grafo cresca in modo efficiente con ogni nuovo utente e ogni nuova query.
- **Arricchimento On-Demand**: Mantenere il grafo "leggero" scaricando dati complessi (es. Wikipedia, crediti completi) solo quando un nuovo nodo Artista/Album viene introdotto da un Utente o tramite la funzione di ricerca.

---

## 2. Modello a Grafo (Core Entities)

Il grafo deve supportare i seguenti **nodi** (entità) e le **relazioni chiave** per garantire la massima interconnessione.

### 2.1. Nodi (Entità Principali)

| Etichetta | Descrizione | Proprietà Essenziali | Fonte Principale |
|-----------|-------------|-----------------------|------------------|
| **Utente** | L'utente che si connette con Spotify | `spotify_user_id` (Chiave), `nome_utente`, `ultima_sincronizzazione` | Spotify |
| **Artista** | Un gruppo o un progetto musicale (collettivo) | `spotify_id` (Chiave), `nome`, `generi_iniziali` (lista), `popolarità` | Spotify |
| **Persona** | Individuo (membro band, collaboratore, produttore) | `nome` (Chiave), `nascita_data`, `bio_breve`, `link_wikipedia` | Wikipedia/API |
| **Album** | Opera pubblicata (album, EP, compilation) | `spotify_id` (Chiave), `titolo`, `anno_pubblicazione` | Spotify |
| **Brano** | Traccia musicale specifica | `spotify_id` (Chiave), `titolo`, `durata_ms`, `bpm` (opzionale) | Spotify |
| **Genere** | Categoria musicale | `nome` (Chiave) | Spotify/Manuale |
| **Luogo** | Posizione geografica | `nome`, `tipo` (Città/Venue), `latitudine`, `longitudine` | API Geografiche |
| **Etichetta** | Etichetta discografica | `nome` (Chiave), `fondazione_anno`, `sede_legale` | Spotify/Discogs |
| **Evento** | Concerto, festival o tour | `data`, `nome`, `tipo` (Storico/Futuro), `link_biglietti` | Setlist.fm/Bandsintown |
| **Media** | Opere esterne (Film, Serie, Videogiochi) | `titolo`, `anno`, `tipo` | TMDb/IMDb |
| **Strumento** | Strumento musicale specifico | `nome` (Chiave), `tipo` | API esterne |

### 2.2. Relazioni (Edge Types)

| Tipo | Struttura (Da → A) | Proprietà Contestuali | Fonte |
|------|---------------------|-----------------------|-------|
| **ASCOLTA** | Utente → Brano | `conteggio`, `ultimo_ascolto` | Spotify |
| **PUBBLICATO** | Artista → Album | `ruolo` | Spotify |
| **PUBBLICATO_DA** | Album → Etichetta | - | Spotify/Discogs |
| **CONTIENE** | Album → Brano | `numero_traccia` | Spotify |
| **È_MEMBRO_DI** | Persona → Artista | `ruolo`, `dal_anno` | Wikipedia |
| **NATO_A** | Persona → Luogo | - | Wikipedia |
| **HA_SUONATO_SU** | Persona → Brano | `strumento`, `ruolo` (Ospite/Sessione) | Discogs |
| **DI_GENERE** | Artista → Genere | - | Spotify |
| **USA_STRUMENTO** | Persona → Strumento | - | API esterne |
| **HA_PARTECIPATO_A** | Artista → Evento | `tipo_partecipazione` | Setlist.fm |
| **USA_BRANO** | Media → Brano | `scena` | TMDb |

---

## 3. Requisiti Funzionali

### 3.1. Autenticazione e Ingestion Utente (Spotify)
- **RF1.1**: L'utente deve autenticarsi tramite OAuth di Spotify.  
- **RF1.2**: Il backend (FastAPI) deve eseguire il `MERGE` di un nodo **Utente** e avviare l’ingestion iniziale.  
- **RF1.3 (Seed)**: Recuperare i **Top Artists** e **Top Tracks** (recenti e storiche).  
- **RF1.4 (Logic Flow)**: Per ogni artista/brano recuperato, eseguire `MERGE` a cascata (**Brano → Album → Artista**).  
- **RF1.5 (Relazione Utente)**: Creare o aggiornare la relazione `(Utente)-[:ASCOLTA]-(Brano)` con `conteggio` e `ultimo_ascolto`.

### 3.2. Logica di Arricchimento On-Demand
- **RF2.1 (Arricchimento Base)**: Quando un **Artista** è creato, recuperare dati da Wikipedia/MusicBrainz (membri, luoghi di nascita).  
- **RF2.2 (Arricchimento Avanzato)**: Alla prima visualizzazione di **Album/Brano**, arricchire con crediti da Discogs.  
- **RF2.3 (Eventi)**: Alla visualizzazione di un **Artista**, interrogare Bandsintown e Setlist.fm per popolare eventi.  

### 3.3. Raccomandazioni e Discovery (Core Value)
- **RF3.1 (Discovery H-Index)**: Suggerire artisti **non ascoltati**, ma con almeno 2 collaboratori in comune.  
- **RF3.2 (Discovery Geografica)**: Suggerire artisti nati nello stesso luogo dei membri degli artisti preferiti.  
- **RF3.3 (Ricerca Contesto Media)**: Dato un **Film**, restituire i Brani utilizzati che l’utente ascolta o correlati tramite Genere.  

### 3.4. Interfaccia Utente (Frontend)
- **RF4.1 (Profilo Utente)**: Dashboard con Top Artists/Tracks e metriche di connessione (es. “5 città, 3 etichette”).  
- **RF4.2 (Pagina Artista)**: Sub-grafo dell’artista con membri, collaborazioni, etichette, eventi.  
- **RF4.3 (Ricerca Globale)**: Barra di ricerca che interroga prima il Knowledge Graph, altrimenti estende a Spotify/Wikipedia.  

---

## 4. Specifiche Tecniche

### 4.1. Stack Tecnologico
- **Database**: Neo4j (AuraDB)  
- **Backend & API**: Python 3.11+ con FastAPI  
- **Frontend & UI**: React (TS/JS) + Tailwind CSS  

### 4.2. Ruoli dei Componenti

| Componente | Ruolo | Dettagli Tecnici |
|------------|-------|------------------|
| **FastAPI Backend** | Motore di ingestion & query | Autenticazione Spotify, API esterne, logica Cypher. Usa **Neo4j Python Driver**. |
| **React Frontend** | Visualizzazione grafo & interazione | Stato app, chiamate API, libreria grafica (vis.js / Canvas). |
| **Neo4j (AuraDB)** | Knowledge Graph | Archivia entità e relazioni, ottimizzato con query Cypher (`MERGE`, `WITH`). |

### 4.3. API Esterne Richieste
- **Spotify Web API** → autenticazione, dati ascolto/popolarità  
- **Wikipedia / MusicBrainz** → biografie, crediti base  
- **Setlist.fm / Bandsintown** → dati concerti e tour  
- **TMDb (The Movie Database)** → entità Media  

---

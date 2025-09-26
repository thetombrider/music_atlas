#!/usr/bin/env python3
"""
Script di inizializzazione del database Neo4j per Music Atlas.
Crea i constraint, gli indici e i dati di seed necessari.
"""

import os
import sys
from neo4j import GraphDatabase
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configurazione
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://your-instance.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")  # Updated to match .env file
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

class DatabaseInitializer:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_constraints(self):
        """Crea i constraint per garantire l'unicità dei nodi principali."""
        constraints = [
            "CREATE CONSTRAINT user_spotify_id IF NOT EXISTS FOR (u:Utente) REQUIRE u.spotify_user_id IS UNIQUE",
            "CREATE CONSTRAINT artist_spotify_id IF NOT EXISTS FOR (a:Artista) REQUIRE a.spotify_id IS UNIQUE", 
            "CREATE CONSTRAINT album_spotify_id IF NOT EXISTS FOR (al:Album) REQUIRE al.spotify_id IS UNIQUE",
            "CREATE CONSTRAINT track_spotify_id IF NOT EXISTS FOR (t:Brano) REQUIRE t.spotify_id IS UNIQUE",
            "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Persona) REQUIRE p.nome IS UNIQUE",
            "CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genere) REQUIRE g.nome IS UNIQUE",
            "CREATE CONSTRAINT place_name IF NOT EXISTS FOR (l:Luogo) REQUIRE l.nome IS UNIQUE",
            "CREATE CONSTRAINT label_name IF NOT EXISTS FOR (e:Etichetta) REQUIRE e.nome IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✓ Constraint creato: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    print(f"✗ Errore creando constraint: {e}")
    
    def create_indexes(self):
        """Crea gli indici per migliorare le performance delle query."""
        indexes = [
            "CREATE INDEX artist_name_idx IF NOT EXISTS FOR (a:Artista) ON (a.nome)",
            "CREATE INDEX album_year_idx IF NOT EXISTS FOR (al:Album) ON (al.anno_pubblicazione)",
            "CREATE INDEX track_title_idx IF NOT EXISTS FOR (t:Brano) ON (t.titolo)",
            "CREATE INDEX person_birth_idx IF NOT EXISTS FOR (p:Persona) ON (p.nascita_data)",
            "CREATE INDEX user_last_sync_idx IF NOT EXISTS FOR (u:Utente) ON (u.ultima_sincronizzazione)",
            "CREATE INDEX event_date_idx IF NOT EXISTS FOR (e:Evento) ON (e.data)"
        ]
        
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                    print(f"✓ Indice creato: {index.split('FOR')[1].split('ON')[0].strip()}")
                except Exception as e:
                    print(f"✗ Errore creando indice: {e}")
    
    def create_seed_genres(self):
        """Crea i generi musicali di base nel database."""
        genres = [
            "Rock", "Pop", "Hip Hop", "Electronic", "Jazz", "Classical",
            "Country", "R&B", "Folk", "Reggae", "Blues", "Punk",
            "Metal", "Alternative", "Indie", "Soul", "Funk", "Dance",
            "Ambient", "Experimental", "World Music", "Latin"
        ]
        
        with self.driver.session() as session:
            for genre in genres:
                query = "MERGE (g:Genere {nome: $genre})"
                session.run(query, genre=genre)
            print(f"✓ Creati {len(genres)} generi musicali di base")
    
    def create_seed_instruments(self):
        """Crea gli strumenti musicali di base nel database."""
        instruments = [
            "Vocals", "Guitar", "Bass", "Drums", "Piano", "Keyboard",
            "Violin", "Saxophone", "Trumpet", "Flute", "Cello", "Synthesizer",
            "Harmonica", "Mandolin", "Banjo", "Accordion", "Clarinet", "Trombone"
        ]
        
        with self.driver.session() as session:
            for instrument in instruments:
                query = "MERGE (s:Strumento {nome: $instrument})"
                session.run(query, instrument=instrument)
            print(f"✓ Creati {len(instruments)} strumenti musicali di base")
    
    def verify_setup(self):
        """Verifica che il setup sia stato completato correttamente."""
        with self.driver.session() as session:
            # Conta i nodi per tipo
            counts = {}
            node_types = ["Utente", "Artista", "Album", "Brano", "Persona", "Genere", "Luogo", "Etichetta", "Strumento"]
            
            for node_type in node_types:
                result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                counts[node_type] = result.single()["count"]
            
            print("\n📊 Stato del database:")
            for node_type, count in counts.items():
                print(f"  {node_type}: {count} nodi")
            
            # Verifica constraint (compatibile con AuraDB)
            try:
                result = session.run("SHOW CONSTRAINTS")
                constraints = list(result)
                print(f"\n🔒 Constraint attivi: {len(constraints)}")
            except Exception:
                print(f"\n🔒 Constraint: Non disponibile (AuraDB)")
            
            # Verifica indici (compatibile con AuraDB)
            try:
                result = session.run("SHOW INDEXES")
                indexes = list(result)
                print(f"📈 Indici: {len(indexes)}")
            except Exception:
                print(f"📈 Indici: Non disponibile (AuraDB)")
    
    def clear_database(self):
        """ATTENZIONE: Cancella tutti i dati dal database. Usare solo in sviluppo!"""
        response = input("⚠️  ATTENZIONE: Questo cancellerà tutti i dati. Confermi? (yes/no): ")
        if response.lower() == "yes":
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                print("🗑️  Database svuotato completamente")
        else:
            print("❌ Operazione annullata")

def main():
    if not NEO4J_PASSWORD:
        print("❌ Errore: NEO4J_PASSWORD non configurata")
        print("Configura le variabili d'ambiente:")
        print("  export NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io")
        print("  export NEO4J_USERNAME=neo4j")
        print("  export NEO4J_PASSWORD=your-password")
        sys.exit(1)
    
    print("🚀 Inizializzazione database Music Atlas...")
    print(f"📡 Connessione a: {NEO4J_URI}")
    
    initializer = DatabaseInitializer(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Test connessione
        with initializer.driver.session() as session:
            session.run("RETURN 1")
        print("✅ Connessione al database stabilita")
        
        # Opzioni
        if len(sys.argv) > 1:
            if sys.argv[1] == "--clear":
                initializer.clear_database()
                return
            elif sys.argv[1] == "--verify":
                initializer.verify_setup()
                return
        
        # Setup completo
        print("\n1️⃣ Creazione constraint...")
        initializer.create_constraints()
        
        print("\n2️⃣ Creazione indici...")
        initializer.create_indexes()
        
        print("\n3️⃣ Creazione dati seed...")
        initializer.create_seed_genres()
        initializer.create_seed_instruments()
        
        print("\n4️⃣ Verifica setup...")
        initializer.verify_setup()
        
        print("\n🎉 Inizializzazione completata con successo!")
        print("\n💡 Comandi utili:")
        print("  python init_database.py --verify   # Verifica stato")
        print("  python init_database.py --clear    # Svuota database")
        
    except Exception as e:
        print(f"❌ Errore durante l'inizializzazione: {e}")
        sys.exit(1)
    finally:
        initializer.close()

if __name__ == "__main__":
    main()

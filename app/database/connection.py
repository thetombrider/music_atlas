from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jConnection:
    """Gestisce la connessione al database Neo4j"""
    
    def __init__(self):
        self.driver = None
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self.database = getattr(settings, 'NEO4J_DATABASE', 'neo4j')
    
    def connect(self):
        """Stabilisce la connessione al database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
                connection_acquisition_timeout=settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT
            )
            # Test connessione
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Chiude la connessione al database"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def get_session(self):
        """Ottiene una sessione del database"""
        if not self.driver:
            self.connect()
        return self.driver.session(database=self.database)
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Esegue una query e ritorna i risultati"""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Esegue una query di scrittura"""
        with self.get_session() as session:
            result = session.write_transaction(self._execute_query, query, parameters or {})
            return result
    
    @staticmethod
    def _execute_query(tx, query: str, parameters: Dict):
        """Metodo statico per eseguire query in una transazione"""
        result = tx.run(query, parameters)
        return [record.data() for record in result]

# Istanza globale della connessione
neo4j_db = Neo4jConnection()

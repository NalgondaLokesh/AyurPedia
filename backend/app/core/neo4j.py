"""
Neo4j client module for AyurPedia.
Handles knowledge graph operations with Neo4j database.
"""

import logging
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase
from .config import get_config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress verbose Neo4j notifications
logging.getLogger("neo4j.notifications").setLevel(logging.WARNING)


class Neo4jDB:
    """Neo4j graph database connection manager."""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None
        self.is_connected = False
        logger.info(f"Neo4jDB initialized with URI: {uri}")
    
    async def connect(self) -> bool:
        """Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            
            # Verify connection
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.debug(f"Successfully connected to Neo4j database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.is_connected = False
            return False
    
    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.is_connected = False
            logger.info("Neo4j connection closed")
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result dictionaries
        """
        if not self.is_connected or not self.driver:
            logger.error("Neo4j not connected")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                # NOTE: use dict(record) rather than record.data(); data() is
                # lossy - it drops node labels/element ids and rewrites
                # relationships into tuples.
                return [self._serialize_record(dict(record)) for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
        return []

    @staticmethod
    def _entity_id(entity: Any) -> str:
        """Return a stable identifier for a Neo4j entity.

        ``element_id`` is the supported identifier on driver 5.x/6.x; the
        legacy integer ``id`` is deprecated and only used as a fallback.
        """
        element_id = getattr(entity, "element_id", None)
        if element_id is not None:
            return str(element_id)
        return str(getattr(entity, "id", ""))

    def _serialize_record(self, value: Any) -> Any:
        """Convert Neo4j graph values into JSON-safe dictionaries."""
        if isinstance(value, Node):
            entity_id = self._entity_id(value)
            return {
                "id": entity_id,
                "element_id": entity_id,
                "labels": list(value.labels),
                **dict(value),
            }
        if isinstance(value, Relationship):
            entity_id = self._entity_id(value)
            return {
                "id": entity_id,
                "element_id": entity_id,
                "type": value.type,
                "start_node": self._serialize_record(value.start_node),
                "end_node": self._serialize_record(value.end_node),
                **dict(value),
            }
        if isinstance(value, Path):
            return {
                "nodes": self._serialize_record(value.nodes),
                "relationships": self._serialize_record(value.relationships),
            }
        if isinstance(value, dict):
            return {key: self._serialize_record(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._serialize_record(item) for item in value]
        return value
    
    def execute_write_query(self, query: str, parameters: Dict[str, Any] = None) -> bool:
        """Execute a write query (CREATE, UPDATE, DELETE).
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.driver:
            logger.error("Neo4j not connected")
            return False
        
        try:
            with self.driver.session() as session:
                session.run(query, parameters or {})
                return True
        except Exception as e:
            logger.error(f"Write query execution failed: {e}")
            return False
    
    def create_constraints(self, constraint_queries: List[str]) -> bool:
        """Create database constraints.
        
        Args:
            constraint_queries: List of Cypher constraint queries
            
        Returns:
            True if all constraints created successfully
        """
        if not self.is_connected:
            logger.error("Cannot create constraints: Neo4j not connected")
            return False
        
        success = True
        for query in constraint_queries:
            try:
                with self.driver.session() as session:
                    session.run(query)
                    logger.debug(f"Constraint created: {query[:50]}...")
            except Exception as e:
                logger.debug(f"Constraint creation failed (may already exist): {e}")
                # Continue even if constraint exists
        
        return success
    
    def create_indexes(self, index_queries: List[str]) -> bool:
        """Create database indexes.
        
        Args:
            index_queries: List of Cypher index queries
            
        Returns:
            True if all indexes created successfully
        """
        if not self.is_connected:
            logger.error("Cannot create indexes: Neo4j not connected")
            return False
        
        success = True
        for query in index_queries:
            try:
                with self.driver.session() as session:
                    session.run(query)
                    logger.debug(f"Index created: {query[:50]}...")
            except Exception as e:
                logger.debug(f"Index creation failed (may already exist): {e}")
                # Continue even if index exists
        
        return success
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics.
        
        Returns:
            Dictionary with node counts, relationship counts, etc.
        """
        stats = {}
        
        # Get node counts by label
        node_query = """
        MATCH (n)
        RETURN labels(n) as labels, count(n) as count
        """
        node_results = self.execute_query(node_query)
        stats['node_counts'] = {
            result['labels'][0] if result['labels'] else 'Unknown': result['count']
            for result in node_results
        }
        
        # Get relationship counts by type
        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(r) as count
        """
        rel_results = self.execute_query(rel_query)
        stats['relationship_counts'] = {
            result['type']: result['count'] for result in rel_results
        }
        
        # Total counts
        stats['total_nodes'] = sum(stats['node_counts'].values())
        stats['total_relationships'] = sum(stats['relationship_counts'].values())
        
        return stats
    
    def search_nodes(self, label: str, property_name: str, search_term: str, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """Search for nodes by property.
        
        Args:
            label: Node label (e.g., "Statute", "Section")
            property_name: Property to search (e.g., "name", "title")
            search_term: Search term (case-insensitive partial match)
            limit: Maximum results to return
            
        Returns:
            List of matching nodes with properties
        """
        query = f"""
        MATCH (n:{label})
        WHERE toLower(n.{property_name}) CONTAINS toLower($search_term)
        RETURN n
        LIMIT $limit
        """
        results = self.execute_query(query, {"search_term": search_term, "limit": limit})
        return [result['n'] for result in results]
    
    def get_node_relationships(self, node_id: Any, depth: int = 1) -> Dict[str, Any]:
        """Get relationships for a node.

        Args:
            node_id: Node element id or node ``name`` property
            depth: Traversal depth (1 = direct relationships only)

        Returns:
            Dictionary with node and its relationships
        """
        depth = max(1, min(depth, 3))
        query = f"""
        MATCH path = (n)-[*1..{depth}]-(related)
        WHERE elementId(n) = $identifier OR n.name = $identifier
        RETURN n, relationships(path) as relationships, related
        LIMIT 100
        """
        results = self.execute_query(query, {"identifier": str(node_id)})
        
        if not results:
            return {}
        
        relationships = []
        seen = set()
        for result in results:
            for relationship in result.get("relationships", []):
                relationship_id = relationship.get("id")
                if relationship_id not in seen:
                    seen.add(relationship_id)
                    relationships.append(relationship)

        return {
            "node": results[0]['n'],
            "relationships": relationships
        }


# Global Neo4j instance
_neo4j_db: Optional[Neo4jDB] = None


def get_neo4j() -> Neo4jDB:
    """Get or initialize global Neo4j instance."""
    global _neo4j_db
    if _neo4j_db is None:
        config = get_config()
        _neo4j_db = Neo4jDB(
            uri=config.neo4j_uri,
            user=config.neo4j_user,
            password=config.neo4j_password
        )
    return _neo4j_db

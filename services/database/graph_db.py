# Integration with graph databases (e.g., Neo4j)

from neo4j import GraphDatabase

class GraphDatabaseManager:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]
    
    def create_node(self, label, properties):
        query = f"CREATE (n:{label} $props) RETURN n"
        return self.execute_query(query, {"props": properties})

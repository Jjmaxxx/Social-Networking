from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))
    
    def close(self):
        self.driver.close()

    # example method
    def create_user(self, user_data):
        query = """
                CREATE (u:User {name: $name, username: $username, password: $password, email: $email})
                RETURN u
                """
        with self.driver.session() as session:
            result = session.run(query, user_data)
            return [record['u'] for record in result]
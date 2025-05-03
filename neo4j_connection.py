from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Neo4jConnection()
        return cls._instance
    

    def close(self):
        self.driver.close()

    def create_user(self, user_data):
        check_query = """
            MATCH (u:User)
            WHERE u.username = $username OR u.email = $email
            RETURN u
        """
        create_query = """
            CREATE (u:User {name: $name, username: $username, password: $password, email: $email})
            RETURN u
        """
        with self.driver.session() as session:
            # Check for existing user
            existing = session.run(check_query, {
                "username": user_data["username"],
                "email": user_data["email"]
            })
            if existing.peek():
                return None 

            result = session.run(create_query, user_data)
            return [record["u"] for record in result]
        
    def authenticate_user(self, username, password):
        query = """
        MATCH (u:User {username: $username, password: $password})
        RETURN u
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, password=password)
            record = result.single()
            return record["u"] if record else None

    def get_profile(self, username):
        query = """
        MATCH (u:User {username: $username})
        RETURN u.name AS name, u.email AS email, u.username AS username, u.bio AS bio
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return result.single()

    def update_profile(self, username, new_name, new_bio):
        query = """
        MATCH (u:User {username: $username})
        SET u.name = $new_name, u.bio = $new_bio
        RETURN u
        """
        with self.driver.session() as session:
            session.run(query, username=username, new_name=new_name, new_bio=new_bio)
    
    def search_users(self, search_term):
        query = """
        MATCH (u:User)
        WHERE u.username CONTAINS $search_term OR u.name CONTAINS $search_term
        RETURN u.username AS username, u.name AS name, u.bio AS bio, u.email AS email
        """
        with self.driver.session() as session:
            result = session.run(query, search_term=search_term)
            return set([record for record in result])

    def get_most_popular_users(self, limit=3):
        query = """
        MATCH (u:User)<-[:FOLLOWS]-(f:User)
        RETURN u.username AS username, COUNT(f) AS followers_count, u.name AS name, u.bio AS bio, u.email AS email
        ORDER BY followers_count DESC
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, limit=limit)
            return set([record for record in result])

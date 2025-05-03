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

    def follow_user(self, current_username, target_username):
        # Create a FOLLOWS relationship from the current user to the target user.
        query = """
        MATCH (u1:User {username: $current_username}), (u2:User {username: $target_username})
        WHERE NOT (u1)-[:FOLLOWS]->(u2) AND u1 <> u2
        CREATE (u1)-[:FOLLOWS]->(u2)
        RETURN u1, u2
        """
        with self.driver.session() as session:
            result = session.run(query, current_username=current_username, target_username=target_username)
            return result.single() is not None

    def unfollow_user(self, current_username, target_username):
        # Remove a FOLLOWS relationship from the current user to the target user.
        query = """
        MATCH (u1:User {username: $current_username})-[r:FOLLOWS]->(u2:User {username: $target_username})
        DELETE r
        RETURN u1, u2
        """
        with self.driver.session() as session:
            result = session.run(query, current_username=current_username, target_username=target_username)
            return result.single() is not None

    def get_following(self, username):
        # Get a list of users that the current user follows.
        query = """
        MATCH (u:User {username: $username})-[:FOLLOWS]->(followed)
        RETURN followed.username as username, followed.name as name
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return [record for record in result]

    def get_followers(self, username):
        # Get a list of users that follow the current user.
        query = """
        MATCH (follower)-[:FOLLOWS]->(u:User {username: $username})
        RETURN follower.username as username, follower.name as name
        """
        with self.driver.session() as session:
            result = session.run(query, username=username)
            return [record for record in result]

    def get_mutual_connections(self, username1, username2):
        # Get a list of users that both username1 and username2 follow.
        query = """
        MATCH (u1:User {username: $username1})-[:FOLLOWS]->(mutual)<-[:FOLLOWS]-(u2:User {username: $username2})
        RETURN mutual.username as username, mutual.name as name
        """
        with self.driver.session() as session:
            result = session.run(query, username1=username1, username2=username2)
            return [record for record in result]

    def get_friend_recommendations(self, username, limit=10):
        # Get friend recommendations based on common connections.
        query = """
        MATCH (u:User {username: $username})-[:FOLLOWS]->()-[:FOLLOWS]->(recommendation)
        WHERE NOT (u)-[:FOLLOWS]->(recommendation) AND u.username <> recommendation.username
        RETURN recommendation.username as username, recommendation.name as name, 
               count(*) as common_connections
        ORDER BY common_connections DESC
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, limit=limit)
            return [record for record in result]

from neo4j_connection import Neo4jConnection

conn = Neo4jConnection()

conn.create_user({"name": "Arden", "username": "arden", "password": "password", "email": "arden@gmail.com"})
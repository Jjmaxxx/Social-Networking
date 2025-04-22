from neo4j import GraphDatabase
import csv
import random
from datetime import datetime

NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

def populate_database(data_csv, follows_csv):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))
    with driver.session() as session:
        # create User nodes
        with open(data_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                userId = int(row['UserID'])
                dob = datetime.strptime(row['DOB'], "%Y-%m-%d").date()
                session.run(
                    """
                    CREATE (:User {userId: $userId, name: $name, username: $username, password: $password, email: $email, bio: $bio, dob: $dob, city: $city, country: $country})
                    """,
                    userId=userId, name=row['Name'], username=row['Username'], password=row['Password'], email=row['Email'], bio=row['Bio'], dob=dob, city=row['City'], country=row['Country']
                )

        # create FOLLOW relationships
        with open(follows_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                session.run(
                    """
                    MATCH (u1:User {username: $follower}), (u2:User {username: $followed})
                    CREATE (u1)-[:FOLLOWS]->(u2)
                    """,
                    follower=row['Follower'], followed=row['Followed']
                )
    
    driver.close()

populate_database("processed_dataset.csv", "follows.csv")
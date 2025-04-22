# How to run

## Install dependencies

```bash
# Optional: Create a Virtual Environment
python -m venv venv
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

## Setting up a local Neo4j database

- Create a local Neo4j database
- Set the username to <code>neo4j</code> (default is neo4j)
- Set password to <code>password</code> for the database
- Start the database and make sure that it is running on <code>bolt://localhost:7687</code>

## Populating the database

Run populate_database.py which is found in the populate-database directory

```bash
cd populate-database
python populate_database.py
```

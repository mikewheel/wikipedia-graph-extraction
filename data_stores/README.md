# DS4300 Final Project: Data Stores

This package contains code that interfaces with the databases we leverage in this project.

# Contents

  - `neo4j/`: Interfaces with the Neo4J store maintaining the graph of artist-artist relationships 
  - `redis/`: Interfaces with the Redis cache managing the state of the crawl in the `search` module
  - `sqlite/`: Interfaces with the SQLite table containing the reverse index lookup for article titles

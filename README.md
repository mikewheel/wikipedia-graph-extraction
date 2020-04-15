# DS4300 Final Project
For *Large Scale Storage and Retrieval*, Prof. John Rachlin, Spring 2020

Written by Maxwell Cunha, Anirudh Kamath, Jay Sherman, Michael Wheeler

## To run
  - Install Redis and ensure that it is running as a service
  - Create a Python 3.8 Virtual Environment and activate it
  - Install dependencies: `pip install -r requirements.txt`
  - Ensure the `data/` directory has necessary assets (see the README there)
  - Ensure that the `PYTHONPATH` environment variable is correctly configured
  - Create a `neo4j.json` config file based on `neo4j_sample.json`
  - Create a `redis.json` config file based on `redis_sample.json`
  - Install and start Neo4J: `neo4j start`
  - Install and start Redis: `redis-server`
  - Run `python3 -m search`
  


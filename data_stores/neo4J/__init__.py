"""
Initialization of Neo4J interfaces and project-specific methods.
"""

from config import NEO4J_CONNECTION_PARAMETERS, SEED_LIST
from wikipedia.models import WikipediaArticle


def add_node(article: WikipediaArticle) -> None:
    raise NotImplementedError("TODO -- implement the ability to add a Wikipedia article as a node in Neo4J")


def add_edge(source_article: WikipediaArticle, dest_article: WikipediaArticle) -> None:
    raise NotImplementedError("TODO -- implement the ability to link to Wikipedia articles to each other in Neo4J")


if __name__ == "__main__":
    # TODO -- init connection to Neo4J using NEO4J_CONNECTION_PARAMETERS
    # TODO -- iterate over SEED_LIST: if not in data store, add_node
    add_node(WikipediaArticle())

"""
Initialization of Neo4J interfaces and project-specific methods.

Neomodel crash course: https://neomodel.readthedocs.io/en/latest/getting_started.html
"""

from __future__ import annotations
from config import NEO4J_CONNECTION_PARAMETERS as N4J_CONF
from wikipedia.models import WikipediaArticle
from neomodel import db, StructuredNode, JSONProperty, RelationshipTo, RelationshipFrom


class ArticleNode(StructuredNode):

    properties = None

    def __init__(self, properties = None, article = None):

        self.article = article
        print("p", properties)
        print("a", article)
        if properties is None:

            self.properties = vars(article).copy()
            # remove properties that don't need to be on graph
            del self.properties["index_key"]
            del self.properties["outgoing_links"]
        else:
            self.properties = properties

        self.links_to = RelationshipTo('ArticleNode', 'LINKS TO')
        self.linked_from = RelationshipFrom('ArticleNode', 'LINKED FROM')


    @staticmethod
    def connect() -> None:
        '''
        Connects to the Neo4J instance
        '''
        user, pw, host, bolt_port = [N4J_CONF[a] for a in ['user', 'pass', 'host', 'bolt_port']]
        connection_url = f'bolt://{user}:{pw}@{host}:{bolt_port}'
        db.set_connection(connection_url)

    @classmethod
    def clear(cls):
        cls.connect()
        db.cypher_query("MATCH (n) DETACH DELETE n;")

    @classmethod
    def add_node(cls, article: WikipediaArticle) -> ArticleNode:
        '''
        Adds a node to the Neo4J Database by creating a node and storing all its properties as JSON data

        :param article: the article to add
        :returns: the node to use so edges can be added
        '''
        print('here')
        cls.connect()
        node = cls(article= article)  # vars() converts a class to JSON data
        node.save()  # Pushes node to the db
        return node

    @classmethod
    def add_edge(cls, source_article: ArticleNode, dest_article: ArticleNode) -> None:
        '''
        Connects one node to another

        :param source_article: the article pointing to the destination
        :param dest_article: the destination article to be pointed to
        '''
        cls.connect()
        source_article.links_to.connect(dest_article)

    '''Performs same functionality as inherited class'''
    def category(cls):
        super().category(cls)


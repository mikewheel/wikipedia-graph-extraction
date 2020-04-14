"""
Initialization of Neo4J interfaces and project-specific methods.

Neomodel crash course: https://neomodel.readthedocs.io/en/latest/getting_started.html

Written by Anirudh Kamath
"""

from __future__ import annotations
from config import NEO4J_CONNECTION_PARAMETERS as N4J_CONF, NEO4J_ENCRYPTED, make_logger
from wikipedia.models import WikipediaArticle
from neomodel import db, StructuredNode, JSONProperty, RelationshipTo, RelationshipFrom, StringProperty
from neomodel import config as neomodel_config

neomodel_config.ENCRYPTED_CONNECTION = NEO4J_ENCRYPTED

logger = make_logger(__name__)


class ArticleNode(StructuredNode):

    properties = JSONProperty()
    article_id = StringProperty()
    article_title = StringProperty()
    links_to = RelationshipTo('ArticleNode', 'LINKS TO')
    linked_from = RelationshipFrom('ArticleNode', 'LINKED FROM')
    article = None

    def update_article(self, article: WikipediaArticle) -> None:
        """
        Sets the article field.

        :param article: the article to set the article field to.
        """
        self.article = article

    @staticmethod
    def connect() -> None:
        """"
        Connects to the Neo4J instance
        """
        user, pw, host, bolt_port = [N4J_CONF[a] for a in ['user', 'pass', 'host', 'bolt_port']]
        connection_url = f'bolt://{user}:{pw}@{host}:{bolt_port}'
        logger.debug(f'Connecting to Neo4J: {connection_url}')
        db.set_connection(connection_url)

    @classmethod
    def clear(cls):
        cls.connect()
        query_txt = "MATCH (n) DETACH DELETE n;"
        logger.debug(f'Executing clear: {query_txt}')
        db.cypher_query(query_txt)

    @classmethod
    def add_node(cls, article: WikipediaArticle) -> ArticleNode:
        '''
        Adds or gets a node to the Neo4J Database by creating a node and storing all its properties as JSON data

        :param article: the article to add
        :returns: the node to use so edges can be added
        '''

        cls.connect()
        properties = article.infobox
        article_id = article.article_url
        title = article.article_title

        # node = cls.nodes.get_or_none(article_id=article_id)
        results, meta = db.cypher_query("""MATCH (s) WHERE s.article_id = '""" + article_id + """' RETURN s""")
        nodes = [cls.inflate(row[0]) for row in results]

        if nodes:
            nodes[0].article = article
            return nodes[0]

        node = cls(article_id=article_id, article_title=title, properties=properties)  # vars() converts a class to JSON data
        node.save()  # Pushes node to the db
        node.article = article
        return node

    @classmethod
    def retrieve_node(cls, article: WikipediaArticle) -> ArticleNode:
        results, meta = db.cypher_query("""MATCH (s) WHERE s.article_id = '""" + article.article_url + """' RETURN s""")
        nodes = [cls.inflate(row[0]) for row in results]
        if nodes:
            return nodes[0]

    # @classmethod
    # def retrieve_edge(cls, source_article: ArticleNode, dest_article: ArticleNode):
    #     results, meta = db.cypher_query('MATCH (t:Track {spotify_id: "%s"})-[:`FEATURED IN`]->(p:Playlist) RETURN p'
    #                                     % spotify_id)
    #     return [Playlist.inflate(row[0]) for row in results]

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


"""
Initialization of Redis interfaces and project-specific methods.

Written by Max Cunha.
"""

from __future__ import annotations
from config import REDIS_CONNECTION_PARAMETERS
from redis import Redis
from wikipedia.models import WikipediaArticle


class ArticleCache:

    def __init__(self):
        self._conn = Redis(REDIS_CONNECTION_PARAMETERS['host'], REDIS_CONNECTION_PARAMETERS['port'])

    def clear(self) -> None:
        """
        Clear the database (called only upon search initialization).
        """
        self._conn.flushall()

    def store_classification(self, article: WikipediaArticle, is_musical_artist: bool) -> None:
        """
        Add a key-value pair in the Redis cache indicating whether the given article is a musical artist or not.
        Since all primitives in Redis are strings, this functionality converts the boolean to a binary integer
        encoding.  This reduces storage overhead vs "true" and "false".
        :param article: the WikipediaArticle to store classification for
        :param is_musical_artist: boolean classification indicating whether article is about a musical artist
        """
        is_musical_artist_int = 1 if is_musical_artist else 0  # convert to integer representation for Redis
        self._conn.set(name=article.article_title, value=is_musical_artist_int)
        pass

    def retrieve_classification(self, article: WikipediaArticle) -> bool:
        """
        Try to retrieve the classification of the given article from the cache: musical artist or not musical artist.
            - If the article is not in the cache, the returned value is None
            - If the article is in the cache, its stored classification is returned
        :param article: the title of the article to retrieve classification for
        :returns: the classification or None
        """
        classification = self._conn.get(article.article_title)
        if classification is not None:
            classification = bool(int(classification))  # convert from Redis string to boolean
        return classification

"""
Data types generated and exposed by the Wikipedia package.

For more information visit https://en.wikipedia.org/wiki/Wikipedia:About
"""
from __future__ import annotations
from typing import List


class WikipediaArticle:
    """
    Represents an article page on Wikipedia. See https://mwparserfromhell.readthedocs.io/en/latest/
    """
    
    def __init__(self, article_title=None, article_url=None, index_key=None):
        self.article_title = article_title
        self.article_url = article_url
        self.index_key = index_key
    
    def links(self) -> List[WikipediaArticle]:
        """
        Generates a list of the internal links to other articles contained in this article.
        :return: List
        """
        return []  # TODO -- write me

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

    def __init__(self, article_title=None, article_url=None, index_key=None, outgoing_links=None):
        self.article_title = article_title
        self.article_url = article_url
        self.index_key = index_key
        self.outgoing_links = outgoing_links
        self.infobox = None


    def __str__(self):
        return "".join(["title: ", self.article_title, "\n",
                        "infobox: ", (str(self.infobox) if self.infobox is not None else "None")])

    def links(self) -> List[WikipediaArticle]:
        return self.outgoing_links



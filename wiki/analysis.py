"""
Supporting functions for analyzing the content of raw Wikipedia article data.
"""
from typing import List


def extract_links(article_text: str) -> List[str]:
    """
    Generates a list of outgoing links to other Wikipedia articles from this article.
    :param article_text: MediaWiki markup as found in the Wikipedia multi-stream archive.
    :return: A list of other article titles.
    """
    pass  # TODO -- write me


def classify_article_as_artist(article_text: str) -> bool:
    """
    Determine based on a number of heuristics and MediaWiki features whether we are confident that an article
    concerns a musical artist.
    :param article_text: MediaWiki markup as found in the Wikipedia multi-stream archive.
    :return: True if article is about a musician, else False.
    """
    pass  # TODO -- write me


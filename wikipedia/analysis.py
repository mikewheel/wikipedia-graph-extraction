"""
Supporting functions for analyzing the content of raw Wikipedia article data.
"""

from wikipedia.models import WikipediaArticle


def classify_article_as_artist(article: WikipediaArticle) -> bool:
    """
    Determine based on a number of heuristics and MediaWiki features whether we are confident that an article
    concerns a musical artist.
    :param article: MediaWiki markup as found in the Wikipedia multi-stream archive.
    :return: True if article is about a musician, else False.
    """
    return "Infobox musical artist" in article.text or "==Discography==" in article.text


"""
Supporting functions for analyzing the content of raw Wikipedia article data.
"""


def classify_article_as_artist(article_text: str) -> bool:
    """
    Determine based on an article's text whether we are confident that an article
    concerns a musical artist.
    :param article_text: the text of the article to classified
    :return: True if article is about a musician, else False.
    """
    return "Infobox musical artist" in article_text or "==Discography==" in article_text


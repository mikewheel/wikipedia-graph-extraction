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
    
    def __init__(self, article_title=None, article_url=None, index_key=None, full_xml=None, text=None):
        self.article_title = article_title
        self.article_url = article_url
        self.index_key = index_key
        self.full_xml = full_xml
        self.text = text
        self.outgoing_links = None

    def __str__(self):
        return "".join(["title: ", self.article_title, "\n",
                        "text: ", (self.text if self.text is not None else "None")])
    
    def links(self) -> List[WikipediaArticle]:
        """
        Generates a list of the internal links to other articles contained in this article.

        First populates a list of all the outgoing links' titles, then constructs basic
        WikipediaArticle objects from it. Note that the WikipediaArticles in the result
        will store the article title and URL. The other features will need to be updated
        during  WikipediaArchiveSearcher.retrieve_article_xml later in the workflow.

        Note: For some outgoing links, the capitalization may be different
        than in the article titles. This should not be an issue for any artists, however,
        so there is not a fix to the capitalism inconsistencies.

        :return: List
        """
        if self.outgoing_links is not None:
            return self.outgoing_links

        #getting all content between double braces
        titles = self.text.split("[[")
        titles = [title.split("]]")[0] for title in titles]

        #if there is a "|" delimiter, name of title is the before the "|"
        titles = [title.split("|")[0] for title in titles if not "Category"]
        urls = ["/".join(["https://en.wikipedia.org/wiki",
                          "_".join(title.split(" "))])
                for title in titles]
        articles = zip(titles, urls)

        self.outgoing_links = [WikipediaArticle(article[0], article[1]) for article in articles]

        return self.outgoing_links

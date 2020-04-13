"""
Controller module for generation of Neo4J data store entries modeling graphical relationships between
members of the music industry on Wikipedia.
"""
from data_stores.redis import ArticleCache
from data_stores.neo4j import ArticleNode
from wikipedia.analysis import classify_article_as_artist
from wikipedia.reader import WikipediaArchiveSearcher
from wikipedia.models import WikipediaArticle
from config import WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE
from seed_list import SEED_LIST

if __name__ == "__main__":
    # Init searcher and seed queue
    wikipedia_searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE,
                                                  index_path=WIKIPEDIA_INDEX_FILE)

    ArticleNode.clear()
    for artist in [SEED_LIST[0]]:
        wikipedia_searcher.retrieve_article_xml(artist)
        ArticleNode.add_node(artist)

    search_queue = [SEED_LIST[0]]
    continue_search = True

    # Init cache
    cache = ArticleCache()

    #init counter, for termination purposes
    counter = len(search_queue)
    
    while not len(search_queue) == 0 and continue_search:
        current_article = search_queue.pop(0)
        links = current_article.outgoing_links

        if links is None:
            #Occurs when cache.retrieve_classification(current_article) gave true on a previous iteration,
            #but current_article has no links object because process_page has not been run on current_article.
            #This only occurs when current_article has the same title but is a different instance of WikipediaArticle
            #as a previously searched Wikipedia article.
            #TL;DR: This will only occur if we have seen this article before, so we don't need to process it.
            continue

        for l in links:
            print(l.article_title)

        for linked_article in links:
            # try to retrieve classification
            stored_classification = cache.retrieve_classification(linked_article)
            if stored_classification is not None:
                # avoid re-classifying articles w/ stored classifications
                link_is_musical_artist = stored_classification
            else:
                #Wikipedia article requires processing, which will update the cache of classifications
                wikipedia_searcher.retrieve_article_xml(linked_article)

                link_is_musical_artist = cache.retrieve_classification(linked_article)
                counter+=(1 if link_is_musical_artist else 0)

            # Add to data store if classification comes back true
            if link_is_musical_artist:
                ArticleNode.add_node(linked_article)
                ArticleNode.add_edge(current_article, linked_article)
                search_queue.append(linked_article)

        continue_search = counter < 20

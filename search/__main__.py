"""
Controller module for generation of Neo4J data store entries modeling graphical relationships between
members of the music industry on Wikipedia.
"""
from data_stores.neo4J import add_node, add_edge

from config import SEED_LIST, WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE
from data_stores.redis import ArticleCache
from wikipedia.analysis import classify_article_as_artist
from wikipedia.reader import WikipediaArchiveSearcher

if __name__ == "__main__":
    # Init searcher and seed queue
    wikipedia_searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE,
                                                  index_path=WIKIPEDIA_INDEX_FILE)

    for artist_title in SEED_LIST:
        add_node(artist_title)

    search_queue = SEED_LIST
    continue_search = True

    # Init cache
    cache = ArticleCache()
    
    while continue_search:
        current_article = search_queue.pop(0)
        links = current_article.links()
        
        for linked_article in links:
            # try to retrieve classification
            stored_classification = cache.retrieve_classification(linked_article)
            if stored_classification is not None:
                # avoid re-classifying articles w/ stored classifications
                link_is_musical_artist = stored_classification
            else:
                # Retrieve text of linked article and classify
                link_is_musical_artist = classify_article_as_artist(linked_article)
                # store classification in cache
                cache.store_classification(linked_article, link_is_musical_artist)
            # Add to data store if classification comes back true
            if link_is_musical_artist:
                add_node(linked_article)
                add_edge(current_article, linked_article)
                search_queue.append(linked_article)
            else:
                raise NotImplementedError("TODO -- set up the Redis cache for articles we've already scraped")
            
        continue_search = True  # TODO -- decide what conditions on which to terminate the search

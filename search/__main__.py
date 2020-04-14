"""
Controller module for generation of Neo4J data store entries modeling graphical relationships between
members of the music industry on Wikipedia.
"""
from config import WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE
from data_stores.neo4j.article_node import ArticleNode
from data_stores.redis.article_cache import ArticleCache
from search.seed_artists import SEED_LIST
from wikipedia.reader import WikipediaArchiveSearcher

if __name__ == "__main__":
    # Init searcher and seed queue
    wikipedia_searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE,
                                                  index_path=WIKIPEDIA_INDEX_FILE)
    ArticleNode.clear()
    search_queue = []

    for artist in SEED_LIST[30:32]:
        wikipedia_searcher.retrieve_article_xml(artist)
        ArticleNode.add_node(artist)
        search_queue.append(artist)

    # Init cache
    cache = ArticleCache()
    cache.clear()

    # init counter, for termination purposes
    counter = len(search_queue)

    continue_search = True
    while continue_search:
        current_article = search_queue.pop()
        links = current_article.outgoing_links

        if links is None:
            '''
            Occurs when cache.retrieve_classification(current_article) gave true on a previous iteration,
            but current_article has no links object because process_page has not been run on current_article.
            This only occurs when current_article has the same title but is a different instance of WikipediaArticle
            as a previously searched Wikipedia article.
            TL;DR: This will only occur if we have seen this article before, so we don't need to process it.
            '''
            continue_search = counter < 150 and len(search_queue) != 0
            continue

        for linked_article in links:
            # try to retrieve classification
            stored_classification = cache.retrieve_classification(linked_article)
            if stored_classification is not None:
                # avoid re-classifying articles w/ stored classifications
                link_is_musical_artist = stored_classification
            else:
                try:
                    wikipedia_searcher.retrieve_article_xml(linked_article)
                    link_is_musical_artist = cache.retrieve_classification(linked_article)
                except WikipediaArchiveSearcher.ArticleNotFoundError:
                    link_is_musical_artist = False

            counter += (1 if link_is_musical_artist else 0)

            # Add to data store if classification comes back true
            if link_is_musical_artist:
                node_is_new = stored_classification is None
                linked_article_node = ArticleNode.add_node(linked_article)  # gets existing or adds new if none exists
                # check if node has been seen before adding to search queue
                if node_is_new:
                    search_queue.append(linked_article)
                # add an edge between current article and its outgoing link
                # get node for current artist and add edge between it and linked article
                current_article_node = ArticleNode.retrieve_node(current_article)
                ArticleNode.add_edge(current_article_node, linked_article_node)

        continue_search = counter < 150 and len(search_queue) != 0




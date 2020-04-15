"""
Controller module for generation of Neo4J data store entries modeling graphical relationships between
members of the music industry on Wikipedia.
"""
from config import WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE, make_logger, COOL_ASCII_ART_HEADER, \
    LOG_UPDATE_SEARCH_EVERY
from datetime import datetime
from data_stores.neo_4j.article_node import ArticleNode
from data_stores.redis_.article_cache import ArticleCache
from search.seed_artists import SEED_LIST
from wikipedia.reader import WikipediaArchiveSearcher

logger = make_logger(__name__)

if __name__ == "__main__":
    logger.info(COOL_ASCII_ART_HEADER)
    logger.info(f'Run @ {datetime.now()}')
    logger.info("Initializing Wikipeda Archive searcher...")
    wikipedia_searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE,
                                                  index_path=WIKIPEDIA_INDEX_FILE)
    
    ArticleNode.clear()
    
    logger.info("Constructing the seed list...")
    search_queue = []

    for artist in SEED_LIST:
        wikipedia_searcher.retrieve_article_xml(artist)
        ArticleNode.add_node(artist)
        search_queue.append(artist)

    logger.info("Initializing search cache...")
    cache = ArticleCache()
    cache.clear()

    # Handle termination of search
    counter = len(search_queue)
    continue_search = True
    
    logger.info("Starting the breadth-first search of Wikipedia")
    while continue_search:
        try:
            if counter % LOG_UPDATE_SEARCH_EVERY == 0:
                logger.info(f'Search has reached {counter} nodes...')
            
            current_article = search_queue.pop(0)
            links = current_article.outgoing_links
            logger.info(f'\tCurrent article: {current_article.article_title}\n\tOutgoing links: {len(links)}')
    
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
                        
                # Add to data store if classification comes back true
                if link_is_musical_artist:
                    logger.info(f'Creating edge: {current_article.article_title} -> {linked_article}')
                    node_is_new = stored_classification is None
                    linked_article_node = ArticleNode.add_node(linked_article)  # gets existing or adds new if none exists
                    # check if node has been seen before adding to search queue
                    if node_is_new:
                        counter += 1
                        search_queue.append(linked_article)
                    # add an edge between current article and its outgoing link
                    # get node for current artist and add edge between it and linked article
                    current_article_node = ArticleNode.retrieve_node(current_article)
                    ArticleNode.add_edge(current_article_node, linked_article_node)
                    
            continue_search = counter < 500 and len(search_queue) != 0
        except KeyboardInterrupt as e:
            logger.info(f'Received keyboard interrupt — hard stop for search.')
            exit()




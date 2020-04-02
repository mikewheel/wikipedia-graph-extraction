"""
Controller module for generation of Neo4J data store entries modeling graphical relationships between
members of the music industry on Wikipedia.
"""

from neo4j import add_node, add_edge
from wiki.analysis import extract_links, classify_article_as_artist
from wiki.reader import WikipediaArchiveSearcher
from config import SEED_LIST, WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE

if __name__ == "__main__":
    # Init searcher and seed queue
    wikipedia_searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE,
                                                  index_path=WIKIPEDIA_INDEX_FILE)
    
    for artist_title in SEED_LIST:
        add_node(artist_title)
    
    search_queue = SEED_LIST
    continue_search = True
    
    while continue_search:
        current_article_title = search_queue.pop(0)
        article_text = wikipedia_searcher.retrieve_article_xml(current_article_title)
        links = extract_links(article_text)
        
        for link_title in links:
            
            link_in_cache = False  # TODO -- maintain cache of seen articles and their classifications
            
            if link_in_cache:
                link_is_musical_artist = None  # TODO -- get the classification from cache
            else:
                # Retrieve text of linked article and classify
                linked_article_text = wikipedia_searcher.retrieve_article_xml(link_title)
                link_is_musical_artist = classify_article_as_artist(linked_article_text)
            
            # Add to data store if classification comes back true
            if link_is_musical_artist:
                add_node(link_title)
                add_edge(current_article_title, link_title)
                search_queue.append(link_title)
            else:
                pass  # TODO -- consider adding a cache of articles we've already seen before
            
        continue_search = True  # TODO -- decide what conditions on which to terminate the search

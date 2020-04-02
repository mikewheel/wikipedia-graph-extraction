from data_stores.neo4j import ArticleNode
from config import NEO4J_CONNECTION_PARAMETERS
from wikipedia.models import WikipediaArticle

def main():
    # TODO -- init connection to Neo4J using NEO4J_CONNECTION_PARAMETERS
    # TODO -- iterate over SEED_LIST: if not in data store, add_node
    print("config", NEO4J_CONNECTION_PARAMETERS)
    src = WikipediaArticle(article_title="cool article 1", article_url="url 1", index_key="your mom")
    dest = WikipediaArticle(article_title="lame article", article_url="url 2", index_key="swag")
    src_node = ArticleNode.add_node(src)
    dest_node = ArticleNode.add_node(dest)
    ArticleNode.add_edge(src_node, dest_node)  
main()

from config import NEO4J_CONNECTION_PARAMETERS
from data_stores.neo4j import ArticleNode
from wikipedia.models import WikipediaArticle

if __name__ == "__main__":
    print("config", NEO4J_CONNECTION_PARAMETERS)
    src = WikipediaArticle(article_title="cool article 1", article_url="url 1", index_key="pura vida")
    dest = WikipediaArticle(article_title="lame article", article_url="url 2", index_key="swag")
    src_node = ArticleNode.add_node(src)
    dest_node = ArticleNode.add_node(dest)
    ArticleNode.add_edge(src_node, dest_node)

from data_stores.redis import ArticleCache
from wikipedia.models import WikipediaArticle

if __name__ == '__main__':

    music_article = WikipediaArticle(article_title="Kanye West", article_url="url 1", index_key="k1")
    not_music_article = WikipediaArticle(article_title="John Cena", article_url="url 2", index_key="k2")
    unstored_article = WikipediaArticle(article_title="Yeet", article_url="url 3", index_key="k3")

    cache = ArticleCache()

    # store
    cache.store_classification(music_article, True)
    cache.store_classification(not_music_article, False)

    # get classifications
    print(f'Classification for a music article: {cache.retrieve_classification(music_article)}')
    print(f'Classification for a non-music article: {cache.retrieve_classification(not_music_article)}')
    print(f'Classification for an article not in the cache: {cache.retrieve_classification(unstored_article)}')
    exit(0)
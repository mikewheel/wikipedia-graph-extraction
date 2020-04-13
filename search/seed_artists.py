"""
Seed list for initializing the graph traversal across Wikipedia.
"""
from typing import List
from wikipedia.models import WikipediaArticle
from pandas import read_csv
from config import INPUT_DATA_DIR

seed_titles = read_csv(INPUT_DATA_DIR / "seed_list.csv")
SEED_LIST: List[WikipediaArticle] = [
    WikipediaArticle(article_title= title,
                     article_url= "/".join(["https://en.wikipedia.org/wiki",
                                            "_".join(title.split(" "))]))
    for title in seed_titles["artist_title"]]

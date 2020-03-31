"""
Low-level interaction with Wikipedia's multi-stream bzip2 file.

Written by Michael Wheeler and Jay Sherman.
"""
import bz2
from config import WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE, OUTPUT_DATA_DIR
from os.path import exists
from os import PathLike
import sqlite3
import html.parser
import re



class WikipediaArchiveSearcher:
    """
    A utility for extracting and parsing articles from the multi-stream bzip2 archive of Wikipedia.
    For more information on how the file formats work see https://en.wikipedia.org/wiki/Wikipedia:Database_download
    """
    
    class ArticleNotFoundError(Exception):
        """Custom exception for when some article isn't found in the archive."""
        pass

    class MWParser(html.parser.HTMLParser):

        def __init__(self, id: str):
            super().__init__()
            self.true_id = id
            self.observed_id = None
            self.lines = []
            self.curr_tag_id = False
            self.final_lines = []

        def handle_starttag(self, tag, attrs):
            if not self.final_lines:
                line_components = []
                if tag  == "page":
                    self.observed_id = None
                    self.lines = []
                    self.curr_tag_id = False
                elif tag == "id":
                    self.curr_tag_id = True
                line_components.append("<")
                line_components.append(tag)
                for tup in attrs:
                    line_components.append(f' {tup[0]}=\"{tup[1]}\"')
                line_components.append(">")
                self.lines.append("".join(line_components))

        def handle_data(self, data):
            if not self.final_lines:
                self.lines.append(data)
                if self.curr_tag_id and self.observed_id is None:
                    self.observed_id = data

        def handle_endtag(self, tag):
            if not self.final_lines:
                line_components = ["</", tag, ">"]
                self.lines.append("".join(line_components))
                if tag == "id":
                    self.curr_tag_id = False
                print(tag, str(self.true_id), str(self.observed_id))
                if tag == "page" and str(self.true_id) == str(self.observed_id):
                    self.final_lines = self.lines.copy()
                print(self.final_lines)

        def feed(self, data):
            self.rawdata = data
            self.goahead(0)


    def __init__(self, multistream_path: PathLike, index_path: PathLike):
        assert exists(multistream_path), f'Multistream path does not exist on the file system: {multistream_path}'
        assert exists(index_path), f'Index path does not exist on the file system: {index_path}'
        
        self.multistream_path = multistream_path
        self.index_path = index_path
        #---
        #commented until index is built---
        # self.index = self.parse_index()
        self.index = None
        #---


        
    def parse_index(self):
        """
        Maps each known article title to its start index, end index, title, and unique ID for fast searching later.
        :return: connection to xml_indices database, which has table named articles that holds above info
        """
        conn = sqlite3.connect(OUTPUT_DATA_DIR / "xml_indices.db")
        return conn

    def retrieve_article_xml(self, title: str) -> str:
        """
        Pulls the XML content of a specific Wikipedia article from the archive.
        :param title: The title of the article in question.
        :return: The decompressed text of the <page> node matching the given title.
        """
        #---
        #commented until index is built---
        #cursor = self.index.cursor()
        #cursor.execute(f'SELECT * FROM articles WHERE title =={title}')
        #results = cursor.fetchall()
        #if len(results) == 0:
        #    raise self.ArticleNotFoundError(title)
        #elif len(results) > 1:
        #    print(f'Got {len(results)} results for title={title}, using first one')
        #start_index, page_id, title, end_index = results[0]
        start_index, page_id, title, end_index = 615, 14, "AfghanistanGeography", 632461
        #---

        xml_block = self.extract_indexed_range(start_index, end_index)
        parser = self.MWParser(id = page_id, )
        parser.feed(xml_block)
        page = "".join(parser.final_lines)
        return page




        # TODO -- try to search self.index for the title text
        # TODO -- except article not found -> raise self.ArticleNotFoundError(title)
        # TODO -- else get the start and end indices where the article is located in the archive, along with the ID
        # TODO -- call self.extract_indexed_range()
        # TODO -- then search the output for the page tag with the ID we care about
        # TODO -- return that specific page tag as a string

    def extract_indexed_range(self, start_index: int, end_index: int) -> str:
        """
        Decompress a small chunk of the Wikipedia multi-stream XML bz2 file.
        :param start_index: Starting point for reading compressed bytes of interest.
        :param end_index: Stopping point for reading compressed bytes of interest.
        :return: The decompressed text of the (partial) XML located between those bytes in the archive.
        """
        bz2_decom = bz2.BZ2Decompressor()
        with open(self.multistream_path, "rb") as wiki_file:
            wiki_file.read(start_index)  # Discard the preceding bytes
            bytes_of_interest = wiki_file.read(end_index - start_index)

        return bz2_decom.decompress(bytes_of_interest).decode()


if __name__ == "__main__":
    print("Wikipedia archive search demo...")
    
    searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE, index_path=WIKIPEDIA_INDEX_FILE)
    out = searcher.extract_indexed_range(start_index=615, end_index=632461)
    
    with open(OUTPUT_DATA_DIR / "some_articles.xml", "w", errors="ignore") as out_file:
        out_file.write(out)

    one_article = searcher.retrieve_article_xml("AfghanistanGeography")

    with open(OUTPUT_DATA_DIR / "one_article.xml", "w", errors="ignore") as out_file:
        out_file.write(one_article)
    #---
    #commented until index is built
    #searcher.index.close()
    #---
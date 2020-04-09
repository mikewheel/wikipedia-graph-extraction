"""
Low-level interaction with Wikipedia's multi-stream bzip2 file.

Written by Michael Wheeler and Jay Sherman.
"""
import bz2
from argparse import ArgumentParser
from config import WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE, OUTPUT_DATA_DIR
from os.path import exists
from os import PathLike
import sqlite3
from html.parser import HTMLParser

from wikipedia.models import WikipediaArticle


class WikipediaArchiveSearcher:
    """
    A utility for extracting and parsing articles from the multi-stream bzip2 archive of Wikipedia.
    For more information on how the file formats work see https://en.wikipedia.org/wiki/Wikipedia:Database_download
    """

    class ArticleNotFoundError(Exception):
        """Custom exception for when some article isn't found in the archive."""
        pass

    def __init__(self, multistream_path: PathLike, index_path: PathLike):
        assert exists(multistream_path), f'Multistream path does not exist on the file system: {multistream_path}'
        assert exists(index_path), f'Index path does not exist on the file system: {index_path}'

        self.multistream_path = multistream_path
        self.index_path = index_path
        self.indices = self.retrieve_indices()
        self.retrieved_pages = {}


    def retrieve_indices(self):
        """
        Maps each known article title to its start index, end index, title, and unique ID for fast searching later.
        :return: connection to xml_indices database, which has table named articles that holds above info
        """
        conn = sqlite3.connect(OUTPUT_DATA_DIR / "pages.db")
        return conn

    def retrieve_article_xml(self, article: WikipediaArticle) -> str:
        """
        Pulls the XML content of a specific Wikipedia article from the archive.
        :param title: The title of the article in question.
        :return: The decompressed text of the <page> node matching the given title.
        """
        cursor = self.indices.cursor()

        cursor.execute('SELECT * FROM pages WHERE title == ?', (article.article_title,))
        results = cursor.fetchall()
        print(f'Got index information: {results}')

        if len(results) == 0:
            raise self.ArticleNotFoundError(article.article_title)
        elif len(results) > 1:
            print(f'Got {len(results)} results for title={article.article_title}, using first one')
        start_index, page_id, title, end_index = results[0]

        print("Starting partial decompression")
        if start_index > 10000000000:
            raise ValueError("Index too large")
        xml_block = self.extract_indexed_range(start_index, end_index)
        print("Finished partial decompression")
        parser = MWParser(id=page_id, )
        parser.feed(xml_block)
        full_xml = "".join(parser.final_lines)

        article.index_key = (start_index, end_index)
        article.full_xml = full_xml
        article.text = parser.text
        self.retrieved_pages[title] = article

        return full_xml

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

class MWParser(HTMLParser):

    """A class for parsing the mediawiki XML.

    Designed to find and reconstruct the XML for a specific page out of a block of XML referring
    to many pages.
    """

    def __init__(self, id: str):
        """Build a MWParser.

        :param id: the id of the page that is desired

        The other fields are:

        observed_id: the id value of the page currently being observed
        lines: the lines of the page currently being parsed
        curr_tag_id: a boolean- does the data being parsed part of
                     an id tag?
        final_lines: the lines of the XML of the page that is desired
        """
        super().__init__()
        self.title = title
        self.true_id = id
        self.observed_id = None
        self.lines = []
        self.curr_tag_id = False
        self.final_lines = []
        self.text = None
        self.curr_tag_text = False


    def handle_starttag(self, tag: str, attrs: list):
        """Reads a start tag, and determines if we're reading a new page or checking an id.

        Does nothing if the desired page has already been found. Otherwise, builds a start tag
        that will be appended to the list of lines in the XML.
        If the tag is a page tag, empties the list of collected lines, as the previous page was not the
        desired page. If the tag is an id tag, updates self.curr_tag_id to True.

        :param tag: a String representing the name of the tag
        :param attrs: a list of attributes for the start tag (not used)
        """
        if not self.final_lines:
            line_components = []
            if tag == "page":
                self.observed_id = None
                self.lines = []
                self.curr_tag_id = False
                self.text = None
            elif tag == "id":
                self.curr_tag_id = True
            elif tag == "text":
                self.curr_tag_text = True
            line_components.append("<")
            line_components.append(tag)
            for tup in attrs:
                line_components.append(f' {tup[0]}=\"{tup[1]}\"')
            line_components.append(">")
            self.lines.append("".join(line_components))

    def handle_data(self, data: str):
        """Reads in the data between a start tag and an end tag.

        Does nothing if the desired page has already been found. Otherwise,
        adds the data to the list of lines of the page currently being parsed.
        If the data currently being read in is from the first id tag of the
        page, sets self.observed_id to the data. If the data currently being read
        in is from the longest text tag found so far, sets self.text to the data

        :param data: the data between a start and end tag
        """
        if not self.final_lines:
            self.lines.append(data)
            if self.curr_tag_id and self.observed_id is None:
                self.observed_id = data
            if self.text is None or len(self.text) < len(data):
                self.text = data

    def handle_endtag(self, tag: str):
        """
        Reads an end tag, and decides if we have found the correct page or not.

        Does nothing if the desired page has already been found. Otherwise, builds
        the XML endtag and adds it to the list of lines of the XML being parsed.
        If the tag being parsed is a page tag and the page currently being parsed
        has the correct id, sets self.final_lines to be the lines collected. If
        the tag being parsed is an id tag, updates self.curr_tag_id to relate
        that we are no longer observing id data

        :param tag: a String representing the name of the tag
        """
        if not self.final_lines:
            line_components = ["</", tag, ">"]
            self.lines.append("".join(line_components))
            self.curr_tag_id = False
            self.curr_tag_text = False
            if tag == "page" and str(self.observed_id) == str(self.true_id):
                self.final_lines = self.lines.copy()

    def feed(self, data):
        """Feeds the XML data into the MWParser.

        Defers to handle_starttag, handle_data, and handle_endtag for
        each line of XML, as appropriate

        :param data: a String of the XML
        """
        self.rawdata = data
        self.goahead(0)

    def error(self, message: str):
        """Handles errors the same way the base class does"""
        super().__init__(self, message)


if __name__ == "__main__":
    print("Wikipedia archive search demo...")
    parser = ArgumentParser()
    parser.add_argument("--title", type=str, nargs=1)
    args = parser.parse_args()
    title = args.title[0]

    searcher = WikipediaArchiveSearcher(multistream_path=WIKIPEDIA_ARCHIVE_FILE, index_path=WIKIPEDIA_INDEX_FILE)

    article = WikipediaArticle(article_title= title,
                               article_url= "/".join(["https://en.wikipedia.org/wiki",
                                                      "_".join(title.split(" "))]))
    one_article = searcher.retrieve_article_xml(article)

    article.links()

    with open(OUTPUT_DATA_DIR / "one_article.xml", "w", errors="ignore") as out_file:
        out_file.write(one_article)
    searcher.indices.close()

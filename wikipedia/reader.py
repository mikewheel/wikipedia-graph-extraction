"""
Low-level interaction with Wikipedia's multi-stream bzip2 file.

Written by Michael Wheeler and Jay Sherman.
"""
import bz2
import sqlite3
from argparse import ArgumentParser
from html.parser import HTMLParser
from os import PathLike
from os.path import exists

import mwparserfromhell

from config import OUTPUT_DATA_DIR, WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE, SQLITE_ARCHIVE_INDEX_FILE
from data_stores.redis_.article_cache import ArticleCache
from wikipedia.analysis import classify_article_as_artist
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
        :return: connection to xml_indices database, which has tablWritten by Anirudh Kamath.e named articles that holds above info
        """
        conn = sqlite3.connect(SQLITE_ARCHIVE_INDEX_FILE)
        return conn

    def retrieve_article_xml(self, article: WikipediaArticle) -> str:
        """
        Pulls the XML content of a specific Wikipedia article from the archive.
        :param title: The title of the article in question.
        :return: The decompressed text of the <page> node matching the given title.
        """
        cursor = self.indices.cursor()

        cursor.execute('SELECT * FROM articles WHERE title == ?', (article.article_title,))
        results = cursor.fetchall()
        # print(f'\nGot index information: {results}')

        if len(results) == 0:
            raise self.ArticleNotFoundError(article.article_title)
        sqlite_table_index, start_index, page_id, title, end_index = results[0]
        start_index = int(start_index)
        end_index = int(end_index)
        page_id = int(page_id)
        title = "".join(title.split("'"))

        xml_block = self.extract_indexed_range(start_index, end_index)
        parser = MWParser(id=page_id, )
        parser.feed(xml_block)

        article.index_key = (start_index, end_index)
        article.outgoing_links = [WikipediaArticle(article_title= title,
                                                   article_url= "/".join(["https://en.wikipedia.org/wiki",
                                                                          "_".join(title.split(" "))]))
                                  for title in set(parser.link_titles)]
        article.infobox = parser.parameters
        
        # Update the cache of classifications
        cache = ArticleCache()
        cache.store_classification(article, parser.classification)

        self.retrieved_pages[title] = article
        full_xml = "".join(parser.final_lines)
        return full_xml

    def extract_indexed_range(self, start_index: int, end_index: int, chunksize: int = 10000000) -> str:
        """
        Decompress a small chunk of the Wikipedia multi-stream XML bz2 file.
        :param start_index: Starting point for reading compressed bytes of interest.
        :param end_index: Stopping point for reading compressed bytes of interest.
        :param chunksize: number of bytes to read at a time until reaching start_index
        :return: The decompressed text of the (partial) XML located between those bytes in the archive.
        """
        bz2_decom = bz2.BZ2Decompressor()
        with open(self.multistream_path, "rb") as wiki_file:
            wiki_file.seek(start_index)
            bytes_of_interest = wiki_file.read(end_index - start_index)

        return bz2_decom.decompress(bytes_of_interest).decode()


class MWParser(HTMLParser):

    """A class for parsing the mediawiki XML.

    Designed to find and reconstruct the XML for a specific page out of a block of XML referring
    to many pages.
    """

    def __init__(self, id: str,
                 tracked_params: list = ["birth_name", "birth_date", "birth_place", "alias", "occupation",
                                         "years_active", "net_worth", "website", "origin", "background", "genre",
                                         "label", "instrument", "organization"]):
        """Build a MWParser.

        :param id: the id of the page that is desired
        :param tracked_params: the parameters in the wikipedia article to track

        The other fields are:

        observed_id: the id value of the page currently being observed
        lines: the lines of the page currently being parsed
        curr_tag_id: a boolean- does the data being parsed part of
                     an id tag?
        final_lines: the lines of the XML of the page that is desired
        """
        super().__init__()
        self.true_id = id
        self.observed_id = None
        self.lines = []
        self.curr_tag_id = False
        self.final_lines = []
        self.text = None
        self.curr_tag_text = False
        self.link_titles = None
        self.classification = None
        self.tracked_params = tracked_params
        self.parameters = None


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
                self.process_text()

    def process_text(self):
        """Performs all necessary options on the text of the page

        Gets the titles of the outgoing links, retrieves the infobox,
        classifies the article, and updates the cache of classifications
        """
        # Get classification
        is_musical_artist = classify_article_as_artist(self.text)
        self.classification = is_musical_artist

        if not is_musical_artist:
            self.link_titles = []
            self.parameters = {}
            return 0 #exit without populating other data

        #Get link titles
        #getting all content between double braces
        titles = self.text.split("[[")
        titles = [title.split("]]")[0] for title in titles]
        #if there is a "|" delimiter, name of title is the before the "|"
        titles = [title.split("|")[0] for title in titles if not "Category" in title and not "&" in title]
        self.link_titles = titles[1:]

        #Get infobox
        templates = mwparserfromhell.parse(self.text).filter_templates()
        templates = [t for t in templates if "Infobox" in t]
        all_params = []
        for template in templates:
            all_params += template.params
        all_params = [param for param in all_params
                      if ("=" in param
                          and param[0] != "="
                          and param[-1:] != 0)]
        parameters_dict = {}
        for seen_param in all_params:
            equals_index = seen_param.index("=")
            key = seen_param[0:equals_index]
            value = seen_param[equals_index + 1:len(seen_param)]
            for tracked_param in self.tracked_params:
                if tracked_param in key:
                    self.process_parameter(tracked_param, value, parameters_dict)
        self.parameters = parameters_dict
    
    def process_parameter(self, key: str, value: str, parameters_dict: dict):
        """Process the value based on what the key is, and update parameters_dict

        :param key: the type of information contained in value, and the key for parameters_dict
        :param value: the information stored in the parameter
        :param parameters_dict: a store of the information related in a wiki page's parameters
        """
        value = value.strip()

        if key == "birth_date":
            value = value.split("}}<ref")[0] if "ref" in value else value[2:len(value) - 2]
            date = [section for section in value.split("|")
                     if section.isdigit()]
            if len(date) == 3:
                parameters_dict[key] = "/".join([date[0], date[1], date[2]])
        elif key == "net_worth":
            value = value.split("<ref")[0]
            value = " ".join(value.split("&nbsp;"))
        elif key == "website":
            #get rid of {{URL| and }}
            value = value[6:len(value) - 2]
        elif key == "years_active":
            value = "-".join(value.split("\u2013"))
        elif key in ["birth_place", "origin"]:
            new_values = []
            value = value.split("<ref")[0]
            values = [val.strip() for val in value.split(",")]
            for entry in values:
                val = entry.strip()
                vals = val.split("|")
                vals = [(val[2:] if "[[" in val else val)
                        for val in vals]
                vals = [(val[:len(val) - 2] if "]]" in val else val)
                        for val in vals]
                new_values.append(", ".join(vals))
            value = ", ".join(list(set(new_values)))
        elif key == "background":
            value = " ".join(value.split("<!")[0].strip().split("_"))

        elif "flatlist" in value or "plainlist" in value or  "hlist" in value:
            values = value.split("\n") if "\n" in value else value.split(",")
            values = values[1:len(values)-1]
            values = [val[1:len(val)] for val in values]
            values = [val.strip() for val in values]
            new_values = []
            for val in values:
                if "[[" in val and "|" in val:
                    new_values.append(val.split("|")[0][2:])
                elif "[[" in val:
                    new_values.append(val[2:len(val)-2])
                else:
                    new_values.append(val)
            value = ", ".join(new_values)

        elif "[[" in value:
            values = value.split(", ")
            values = [val.split("|")[0] for val in values]
            values =  [(val[2:] if "[[" in val else val)
                       for val in values]
            values = [(val[:len(val) - 2] if "]]" in val else val)
                       for val in values]
            value = ", ".join(values)

        if key != "birth_date":
            parameters_dict[key] = value

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

    with open(OUTPUT_DATA_DIR / "one_article.xml", "w", errors="ignore") as out_file:
        out_file.write(one_article)
    searcher.indices.close()

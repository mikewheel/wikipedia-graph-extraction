"""
Low-level interaction with Wikipedia's multi-stream bzip2 file.

Written by Michael Wheeler and Jay Sherman.
"""
import bz2
from config import WIKIPEDIA_ARCHIVE_FILE, WIKIPEDIA_INDEX_FILE, OUTPUT_DATA_DIR
from os.path import exists
from os import PathLike


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
        # self.index = self.parse_index()
        
    def parse_index(self):
        """
        Maps each known article title to its start index, end index, and unique ID for fast searching later.
        :return: TODO -- decide how this should be stored (pandas DF, SQLite table, etc)
        """
        raise NotImplementedError("Write me!")
    
    def retrieve_article_xml(self, title: str) -> str:
        """
        Pulls the XML content of a specific Wikipedia article from the archive.
        :param title: The title of the article in question.
        :return: The decompressed text of the <page> node matching the given title.
        """
        raise NotImplementedError("Write me!")
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
    
    with open(OUTPUT_DATA_DIR / "some_articles.xml", "w") as out_file:
        out_file.write(out)

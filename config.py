from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_DATA_DIR = DATA_DIR / "input"
OUTPUT_DATA_DIR = DATA_DIR / "output"

WIKIPEDIA_ARCHIVE_FILE = INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream.xml.bz2"
WIKIPEDIA_INDEX_FILE = INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream-index.txt"

SEED_LIST = []  # TODO -- read in seed list from somewhere

NEO4J_CONNECTION_PARAMETERS = {}  # TODO -- include connection params

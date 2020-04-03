"""
Project-wide constants and settings.
"""

from pathlib import Path
from typing import Any, Dict, List

from wikipedia.models import WikipediaArticle

BASE_DIR: Path = Path(__file__).parent
DATA_DIR : Path = BASE_DIR / "data"
INPUT_DATA_DIR: Path = DATA_DIR / "input"
OUTPUT_DATA_DIR: Path = DATA_DIR / "output"

WIKIPEDIA_ARCHIVE_FILE: Path = INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream.xml.bz2"
WIKIPEDIA_INDEX_FILE: Path = INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream-index.txt"

SEED_LIST: List[WikipediaArticle] = []  # TODO -- read in seed list from somewhere

NEO4J_CONNECTION_PARAMETERS: Dict[Any] = {}  # TODO -- include connection params

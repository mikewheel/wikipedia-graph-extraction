"""
Project-wide constants and settings.
"""
from logging import getLogger, FileHandler, StreamHandler, Formatter, DEBUG, INFO
import json
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List
from sys import stdout

BASE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = BASE_DIR / "data"
INPUT_DATA_DIR: Path = DATA_DIR / "input"
OUTPUT_DATA_DIR: Path = DATA_DIR / "output"
SQLITE_ARCHIVE_INDEX_FILE: Path = OUTPUT_DATA_DIR / "wiki_archive_index.db"

WIKIPEDIA_ARCHIVE_FILE: Path = INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream.xml.bz2"
WIKIPEDIA_INDEX_FILE: Path = INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream-index.txt"

NEO4J_CONNECTION_PARAMETERS: Dict[str, Any] = json.load(open(BASE_DIR / 'neo4j.json', 'r'))
REDIS_CONNECTION_PARAMETERS: Dict[str, Any] = json.load(open(BASE_DIR / 'redis.json', 'r'))
NEO4J_ENCRYPTED = False  # https://github.com/neo4j-contrib/neomodel/issues/485

COOL_ASCII_ART_HEADER = dedent("""\n
 #     #                                                                     #     #
 #  #  # # #    # # #####  ###### #####  #   ##      ######  ####  #####     ##   ## #    #  ####  #  ####
 #  #  # # #   #  # #    # #      #    # #  #  #     #      #    # #    #    # # # # #    # #      # #    #
 #  #  # # ####   # #    # #####  #    # # #    #    #####  #    # #    #    #  #  # #    #  ####  # #
 #  #  # # #  #   # #####  #      #    # # ######    #      #    # #####     #     # #    #      # # #
 #  #  # # #   #  # #      #      #    # # #    #    #      #    # #   #     #     # #    # #    # # #    #
  ## ##  # #    # # #      ###### #####  # #    #    #       ####  #    #    #     #  ####   ####  #  ####
""")

LOG_UPDATE_SEARCH_EVERY = 10000


def make_logger(module_name):
    logger = getLogger(module_name)
    logger.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    
    file_handler = FileHandler(OUTPUT_DATA_DIR / "search.log", mode="w")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(DEBUG)
    
    stdout_handler = StreamHandler(stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(INFO)
    
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)
    return logger

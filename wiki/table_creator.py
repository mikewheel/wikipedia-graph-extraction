"""
Creates a table relating the multistream indices

Written by Michael Wheeler and Jay Sherman.
"""
from config import INPUT_DATA_DIR, OUTPUT_DATA_DIR
import sqlite3
from pathlib import Path
import pandas


def parse_colons(s):
    """
    Separates the values delimited by the first two colons
    :param s: A String to parse colons over
    :return: the three Strings separated by the first two colons
    """
    portions = s.split(":")
    return [portions[0], portions[1], s[len(portions[0]) + len(portions[1]) + 2:len(s)]]


if __name__ == "__main__":

    """#reading in data from index text file, turning into table with columns relating, in order:
    #byte location of xml tags in .bz2 file, id of page, title of page
    indices = pandas.read_csv(INPUT_DATA_DIR / "enwiki-20200201-pages-articles-multistream-index.txt",
                              delimiter = "|")
    print("done reading from csv")
    indices_values = indices["byte:id:title"]
    row_values = []
    byte_values = [] #just the byte location of xml tag, first column of row
    for i in range(len(indices_values)):
        if i % 10000 == 0:
            print(i)
        line = indices_values[i]
        row_value = parse_colons(line)
        byte_values.append(row_value[0])
        row_values.append(parse_colons(line))

    print("Done formatting data")
    
    articles = pandas.DataFrame(row_values, columns = ["first_byte", "page_id", "title"])

    #Creating a mapping from the byte location of the xml tag to the next byte value,
    #so that only a small range of the bz2 file needs to be decompressed
    byte_values = articles["first_byte"]
    byte_values = list(set(byte_values))
    byte_values.sort()
    byte_values.append(-1) #for articles at the last byte, will read to end of file
    byte_dict = {}
    for i in range(len(byte_values) - 1):
        byte_dict[byte_values[i]] = byte_values[i + 1]

    print("Byte mapping built")
    
    #Creating new row on dataframe to relate the end of partial decompression range
    last_bytes = [byte_dict[byte] for byte in articles["first_byte"]]
    articles["last_byte"] = last_bytes
    
    print("Byte ranges assigned")

    #not tracked on repo- just for debug purposes
    articles.to_csv(OUTPUT_DATA_DIR / "pages.csv")"""

    #remove
    articles = pandas.read_csv(OUTPUT_DATA_DIR / "articles.csv")
    articles = articles.loc[:, ~articles.columns.str.contains('^Unnamed')]
    print("done reading from csv")

    #creation of sqlite table
    conn = sqlite3.connect(OUTPUT_DATA_DIR / 'pages.db') #also not tracked on repo
    print("found connection")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS pages")
    articles.to_sql("pages", conn, index = False)
    print("read out to sql")
    cursor.execute("CREATE INDEX articles_id_idx ON pages (page_id)")
    cursor.execute("CREATE INDEX articles_title_idx ON pages (title)")
    conn.commit()
    conn.close()

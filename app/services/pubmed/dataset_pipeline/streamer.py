import gzip
from lxml import etree
import zlib

def stream_pubmed_gz(path):
    try:
        with gzip.open(path, "rb") as f:
            context = etree.iterparse(f, events=("end",), tag="PubmedArticle", recover=True)
            for event, elem in context:
                yield elem
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
    except (OSError, gzip.BadGzipFile, zlib.error) as e:
        print(f"Skipping corrupted file {path}: {e}")
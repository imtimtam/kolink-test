from time import sleep
from pubmed_services import parse_pubmed_xml_to_json, parse_date
import json
import requests
import xmltodict

PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_ENDPOINT = PUBMED_BASE_URL + "esearch.fcgi"
EFETCH_ENDPOINT = PUBMED_BASE_URL + "efetch.fcgi"
BATCH_SIZE = 10
MAX_ARTICLES = 10 # 0 for no limit

def pubmed_search_year(year: int):
    params = {
        "db": "pubmed",
        "term": f"{year}[DP]",
        "usehistory": "y",
        "retmax": 0,
    }

    r = requests.get(ESEARCH_ENDPOINT, params=params)
    r.raise_for_status()

    data = xmltodict.parse(r.text)["eSearchResult"]
    return {
        "webenv": data["WebEnv"],
        "query_key": data["QueryKey"],
        "count": data["Count"]
    }

def pubmed_fetch_batches(webenv: str, query_key: str, count: int):
    retstart = 0

    while retstart < count:
        params = {
            "db": "pubmed",
            "query_key": query_key,
            "WebEnv": webenv,
            "retstart": retstart,
            "retmax": BATCH_SIZE,
            "rettype": "xml",
            "retmode": "xml",
        }

        r = requests.get(EFETCH_ENDPOINT, params=params)
        r.raise_for_status()

        yield xmltodict.parse(r.text)
        retstart += BATCH_SIZE
        sleep(0.34)

def get_pubmed_year(year: int = 2025):
    search = pubmed_search_year(year)
    count = int(search["count"])

    for batch in pubmed_fetch_batches(search["webenv"], search["query_key"], count=count):
        yield batch

if __name__ == "__main__":
    batch_num = 1
    total_fetched = 0

    for batch in get_pubmed_year(2025):
        parsed_articles = parse_pubmed_xml_to_json(batch)

        if MAX_ARTICLES:
            if total_fetched + len(parsed_articles) > MAX_ARTICLES:
                parsed_articles = parsed_articles[: MAX_ARTICLES - total_fetched]

        print(f"Batch {batch_num}, {len(parsed_articles)} articles")
        print(json.dumps(parsed_articles[:5], indent=2))

        total_fetched += len(parsed_articles)
        batch_num += 1
        if MAX_ARTICLES and total_fetched >= MAX_ARTICLES:
            break

        

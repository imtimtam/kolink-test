from fastapi import FastAPI, HTTPException, requests
from typing import List

app = FastAPI()

PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_ENDPOINT = PUBMED_BASE_URL + "esearch.fcgi"
EFETCH_ENDPOINT = PUBMED_BASE_URL + "efetch.fcgi"

def get_author_pmids(author_name: str, max_results: int = 20):
    # Logic to retrieve PMIDs for a given author
    params = {
        "db": "pubmed",
        "term": author_name + "[Author]",
        "retmode": "json",
        "retmax": max_results
    }
    r = requests.get(ESEARCH_ENDPOINT, params=params)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])

def fetch_pubmed_metadata(pmids: list[str]):
    # Logic to fetch metadata for given PMIDs
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    r = requests.get(EFETCH_ENDPOINT, params=params)
    r.raise_for_status()
    return r.text  # In real implementation, parse XML and return structured data

@app.get("/pubmed/author/{author_name}")
def get_author_articles(author_name: str):
    pmids = get_author_pmids(author_name)
    xml_data = fetch_pubmed_metadata(pmids)
    # parse XML here into structured dicts
    return {"author": author_name, "pmids": pmids, "raw_xml": xml_data[:500]} 
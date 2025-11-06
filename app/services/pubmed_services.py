from fastapi import FastAPI, HTTPException
import xmltodict, json
import requests

app = FastAPI()

PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_ENDPOINT = PUBMED_BASE_URL + "esearch.fcgi"
EFETCH_ENDPOINT = PUBMED_BASE_URL + "efetch.fcgi"
ESUMMARY_ENDPOINT = PUBMED_BASE_URL + "esummary.fcgi"

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
    return xmltodict.parse(r.text)

def parse_pubmed_xml_to_json(xml_data: dict):
    articles = xml_data["PubmedArticleSet"]["PubmedArticle"]
    cleaned_articles = []

    for article in articles:
        citation = article["MedlineCitation"]
        pmid = citation["PMID"]["#text"]
        date_completed = citation.get("DateCompleted", {})

        article_data = citation["Article"]
        title = article_data.get("ArticleTitle", "")
        abstract_raw = article_data.get("Abstract", {}).get("AbstractText", "")
        if isinstance(abstract_raw, dict):
            abstract_text = abstract_raw.get("#text", "")
        else:
            abstract_text = abstract_raw

        authors = []
        author_list = article_data.get("AuthorList", {}).get("Author", [])
        if isinstance(author_list, dict):
            author_list = [author_list]
        for author in author_list:
            last_name = author.get("LastName", "")
            fore_name = author.get("ForeName", "")
            full_name = f"{fore_name} {last_name}".strip()

            aff_info = author.get("AffiliationInfo", [])
            if isinstance(aff_info, dict):
                aff_info = [aff_info]

            author_affiliations = []
            for aff in aff_info:
                aff_text = aff.get("Affiliation", "")
                if aff_text and "contributed equally" not in aff_text.lower():
                    author_affiliations.append(aff_text.strip())

            authors.append({
                "name": full_name,
                "affiliations": author_affiliations
            })

        journal_title = article_data.get("Journal", {}).get("Title", "")

        cleaned_articles.append({
            "pmid": pmid,
            "title": title,
            "journal": journal_title,
            "abstract": abstract_text,
            "authors": authors,
            "date_completed": parse_date(date_completed)
        })

    return cleaned_articles

def parse_date(date_dict: dict):
    if not date_dict: return
    year = date_dict.get("Year", "0000")
    month = date_dict.get("Month", "01").zfill(2)
    day = date_dict.get("Day", "01").zfill(2)
    return f"{year}-{month}-{day}"

if __name__ == "__main__":
    author_name = "Anthony Fauci"
    pmids = get_author_pmids(author_name)
    print(pmids)
from fastapi import FastAPI
from cache_services import cache_pubmed_entries
import xmltodict, json
import requests

app = FastAPI()

PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_ENDPOINT = PUBMED_BASE_URL + "esearch.fcgi"
EFETCH_ENDPOINT = PUBMED_BASE_URL + "efetch.fcgi"
ESUMMARY_ENDPOINT = PUBMED_BASE_URL + "esummary.fcgi"

def search(term: str, max_results: int = 5000, field_type: str = None):
    query = f"{term}[{field_type}]" if field_type else term
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    r = requests.get(ESEARCH_ENDPOINT, params=params)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])

def fetch_pubmed_metadata(pmids: list[str]):
    if not pmids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }
    r = requests.get(EFETCH_ENDPOINT, params=params)
    r.raise_for_status()
    return xmltodict.parse(r.text)

def parse_pubmed_xml_to_json(xml_data: dict):
    articles = xml_data.get("PubmedArticleSet", {}).get("PubmedArticle", [])
    if isinstance(articles, dict):
        articles = [articles]
    filtered = []

    for article in articles:
        citation = article.get("MedlineCitation", {})
        pmid = citation.get("PMID", {}).get("#text", "")
        if not pmid: continue
        pubmed_data = article.get("PubmedData", {})
        date_data = pubmed_data.get("History", {}).get("PubMedPubDate", {})
        if isinstance(date_data, dict):
            date_data = [date_data]
        date_published = None
        for date in date_data:
            if date.get("@PubStatus") == "pubmed":
                date_published = date
                break

        article_data = citation.get("Article", {})
        title = article_data.get("ArticleTitle", "")
        abstract_raw = article_data.get("Abstract", {}).get("AbstractText", "")
        if isinstance(abstract_raw, dict):
            abstract_text = abstract_raw.get("#text", "")
        elif isinstance(abstract_raw, list):
            abstract_text = " ".join(a.get("#text", "") if isinstance(a, dict) else str(a) for a in abstract_raw).strip()
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
        language = article_data.get("Language", "")

        pub_type_raw = article_data.get("PublicationTypeList", {}).get("PublicationType", [])
        if isinstance(pub_type_raw, dict):
            pub_types = [pub_type_raw.get("#text", "").strip()]
        elif isinstance(pub_type_raw, list):
            pub_types = [(p.get("#text", "") if isinstance(p, dict) else str(p)).strip() for p in pub_type_raw]
        else:
            pub_types = []
        pub_type = pub_types

        mesh_list = citation.get("MeshHeadingList", {}).get("MeshHeading", [])
        if isinstance(mesh_list, dict):
            mesh_list = [mesh_list]

        mesh_terms = []
        for mesh in mesh_list:
            descriptor = mesh.get("DescriptorName", {})
            if isinstance(descriptor, dict):
                term = descriptor.get("#text", "")
            else:
                term = str(descriptor)
            
            if term:
                mesh_terms.append(term)

        filtered.append({
            "pmid": pmid,
            "publication_type": pub_type,
            "title": title,
            "journal_title": journal_title,
            "authors": authors,
            "abstract": abstract_text,
            "mesh_terms": mesh_terms,
            "date_published": parse_date(date_published),
            "language": language,
        })

    return filtered

def parse_date(date_dict: dict):
    if not date_dict: return None
    year = date_dict.get("Year")
    if not year: return None
    
    month = date_dict.get("Month", "01").zfill(2)
    day = date_dict.get("Day", "01").zfill(2)
    return f"{year}-{month}-{day}"

if __name__ == "__main__":
    search_term = "Diabetes"
    pmids = search(search_term, 5)
    #pmids = search(search_term, 5, "Author")
    xml_data = fetch_pubmed_metadata(pmids)
    parsed_data = parse_pubmed_xml_to_json(xml_data)
    cache_pubmed_entries(parsed_data)
    print(json.dumps(parsed_data, indent=2))
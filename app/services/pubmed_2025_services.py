from time import sleep
import os
import json
import requests
import xmltodict

PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_ENDPOINT = PUBMED_BASE_URL + "esearch.fcgi"
EFETCH_ENDPOINT = PUBMED_BASE_URL + "efetch.fcgi"
BATCH_SIZE = 1000
MAX_ARTICLES = 0

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
        batch_size = min(BATCH_SIZE, count - retstart)
        params = {
            "db": "pubmed",
            "query_key": query_key,
            "WebEnv": webenv,
            "retstart": retstart,
            "retmax": batch_size,
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

def export_pubmed_year(year: int):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FOLDER = os.path.join(script_dir, "..", "exports")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    OUTPUT_FILE = f"pubmed_{year}.jsonl"
    full_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)

    count = int(pubmed_search_year(year)["count"])
    print(f"Total articles for {year}: {count}")

    batch_num = 1
    total_written = 0

    with open(full_path, "w", encoding="utf-8") as f:
        for batch in get_pubmed_year(year):
            parsed_articles = parse_pubmed_xml_to_json(batch)

            for article in parsed_articles:
                f.write(json.dumps(article) + "\n")

            total_written += len(parsed_articles)
            print(f"Wrote batch {batch_num}, {len(parsed_articles)} articles (total {total_written})")
            batch_num += 1

    print(f"Finished exporting PubMed articles for {year} to {OUTPUT_FILE}")

if __name__ == "__main__":
    export_pubmed_year(2025)

        
# if __name__ == "__main__":
#     batch_num = 1
#     total_fetched = 0

#     for batch in get_pubmed_year(2025):
#         parsed_articles = parse_pubmed_xml_to_json(batch)

#         if MAX_ARTICLES:
#             if total_fetched + len(parsed_articles) > MAX_ARTICLES:
#                 parsed_articles = parsed_articles[: MAX_ARTICLES - total_fetched]

#         print(f"Batch {batch_num}, {len(parsed_articles)} articles")
#         print(json.dumps(parsed_articles[:5], indent=2))

#         total_fetched += len(parsed_articles)
#         batch_num += 1
#         if MAX_ARTICLES and total_fetched >= MAX_ARTICLES:
#             break
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

def parse_pubmed_article(elem):   
    citation = elem.find("MedlineCitation")
    pubmed_data = elem.find("PubmedData")
    article_data = citation.find("Article") if citation is not None else None

    pmid_elem = citation.find("PMID") if citation is not None else None
    pmid = pmid_elem.text.strip() if (pmid_elem is not None and pmid_elem.text) else None
    if not pmid:
        return None
    
    date_published = None
    history = pubmed_data.find("History") if pubmed_data is not None else None
    if history is not None:
        for pub_date in history.findall("PubMedPubDate"):
            if pub_date.get("PubStatus") == "pubmed":
                year = pub_date.find("Year").text.strip() if pub_date.find("Year") is not None and pub_date.find("Year").text else None
                month = pub_date.find("Month").text.strip().zfill(2) if pub_date.find("Month") is not None and pub_date.find("Month").text else "01"
                day = pub_date.find("Day").text.strip().zfill(2) if pub_date.find("Day") is not None and pub_date.find("Day").text else "01"
                if year is not None:
                    date_published = f"{year}-{month}-{day}"
                else: date_published = None
                break

    title_elem = article_data.find("ArticleTitle") if article_data is not None else None
    title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else None

    abstract_text = None
    abstract_sect = article_data.find("Abstract") if article_data is not None else None
    if abstract_sect is not None:
        abstract_raw = abstract_sect.findall("AbstractText")
        if abstract_raw:
            parts = []
            for a in abstract_raw:
                if a.text:
                    parts.append(a.text.strip())
            abstract_text = " ".join(parts).strip() if parts else None

    authors = []
    author_list = article_data.find("AuthorList") if article_data is not None else None
    if author_list is not None:
        for author in author_list.findall("Author"):
            last_name_elem = author.find("LastName")
            fore_name_elem = author.find("ForeName")
            last_name = last_name_elem.text.strip() if (last_name_elem is not None and last_name_elem.text) else ""
            fore_name = fore_name_elem.text.strip() if (fore_name_elem is not None and fore_name_elem.text) else ""
            full_name = f"{fore_name} {last_name}".strip() or None

            aff_info = author.findall("AffiliationInfo")
            author_affiliations = []
            for aff in aff_info:
                aff_text_elem = aff.find("Affiliation")
                aff_text = aff_text_elem.text.strip() if (aff_text_elem is not None and aff_text_elem.text) else ""
                if aff_text and "contributed equally" not in aff_text.lower():
                    author_affiliations.append(aff_text)

            authors.append({
                "full_name": full_name,
                "affiliations": author_affiliations
            })

    journal_title = None
    language = None
    if article_data is not None:
        journal_elem = article_data.find("Journal")
        if journal_elem is not None:
            journal_title_elem = journal_elem.find("Title")
            journal_title = journal_title_elem.text.strip() if (journal_title_elem is not None and journal_title_elem.text) else None
        language_elem = article_data.find("Language")
        language = language_elem.text.strip() if (language_elem is not None and language_elem.text) else None

    pub_type = []
    if article_data is not None:
        pub_type_list = article_data.find("PublicationTypeList")
        if pub_type_list is not None:
            for p in pub_type_list.findall("PublicationType"):
                type_text = p.text.strip() if (p is not None and p.text) else None
                if type_text:
                    pub_type.append(type_text)

    mesh_terms = []
    mesh_list = citation.find("MeshHeadingList") if citation is not None else None
    if mesh_list is not None:
        for mesh in mesh_list.findall("MeshHeading"):
            descriptor_elem = mesh.find("DescriptorName")
            if descriptor_elem is not None and descriptor_elem.text:
                mesh_terms.append(descriptor_elem.text.strip())

    return {
        "pmid": pmid,
        "publication_types": pub_type,
        "title": title,
        "journal_title": journal_title,
        "authors": authors,
        "abstract": abstract_text,
        "mesh_terms": mesh_terms,
        "date_published": date_published,
        "language": language,
    }

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
            parsed_articles = parse_pubmed_article(batch)

            for article in parsed_articles:
                f.write(json.dumps(article) + "\n")

            total_written += len(parsed_articles)
            print(f"Wrote batch {batch_num}, {len(parsed_articles)} articles (total {total_written})")
            batch_num += 1

    print(f"Finished exporting PubMed articles for {year} to {OUTPUT_FILE}")

if __name__ == "__main__":
    export_pubmed_year(2025)
    
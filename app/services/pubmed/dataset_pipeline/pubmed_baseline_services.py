import os
import ftplib
import gzip
from dotenv import load_dotenv
from lxml import etree
import json
import zlib

load_dotenv()
FTP_HOST = "ftp.ncbi.nlm.nih.gov"
FTP_DIR = "/pubmed/updatefiles/"
LOCAL_DAILY_DIR = os.getenv("LOCAL_DAILY_DIR")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
os.makedirs(LOCAL_DAILY_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ftp = ftplib.FTP(FTP_HOST)
ftp.login()
ftp.cwd(FTP_DIR)

def download_gz_files():
    files = ftp.nlst()
    gz_files = [f for f in files if f.endswith(".gz")]
    print(f"Found {len(files)} files in {FTP_DIR} on {FTP_HOST}")

    for filename in gz_files:
        local_path = os.path.join(LOCAL_DAILY_DIR, filename)
        if os.path.exists(local_path):
            continue
        
        print(f"Downloading {filename}...")
        with open(local_path, "wb") as f:
            ftp.retrbinary(f"RETR {filename}", f.write)

    ftp.quit()
    print("All files downloaded.")

def download_target_gz_files(index: int):
    filename = f"pubmed25n{index:04d}.xml.gz"
    local_path = os.path.join(LOCAL_DAILY_DIR, filename)

    if os.path.exists(local_path):
        print(f"Already exists: {filename}")
        return local_path

    try:
        print(f"Connecting to FTP: {FTP_HOST}")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login()
        ftp.cwd(FTP_DIR)

        print(f"Downloading {filename}...")
        with open(local_path, "wb") as f:
            ftp.retrbinary(f"RETR {filename}", f.write)

        ftp.quit()
        print(f"Downloaded → {local_path}")
        return local_path

    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return None

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

def parse_export_pubmed(sample_limit=None, starting_index=1):
    for filename in sorted(os.listdir(LOCAL_DAILY_DIR)):
        if not filename.endswith(".gz"):
            continue

        try:
            idx = int(filename.replace("pubmed25n", "").replace(".xml.gz", ""))
        except ValueError:
            continue
        if idx < starting_index:
            continue
        local_path = os.path.join(LOCAL_DAILY_DIR, filename)
        print(f"Processing {filename}...")

        year_buffers = {}
        def load_existing(year, out_path):
            if os.path.exists(out_path):
                existing = {}
                with open(out_path, "r", encoding="utf-8") as fr:
                    for line in fr:
                        try:
                            row = json.loads(line)
                            existing[row["pmid"]] = row
                        except:
                            continue
                return existing
            return {}
        count = 0

        for elem in stream_pubmed_gz(local_path):
            article = parse_pubmed_article(elem)
            if article is None:
                continue

            year = article["date_published"][:4] if article["date_published"] else "UNKNOWN"
            year_dir = os.path.join(OUTPUT_DIR, year)
            os.makedirs(year_dir, exist_ok=True)
            output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))
            if year not in year_buffers:
                year_buffers[year] = load_existing(year, output_path)
            year_buffers[year][article["pmid"]] = article
            count += 1

            if sample_limit and count >= sample_limit:
                break
            if count % 1000 == 0:
                print(f"{count} articles processed in {filename}...")

        for year, pmid_map in year_buffers.items():
            year_dir = os.path.join(OUTPUT_DIR, year)
            output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))
            with open(output_path, "w", encoding="utf-8") as fw:
                for row in pmid_map.values():
                    json.dump(row, fw, ensure_ascii=False)
                    fw.write("\n")
        print(f"Finished {filename}, total articles processed: {count}")

def parse_export_pubmed_single_file(local_path, filename):
    year_buffers = {}

    def load_existing(year, out_path):
        if os.path.exists(out_path):
            existing = {}
            with open(out_path, "r", encoding="utf-8") as fr:
                for line in fr:
                    try:
                        row = json.loads(line)
                        existing[row["pmid"]] = row
                    except:
                        continue
            return existing
        return {}

    print(f"Processing {filename}...")
    count = 0

    for elem in stream_pubmed_gz(local_path):
        article = parse_pubmed_article(elem)
        if article is None:
            continue
        
        year = article["date_published"][:4] if article["date_published"] else "UNKNOWN"
        year_dir = os.path.join(OUTPUT_DIR, year)
        os.makedirs(year_dir, exist_ok=True)
        output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))
        if year not in year_buffers:
            year_buffers[year] = load_existing(year, output_path)
        year_buffers[year][article["pmid"]] = article
        count += 1

        if count % 1000 == 0:
            print(f"{count} articles processed...")

    for year, pmid_map in year_buffers.items():
        year_dir = os.path.join(OUTPUT_DIR, year)
        output_path = os.path.join(year_dir, filename.replace(".xml.gz", ".jsonl"))
        with open(output_path, "w", encoding="utf-8") as fw:
            for row in pmid_map.values():
                json.dump(row, fw, ensure_ascii=False)
                fw.write("\n")
    print(f"Finished {filename}, total articles processed: {count}")

if __name__ == "__main__":
    #download_gz_files()
    parse_export_pubmed(starting_index=1275)
